! Validation-only process adapter. Production Rust never links this program.
program iregi_reference
  use iso_fortran_env, only: output_unit, error_unit
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use global
  use ti_reduce, only: tensor_integral_reduce
  use cti_reduce, only: comp_tensor_integral_reduce
  use gti_reduce, only: general_ti_reduce
  use si_reduce, only: scalar_integral_reduce
  use csi_reduce, only: comp_scalar_integral_reduce
  use avh_olo_forIREGI, only: olo_scale
  implicit none
  character(8192) :: line
  character(32) :: command, api
  character(128) :: request_id
  integer :: ios, mode, n, rank, idim, snap, count, i, j
  integer :: powers(7)
  real(kind(1d0)) :: mu, threshold, shifts(7,0:3), masses_real(7), masses_imag(7)
  complex(kind(1d0)) :: masses(7), result(0:329,4)
  logical :: stable, complex_mass, mass_exists

  nullify(ibp_save,pave_save,shiftpaveden_save,ibp_save2,pave_save2,shiftpaveden_save2)
  nullify(cibp_save,cpave_save,cshiftpaveden_save)
  nullify(xyzmatrices_save,rsmatrices_save,cxyzmatrices_save,crsmatrices_save)
  print_banner=.true.
  call olo_scale(1d0)
  write(output_unit,'(a)') 'READY IREGI_REFERENCE_V1'
  flush(output_unit)
  do
    read(*,'(a)',iostat=ios) line
    if (ios < 0) exit
    if (ios /= 0) error stop 'Cannot read request'
    if (len_trim(line)==0) cycle
    if (line(1:1)=='#') cycle
    if (trim(line)=='QUIT') exit
    read(line,*,iostat=ios) command,request_id,api,mode,n,rank,idim,mu,snap,threshold
    if (ios /= 0.or.trim(command)/='EVAL') error stop 'Invalid EVAL header'
    if (verify(trim(request_id),'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-.')/=0) &
      error stop 'Request ID must be an ASCII identifier'
    if (n<1.or.n>7.or.rank<0.or.rank>7) error stop 'n/rank outside reference capacities'
    if (mode<0.or.mode>2.or.mu<=0d0.or.threshold<0d0) error stop 'Invalid options'
    if (mod(idim,2)/=0) error stop 'Dimension shift must be even'
    do i=1,n
      read(*,*,iostat=ios) shifts(i,0:3),masses_real(i),masses_imag(i),powers(i)
      if (ios/=0.or.powers(i)<1.or.powers(i)>10) error stop 'Invalid propagator row'
      masses(i)=cmplx(masses_real(i),masses_imag(i),kind(1d0))
    end do
    call INITIREGI(.true.,2,threshold)
    ONSHELL_IREGI=snap/=0
    ML5_CONVENTION=.true. ! Raw monomial moments, without multinomial weights.
    STABLE_IREGI=.true.
    MU_R_IREGI=mu
    nmass=0
    massref=0d0
    complex_mass=.false.
    do i=1,n
      ! Match IMLOOP's policy, including its signed relative denominator.
      if (abs(masses_imag(i))/max(abs(masses(i)),1d-2)>1d-15) complex_mass=.true.
      if (abs(masses_real(i))>threshold) then
        mass_exists=.false.
        do j=1,nmass
          if (abs(masses_real(i)-massref(j))/masses_real(i)<threshold) then
            mass_exists=.true.
            exit
          end if
        end do
        if (.not.mass_exists) then
          nmass=nmass+1
          massref(nmass)=masses_real(i)
        end if
      end if
    end do
    count=(rank+1)*(rank+2)*(rank+3)*(rank+4)/24
    result=cmplx(0d0,0d0,kind(1d0))
    select case(trim(api))
    case('tensor')
      if (any(powers(1:n)/=1).or.idim/=0) error stop 'tensor requires unit powers and idim=0'
      if (complex_mass) then
        call comp_tensor_integral_reduce(mode,n,rank,count,shifts(1:n,:),masses(1:n),mu, &
                                        result(0:count-1,:),stable,1)
      else
        call tensor_integral_reduce(mode,n,rank,count,shifts(1:n,:),masses_real(1:n),mu, &
                                    result(0:count-1,:),stable,1)
      end if
    case('general')
      if (complex_mass) error stop 'general tensor API supports real masses only'
      if (any(shifts(1,:)/=0d0)) error stop 'general API requires first shift zero'
      call general_ti_reduce(mode,n,idim,powers(1:n),rank,count,shifts(1:n,:), &
                             masses_real(1:n),mu,result(0:count-1,:),stable)
    case('scalar')
      if (rank/=0) error stop 'scalar requires rank=0'
      if (complex_mass) then
        result(0,:)=comp_scalar_integral_reduce(n,idim,powers(1:n),shifts(1:n,:),masses(1:n))
      else
        result(0,:)=scalar_integral_reduce(n,idim,powers(1:n),shifts(1:n,:),masses_real(1:n))
      end if
      stable=STABLE_IREGI
    case default
      error stop 'Unknown API'
    end select
    if (.not.all(ieee_is_finite(real(result(0:count-1,:)))).or. &
        .not.all(ieee_is_finite(aimag(result(0:count-1,:))))) then
      write(output_unit,'(a)') 'RESULT {"id":"'//trim(request_id)// &
        '","stable":false,"error":"nonfinite_reference_output","moments":null}'
      flush(output_unit)
      call IREGI_FREE_PS
      cycle
    end if
    write(output_unit,'(a)',advance='no') 'RESULT {"id":"'//trim(request_id)//'","stable":'
    if (stable) then
      write(output_unit,'(a)',advance='no') 'true'
    else
      write(output_unit,'(a)',advance='no') 'false'
    end if
    write(output_unit,'(a)',advance='no') ',"poles":["uv1","ir1","ir2","finite"],"moments":['
    do i=0,count-1
      if (i>0) write(output_unit,'(a)',advance='no') ','
      write(output_unit,'(a)',advance='no') '['
      do j=1,4
        if (j>1) write(output_unit,'(a)',advance='no') ','
        write(output_unit,'(a,es25.17e3,a,es25.17e3,a)',advance='no') &
          '[',real(result(i,j)),',',aimag(result(i,j)),']'
      end do
      write(output_unit,'(a)',advance='no') ']'
    end do
    write(output_unit,'(a)') ']}'
    flush(output_unit)
    call IREGI_FREE_PS
  end do
end program iregi_reference
