! Direct bundled OneLOop probe, independent of IREGI's reduction dispatcher.
program box_probe
  use avh_olo_forIREGI
  implicit none
  complex(kind(1d0)) :: result(0:2), mass(4)
  integer :: i
  mass = [cmplx(1d0,-5d0,kind(1d0)), cmplx(3d0,-5d0,kind(1d0)), &
          cmplx(4d0,-5d0,kind(1d0)), cmplx(5d0,-5d0,kind(1d0))]
  call olo_scale(1d0)
  call olo(result, cmplx(-1d0,0d0,kind(1d0)), cmplx(-2d0,0d0,kind(1d0)), &
      cmplx(-2d0,0d0,kind(1d0)), cmplx(-1d0,0d0,kind(1d0)), &
      cmplx(-1d0,0d0,kind(1d0)), cmplx(-2d0,0d0,kind(1d0)), &
      mass(1), mass(2), mass(3), mass(4))
  do i = 0, 2
    write(*,'(a,i1,2(1x,es25.17e3))') 'SLOT ', i, real(result(i)), aimag(result(i))
  end do
end program box_probe
