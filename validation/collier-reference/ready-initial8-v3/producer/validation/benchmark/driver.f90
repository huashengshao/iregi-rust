! Validation-only benchmark. Timed regions contain no process transport or I/O.
program iregi_benchmark
  use iso_fortran_env, only: int64, output_unit
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use global
  use ti_reduce, only: tensor_integral_reduce
  use cti_reduce, only: comp_tensor_integral_reduce
  use avh_olo_forIREGI, only: olo_scale
  implicit none
  character(8192) :: line
  character(32) :: command
  character(128) :: request_id
  integer :: ios, mode, n, rank, batch, warmup, repeats, iterations
  integer :: i, j, k, lane, repeat, iteration, count
  integer(int64) :: start, finish, rate
  real(kind(1d0)) :: mu
  real(kind(1d0)), allocatable :: shifts(:,:,:), masses_real(:,:), times(:)
  complex(kind(1d0)), allocatable :: masses(:,:), result(:,:,:)
  logical, allocatable :: stable(:), complex_mass(:)
  logical :: all_stable

  nullify(ibp_save,pave_save,shiftpaveden_save,ibp_save2,pave_save2,shiftpaveden_save2)
  nullify(cibp_save,cpave_save,cshiftpaveden_save)
  nullify(xyzmatrices_save,rsmatrices_save,cxyzmatrices_save,crsmatrices_save)
  print_banner=.true.
  call olo_scale(1d0)
  call system_clock(count_rate=rate)
  if (rate<=0) error stop 'Monotonic wall clock unavailable'
  write(output_unit,'(a)') 'READY IREGI_BENCHMARK_V1'
  flush(output_unit)
  do
    read(*,'(a)',iostat=ios) line
    if (ios<0) exit
    if (ios/=0) error stop 'Cannot read request'
    if (len_trim(line)==0) cycle
    if (trim(line)=='QUIT') exit
    read(line,*,iostat=ios) command,request_id,mode,n,rank,mu,batch,warmup,repeats,iterations
    if (ios/=0.or.trim(command)/='BENCH') error stop 'Invalid BENCH header'
    if (verify(trim(request_id),'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-.')/=0) &
      error stop 'Invalid request ID'
    if (n<1.or.n>7.or.rank<0.or.rank>7.or.mode<0.or.mode>2) error stop 'Unsupported topology'
    if (batch<1.or.batch>4096.or.warmup<0.or.repeats<1.or.iterations<1.or.mu<=0d0) &
      error stop 'Invalid run dimensions'
    count=(rank+1)*(rank+2)*(rank+3)*(rank+4)/24
    allocate(shifts(n,0:3,batch),masses_real(n,batch),masses(n,batch))
    allocate(result(0:count-1,4,batch),stable(batch),complex_mass(batch),times(repeats))
    do lane=1,batch
      do i=1,n
        read(*,*,iostat=ios) shifts(i,:,lane),masses(i,lane)
        if (ios/=0) error stop 'Invalid propagator row'
      end do
      masses_real(:,lane)=real(masses(:,lane))
      complex_mass(lane)=any(aimag(masses(:,lane))/=0d0)
    end do
    call INITIREGI(.true.,2,1d-12)
    ONSHELL_IREGI=.false.
    ML5_CONVENTION=.true.
    MU_R_IREGI=mu
    all_stable=.true.
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
    if (all_stable) then
      write(output_unit,'(a)',advance='no') 'true'
    else
      write(output_unit,'(a)',advance='no') 'false'
    end if
    write(output_unit,'(a,i0,a)',advance='no') ',"clock_ticks_per_second":',rate,',"total_ns":['
    do i=1,repeats
      if (i>1) write(output_unit,'(a)',advance='no') ','
      write(output_unit,'(es25.17e3)',advance='no') times(i)
    end do
    write(output_unit,'(a)',advance='no') '],"lanes":['
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
    deallocate(shifts,masses_real,masses,result,stable,complex_mass,times)
  end do
contains
  subroutine evaluate_batch()
    do k=1,batch
      ! IREGI caches numerical recurrence values only within this sample.
      STABLE_IREGI=.true.
      nmass=0
      massref=0d0
      do j=1,n
        if (abs(masses_real(j,k))>1d-12) then
          nmass=nmass+1
          massref(nmass)=masses_real(j,k)
        end if
      end do
      if (complex_mass(k)) then
        call comp_tensor_integral_reduce(mode,n,rank,count,shifts(:,:,k),masses(:,k),mu, &
                                         result(:,:,k),stable(k),1)
      else
        call tensor_integral_reduce(mode,n,rank,count,shifts(:,:,k),masses_real(:,k),mu, &
                                    result(:,:,k),stable(k),1)
      end if
      stable(k)=stable(k).and.all(ieee_is_finite(real(result(:,:,k)))).and. &
                             all(ieee_is_finite(aimag(result(:,:,k))))
      all_stable=all_stable.and.stable(k)
      ! Cache disposal is part of both engines' cold-numerical-cache contract.
      call IREGI_FREE_PS
    end do
  end subroutine evaluate_batch
end program iregi_benchmark
