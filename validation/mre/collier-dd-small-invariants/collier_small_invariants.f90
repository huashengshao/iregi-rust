! COLLIER 1.2.10: a top-loop pentagon (gg -> Hgg at sqrt(s) = 1 TeV) whose
! massless legs have binary64 invariants of ~1e-10 GeV^2 (computed from the
! momenta, as an amplitude code would) instead of exact zeros. With internal
! masses m_t^2 = 29929 GeV^2 the integral is regular there: the two inputs
! may differ by ~|p^2|/m^2 ~ 1e-15 only.
!
! Build: gfortran -O2 -ffree-line-length-none -I <collier>/modules \
!        collier_small_invariants.f90 <collier>/libcollier.a
program collier_small_invariants
  use collier
  implicit none
  integer, parameter :: n = 5, rank = 5
  double precision :: q(0:3, 0:n-1), d(0:3), scale, worst, size_, weight
  double complex :: mom(0:3, n-1), inv(n*(n-1)/2), zinv(n*(n-1)/2), masses(0:n-1)
  double complex :: t(0:rank,0:rank,0:rank,0:rank), tuv(0:rank,0:rank,0:rank,0:rank)
  double complex :: ref(0:rank,0:rank,0:rank,0:rank)
  double precision :: err(0:rank)
  integer :: i, k, distance, start, length, mode, flag, n0, n1, n2, n3
  ! Loop-momentum shifts q_i (GeV), stability study point pentagon-r5 #0.
  q(:,0) = [0.0d0, 0.0d0, 0.0d0, 0.0d0]
  q(:,1) = [500.0d0, 0.0d0, 0.0d0, 500.0d0]
  q(:,2) = [1000.0d0, 0.0d0, 0.0d0, 0.0d0]
  q(:,3) = [636.4389996374975d0, 200.64958343246792d0, -293.7037081332071d0, 75.1962597591425d0]
  q(:,4) = [381.0252510177986d0, -5.258369435281395d0, -357.7820947151467d0, 130.9372527789567d0]
  do i = 1, n - 1
    mom(:, i) = cmplx(q(:, i) - q(:, 0), 0d0, kind(1d0))
  end do
  ! COLLIER's invariant order: cyclic distances 1, 2.
  k = 0
  do distance = 1, n / 2
    length = n
    if (2 * distance == n) length = n / 2
    do start = 0, length - 1
      d = q(:, mod(start + distance, n)) - q(:, start)
      k = k + 1
      inv(k) = cmplx(d(0)**2 - d(1)**2 - d(2)**2 - d(3)**2, 0d0, kind(1d0))
    end do
  end do
  scale = maxval(abs(real(inv)))
  zinv = inv
  where (abs(real(zinv)) <= 1d-12 * scale) zinv = (0d0, 0d0)
  masses = (29929d0, 0d0)
  call Init_cll(n, rank, '', .false.)
  call SwitchOffFileOutput_cll
  call SetMuUV2_cll(1d6)
  call SetMuIR2_cll(1d6)
  if (command_argument_count() > 0) then
    ! The stability study's settings.
    call SetReqAcc_cll(1d-10)
    call SetCritAcc_cll(1d-3)
    call SetTenRed_cll(6)
    write(*, '(A)') 'SetReqAcc_cll(1e-10), SetCritAcc_cll(1e-3), SetTenRed_cll(6)'
  end if
  write(*, '(A)') 'invariants as computed from the momenta (GeV^2):'
  write(*, '(5ES12.3)') real(inv)
  do mode = 1, 2
    call SetMode_cll(mode)
    ref = (0d0, 0d0)
    t = (0d0, 0d0)
    call TNten_cll(ref, tuv, mom, zinv, masses, n, rank, err)
    call GetErrFlag_cll(flag)
    write(*, '(A,I1,A,I3,A,2ES24.15)') 'mode ', mode, ' exact-zero invariants: err flag', flag, &
      '  T(0,0,0,0) =', ref(0,0,0,0)
    call TNten_cll(t, tuv, mom, inv, masses, n, rank, err)
    call GetErrFlag_cll(flag)
    write(*, '(A,I1,A,I3,A,2ES24.15)') 'mode ', mode, ' computed invariants:   err flag', flag, &
      '  T(0,0,0,0) =', t(0,0,0,0)
    worst = 0d0
    size_ = 0d0
    do n0 = 0, rank
      do n1 = 0, rank - n0
        do n2 = 0, rank - n0 - n1
          do n3 = 0, rank - n0 - n1 - n2
            ! Moments weighted by mu^rank (mu = 1000 GeV).
            weight = 1d3**(n0 + n1 + n2 + n3)
            worst = max(worst, abs(t(n0,n1,n2,n3) - ref(n0,n1,n2,n3)) * weight)
            size_ = max(size_, abs(ref(n0,n1,n2,n3)) * weight)
          end do
        end do
      end do
    end do
    write(*, '(A,ES11.3)') '   E/A of the rank-5 tensor, computed against exact-zero invariants:', worst / size_
  end do
end program
