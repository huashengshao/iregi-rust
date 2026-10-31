! COLLIER 1.2.10: a regular seven-point tensor integral (exact dyadic shifts,
! squared masses 1..4, every invariant far below threshold) for which
! TNten_cll returns NaN in both COLI and DD modes from some rank on.
program collier_n7_nan
  use collier
  implicit none
  integer, parameter :: n = 7, rmax = 7
  double precision :: q(0:3, 0:n-1), d(0:3)
  double complex :: mom(0:3, n-1), inv(n*(n-1)/2), masses(0:n-1)
  double complex :: t(0:rmax,0:rmax,0:rmax,0:rmax), tuv(0:rmax,0:rmax,0:rmax,0:rmax)
  double precision :: err(0:rmax)
  integer :: i, k, distance, start, length, mode, rank, flag
  logical :: finite
  q(:,0) = [0d0, 0d0, 0d0, 0d0]
  q(:,1) = [0d0, 1d0, 0d0, 0d0]
  q(:,2) = [0d0, 0d0, 1d0, 0d0]
  q(:,3) = [0d0, 0d0, 0d0, 1d0]
  q(:,4) = [0.5d0, 0d0, 0d0, 0d0]
  q(:,5) = [0d0, 1d0, 1d0, 0d0]
  q(:,6) = [0.25d0, 0.375d0, 0.125d0, 0.625d0]
  masses = [(1d0,0d0), (2d0,0d0), (3d0,0d0), (4d0,0d0), (2d0,0d0), (3d0,0d0), (4d0,0d0)]
  do i = 1, n - 1
    mom(:, i) = cmplx(q(:, i) - q(:, 0), 0d0, kind(1d0))
  end do
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
  call Init_cll(n, rmax, '', .false.)
  call SwitchOffFileOutput_cll
  call SetMuUV2_cll(9d0)
  call SetMuIR2_cll(9d0)
  do mode = 1, 2
    call SetMode_cll(mode)
    do rank = 0, rmax
      t = (0d0, 0d0)
      call TNten_cll(t, tuv, mom, inv, masses, n, rank, err)
      call GetErrFlag_cll(flag)
      finite = .not. any(isnan(real(t(0:rank,0:rank,0:rank,0:rank))) .or. isnan(aimag(t(0:rank,0:rank,0:rank,0:rank))))
      write(*, '(A,I1,A,I1,A,L1,A,I3,A,2ES14.6)') 'mode ', mode, ' rank ', rank, ': finite ', finite, &
        '  err flag', flag, '  T(0,0,0,0) =', t(0,0,0,0)
    end do
  end do
end program
