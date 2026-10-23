! Optional external-reference benchmark. Production iregi-rust remains Rust-only.
! Domain: ordinary unit-power N=2..4, rank<=3, real spatial shifts with zero
! origin and positive-real squared masses (nonpositive imaginary parts).
! This domain is IR finite. CHECK independently varies all pole parameters.
! Only public tensor calls, native conversion, and status checks are timed.
program collier_benchmark
  use iso_fortran_env, only: int64, output_unit
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use COLLIER
  implicit none
  character(8192) :: line
  character(32) :: command
  character(128) :: request_id
  integer :: ios, mode, n, rank, batch, warmup, repeats, iterations
  integer :: i, j, lane, repeat, iteration, count, r, nt, nx, ny, nz, pos
  integer :: err_flag, acc_flag, bad_poles
  integer(int64) :: start, finish, rate
  real(kind(1d0)) :: mu, pi, a, uv_error, norm
  real(kind(1d0)), allocatable :: shifts(:,:,:), times(:), tensor_error(:), pole_errors(:,:)
  complex(kind(1d0)), allocatable :: masses(:,:), result(:,:,:), mom(:,:), invariants(:)
  complex(kind(1d0)), allocatable :: tensor(:,:,:,:), tensor_uv(:,:,:,:)
  complex(kind(1d0)), allocatable :: baseline(:), baseline_uv(:)
  logical, allocatable :: stable(:)
  logical :: all_stable, check_poles
  complex(kind(1d0)) :: ipi2

  pi=acos(-1d0)
  a=0.577215664901532860606512090082402431d0+log(pi)
  ipi2=cmplx(0d0,pi*pi,kind(1d0))
  call system_clock(count_rate=rate)
  if (rate<=0) error stop 'Monotonic wall clock unavailable'
  write(output_unit,'(a)') 'READY COLLIER_BENCHMARK_V1'
  flush(output_unit)
  do
    read(*,'(a)',iostat=ios) line
    if (ios<0) exit
    if (ios/=0) error stop 'Cannot read request'
    if (len_trim(line)==0) cycle
    if (trim(line)=='QUIT') exit
    read(line,*,iostat=ios) command,request_id,mode,n,rank,mu,batch,warmup,repeats,iterations
    if (ios/=0.or.(trim(command)/='BENCH'.and.trim(command)/='CHECK')) error stop 'Invalid header'
    if (verify(trim(request_id),'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-.')/=0) &
      error stop 'Invalid request ID'
    if (n<2.or.n>4.or.rank<0.or.rank>3.or.mode<1.or.mode>3) error stop 'Unsupported topology'
    if (batch<1.or.batch>4096.or.warmup<0.or.repeats<1.or.iterations<1.or.mu<=0d0) &
      error stop 'Invalid run dimensions'
    if (.not.ieee_is_finite(mu).or..not.ieee_is_finite(mu*mu)) error stop 'Invalid scale'
    if (mu*mu<=0d0) error stop 'Squared scale underflow'
    count=(rank+1)*(rank+2)*(rank+3)*(rank+4)/24
    allocate(shifts(n,0:3,batch),masses(n,batch),result(0:count-1,4,batch),stable(batch),times(repeats))
    allocate(mom(0:3,n-1),invariants(n*(n-1)/2),tensor_error(0:rank))
    allocate(tensor(0:rank,0:rank,0:rank,0:rank),tensor_uv(0:rank,0:rank,0:rank,0:rank))
    allocate(baseline(0:count-1),baseline_uv(0:count-1),pole_errors(3,batch))
    do lane=1,batch
      do i=1,n
        read(*,*,iostat=ios) shifts(i,:,lane),masses(i,lane)
        if (ios/=0) error stop 'Invalid propagator row'
      end do
      if (any(shifts(1,:,lane)/=0d0)) error stop 'Only zero-origin routing is supported'
      if (any(shifts(:,0,lane)/=0d0)) error stop 'Only real spatial shifts are qualified'
      if (any(.not.ieee_is_finite(shifts(:,:,lane)))) error stop 'Nonfinite shift'
      if (any(.not.ieee_is_finite(real(masses(:,lane))))) error stop 'Nonfinite mass'
      if (any(.not.ieee_is_finite(aimag(masses(:,lane))))) error stop 'Nonfinite mass'
      if (any(real(masses(:,lane))<=0d0).or.any(aimag(masses(:,lane))>0d0)) &
        error stop 'Only squared masses with positive real part and nonpositive imaginary part are qualified'
    end do
    ! Init_cll enables local-only memoization, reset by each root tensor call.
    ! No global event cache is created. Both references reuse initialization.
    call Init_cll(n,rank,'',.false.)
    call SwitchOffFileOutput_cll
    call SetInfOutLev_cll(0)
    call SetErrOutLev_cll(0)
    call SwitchOffErrStop_cll
    call SetMode_cll(mode)
    call InitCacheSystem_cll(0,n)
    call SetReqAcc_cll(1d-12)
    call SetCritAcc_cll(1d-10)
    call SetMuUV2_cll(mu*mu)
    call SetMuIR2_cll(mu*mu)
    call SetDeltaUV_cll(0d0)
    call SetDeltaIR_cll(0d0,0d0)
    check_poles=trim(command)=='CHECK'
    all_stable=.true.
    stable=.true.
    bad_poles=0
    pole_errors=0d0
    if (check_poles) call verify_poles()
    do iteration=1,warmup
      call evaluate_batch()
    end do
    do repeat=1,repeats
      call system_clock(start)
      do iteration=1,iterations
        call evaluate_batch()
      end do
      call system_clock(finish)
      times(repeat)=real(finish-start,kind(1d0))*1d9/real(rate,kind(1d0))/iterations
    end do
    write(output_unit,'(a)',advance='no') 'RESULT {"id":"'//trim(request_id)//'","stable":'
    if (all_stable.and.bad_poles==0) then
      write(output_unit,'(a)',advance='no') 'true'
    else
      write(output_unit,'(a)',advance='no') 'false'
    end if
    write(output_unit,'(a,i0,a,i0,a)',advance='no') &
      ',"collier_mode":',mode,',"clock_ticks_per_second":',rate,',"total_ns":['
    do i=1,repeats
      if (i>1) write(output_unit,'(a)',advance='no') ','
      write(output_unit,'(es25.17e3)',advance='no') times(i)
    end do
    write(output_unit,'(a)',advance='no') '],"pole_check_errors":'
    if (check_poles) then
      write(output_unit,'(a)',advance='no') '['
      do lane=1,batch
        if (lane>1) write(output_unit,'(a)',advance='no') ','
        write(output_unit,'(a,es25.17e3,a,es25.17e3,a,es25.17e3,a)',advance='no') &
          '[',pole_errors(1,lane),',',pole_errors(2,lane),',',pole_errors(3,lane),']'
      end do
      write(output_unit,'(a)',advance='no') ']'
    else
      write(output_unit,'(a)',advance='no') 'null'
    end if
    write(output_unit,'(a)',advance='no') ',"lanes":['
    do lane=1,batch
      if (lane>1) write(output_unit,'(a)',advance='no') ','
      if (.not.stable(lane)) then
        write(output_unit,'(a)',advance='no') '{"status":"unstable","moments":null}'
        cycle
      end if
      write(output_unit,'(a)',advance='no') '{"status":"success","moments":['
      do i=0,count-1
        if (i>0) write(output_unit,'(a)',advance='no') ','
        write(output_unit,'(a)',advance='no') '['
        do j=1,4
          if (j>1) write(output_unit,'(a)',advance='no') ','
          write(output_unit,'(a,es25.17e3,a,es25.17e3,a)',advance='no') &
            '[',real(result(i,j,lane)),',',aimag(result(i,j,lane)),']'
        end do
        write(output_unit,'(a)',advance='no') ']'
      end do
      write(output_unit,'(a)',advance='no') ']}'
    end do
    write(output_unit,'(a)') ']}'
    flush(output_unit)
    deallocate(shifts,masses,result,stable,times,mom,invariants,tensor_error,tensor,tensor_uv)
    deallocate(baseline,baseline_uv,pole_errors)
  end do
