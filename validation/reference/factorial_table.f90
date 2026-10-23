program factorial_table
  use global
  use funlib, only: calc_factorial_pair
  implicit none
  integer :: i,j
  call calc_factorial_pair
  do i=1,MAXINDICES_IREGI
    do j=0,MAXRANK_IREGI
      write(*,'(i3,1x,i3,1x,f20.0)') i,j,factorial_pair(i,j)
    end do
  end do
end program factorial_table