contains
  real(kind(1d0)) function square(v)
    real(kind(1d0)), intent(in) :: v(0:3)
    square=v(0)*v(0)-v(1)*v(1)-v(2)*v(2)-v(3)*v(3)
  end function square

  logical function finite_complex(value)
    complex(kind(1d0)), intent(in) :: value
    finite_complex=ieee_is_finite(real(value)).and.ieee_is_finite(aimag(value))
  end function finite_complex

  subroutine prepare_lane(k)
    integer, intent(in) :: k
    integer :: t
    do t=1,n-1
      mom(:,t)=cmplx(shifts(t+1,:,k),0d0,kind(1d0))
    end do
    invariants(1)=cmplx(square(shifts(2,:,k)),0d0,kind(1d0))
    if (n>=3) then
      invariants(2)=cmplx(square(shifts(3,:,k)-shifts(2,:,k)),0d0,kind(1d0))
      invariants(3)=cmplx(square(shifts(3,:,k)),0d0,kind(1d0))
    end if
    if (n==4) then
      invariants(3)=cmplx(square(shifts(4,:,k)-shifts(3,:,k)),0d0,kind(1d0))
      invariants(4)=cmplx(square(shifts(4,:,k)),0d0,kind(1d0))
      invariants(5)=cmplx(square(shifts(3,:,k)),0d0,kind(1d0))
      invariants(6)=cmplx(square(shifts(4,:,k)-shifts(2,:,k)),0d0,kind(1d0))
    end if
    if (any(.not.ieee_is_finite(real(invariants))).or.any(.not.ieee_is_finite(aimag(invariants)))) &
      error stop 'Derived invariants overflowed'
  end subroutine prepare_lane

  subroutine tensor_call(k)
    integer, intent(in) :: k
    call InitEvent_cll
    select case(n)
    case(2)
      call Bten_cll(tensor,tensor_uv,mom,invariants,masses(:,k),rank,tensor_error)
    case(3)
      call Cten_cll(tensor,tensor_uv,mom,invariants,masses(:,k),rank,tensor_error)
    case(4)
      call Dten_cll(tensor,tensor_uv,mom,invariants,masses(:,k),rank,tensor_error)
    end select
    call GetErrFlag_cll(err_flag)
    call GetAccFlag_cll(acc_flag)
    stable(k)=stable(k).and.err_flag==0.and.acc_flag==0.and.all(ieee_is_finite(tensor_error))
    do r=0,rank
      do nt=r,0,-1
        do nx=r-nt,0,-1
          do ny=r-nt-nx,0,-1
            nz=r-nt-nx-ny
            stable(k)=stable(k).and.finite_complex(tensor(nt,nx,ny,nz)).and. &
                                  finite_complex(tensor_uv(nt,nx,ny,nz))
          end do
        end do
      end do
    end do
    all_stable=all_stable.and.stable(k)
  end subroutine tensor_call

  subroutine evaluate_batch()
    integer :: k
    do k=1,batch
      call prepare_lane(k)
      call tensor_call(k)
      pos=0
      do r=0,rank
        do nt=r,0,-1
          do nx=r-nt,0,-1
            do ny=r-nt-nx,0,-1
              nz=r-nt-nx-ny
              result(pos,1,k)=ipi2*tensor_uv(nt,nx,ny,nz)
              result(pos,2:3,k)=cmplx(0d0,0d0,kind(1d0))
              result(pos,4,k)=ipi2*(tensor(nt,nx,ny,nz)-a*tensor_uv(nt,nx,ny,nz))
              stable(k)=stable(k).and.all(ieee_is_finite(real(result(pos,:,k)))).and. &
                                    all(ieee_is_finite(aimag(result(pos,:,k))))
              pos=pos+1
            end do
          end do
        end do
      end do
      all_stable=all_stable.and.stable(k)
    end do
  end subroutine evaluate_batch

  subroutine verify_poles()
    integer :: k, variation
    do k=1,batch
      call prepare_lane(k)
      call tensor_call(k)
      pos=0
      do r=0,rank
        do nt=r,0,-1
          do nx=r-nt,0,-1
            do ny=r-nt-nx,0,-1
              nz=r-nt-nx-ny
              baseline(pos)=tensor(nt,nx,ny,nz)
              baseline_uv(pos)=tensor_uv(nt,nx,ny,nz)
              pos=pos+1
            end do
          end do
        end do
      end do
      do variation=1,3
        call SetDeltaUV_cll(0d0)
        call SetDeltaIR_cll(0d0,0d0)
        if (variation==1) call SetDeltaUV_cll(1d0)
        if (variation==2) call SetDeltaIR_cll(1d0,0d0)
        if (variation==3) call SetDeltaIR_cll(0d0,1d0)
        call tensor_call(k)
        pos=0
        do r=0,rank
          do nt=r,0,-1
            do nx=r-nt,0,-1
              do ny=r-nt-nx,0,-1
                nz=r-nt-nx-ny
                if (finite_complex(baseline(pos)).and.finite_complex(baseline_uv(pos)).and. &
                    finite_complex(tensor(nt,nx,ny,nz))) then
                  norm=1d0+abs(baseline(pos))+abs(baseline_uv(pos))
                  uv_error=abs(tensor(nt,nx,ny,nz)-baseline(pos))
                  if (variation==1) uv_error=abs(tensor(nt,nx,ny,nz)-baseline(pos)-baseline_uv(pos))
                  if (ieee_is_finite(norm).and.ieee_is_finite(uv_error)) then
                    pole_errors(variation,k)=max(pole_errors(variation,k),uv_error/norm)
                  else
                    pole_errors(variation,k)=huge(1d0)
                  end if
                else
                  pole_errors(variation,k)=huge(1d0)
                end if
                pos=pos+1
              end do
            end do
          end do
        end do
      end do
      if (any(pole_errors(:,k)>1d-12)) then
        bad_poles=bad_poles+1
        stable(k)=.false.
        all_stable=.false.
      end if
      call SetDeltaUV_cll(0d0)
      call SetDeltaIR_cll(0d0,0d0)
    end do
  end subroutine verify_poles
end program collier_benchmark
