! Validation template: check.py inserts each original/harness policy verbatim.
program snapping_reference
use global
use kinematics
implicit none
real(kind(1d0)) :: p(0:3),q(0:3)
complex(kind(1d0)) :: z
logical :: complex_mode
ZEROTHR_IREGI=0.125d0
nmass=1; massref(1)=8d0
call probe('zero-boundary',1d0)
call probe('zero-inside',nearest(1d0,-1d0))
call probe('mass-lower-boundary',7d0)
call probe('mass-upper-boundary',9d0)
call probe('mass-inside',7.5d0)
ZEROTHR_IREGI=0d0
call build([dcmplx(8d0,0d0)])
call probe('zero-threshold-retains-small-nonzero',1d-12)
call probe('zero-threshold-retains-near-mass',8d0+1d-10)
call build([dcmplx(-4d0,0d0)])
call probe('zero-threshold-negative-reference-changes-zero',0d0)
nmass=0; ZEROTHR_IREGI=0d0
call probe('massless-inside-independent-threshold',nearest(1d-3,-1d0))
call probe('massless-boundary',1d-3)
call probe('massless-negative-boundary',-1d-3)
ZEROTHR_IREGI=1d-6
call build([dcmplx(4d0,0d0),dcmplx(4d0+2d-6,0d0),dcmplx(9d0,0d0)])
call report('duplicate-first-preserved')
call build([dcmplx(4d0,0d0),dcmplx(100d0,0d0)])
call probe('order-first-small',1d-5)
call build([dcmplx(100d0,0d0),dcmplx(4d0,0d0)])
call probe('order-first-large',1d-5)
call build([dcmplx(4d0,0d0),dcmplx(-9d0,0d0)])
call report('negative-candidate-deduplicated')
call build([dcmplx(-4d0,0d0),dcmplx(9d0,0d0)])
call report('negative-first-kept')
call probe('negative-first-snaps-unrelated-value',123d0)
call build([dcmplx(0d0,-2d0),dcmplx(4d0,-0.1d0)])
call report('complex-real-parts-only')
ZEROTHR_IREGI=0.125d0
call build([dcmplx(0.125d0,0d0),dcmplx(7d0,0d0),dcmplx(8d0,0d0)])
call report('admission-and-dedup-boundaries')
nmass=1;massref(1)=8d0
p=[1d0,0d0,0d0,0d0];q=[0.5d0,0d0,0d0,0d0]
ONSHELL_IREGI=.false.;check=.false.
write(*,'(A,ES26.17)') 'flags-disabled ',scalarprod(p,q)
check=.true.
write(*,'(A,ES26.17)') 'check-enables-snap ',scalarprod(p,q)
z=cscalarprod(dcmplx(p,0d0),dcmplx(q,0d0))
write(*,'(A,2ES26.17)') 'complex-scalarprod-unsnapped ',z
ZEROTHR_IREGI=1d-6;massref(1)=4d0;nmass=1
p=[1d0,0d0,0d0,0d0];q=[4.000001d0,1d0,0d0,0d0]
write(*,'(A,ES26.17)') 'cross-direct-snapped ',scalarprod(p,q)
write(*,'(A,ES26.17)') 'cross-reconstructed-from-snapped-distances ', &
  (scalarprod(p,p)+scalarprod(q,q)-scalarprod(p-q,p-q))/2d0
call build([dcmplx(1d0,-1d-15)])
call report('imaginary-dispatch-boundary')
call build([dcmplx(1d0,-nearest(1d-15,1d0))])
call report('imaginary-dispatch-above-boundary')
ZEROTHR_IREGI=0.1d0
call build([dcmplx(8d0,0d0),dcmplx(9d0,0d0)])
call probe('first-matching-reference-low',8.5d0)
call build([dcmplx(9d0,0d0),dcmplx(8d0,0d0)])
call probe('first-matching-reference-high',8.5d0)
ZEROTHR_IREGI=2d0
call build([dcmplx(8d0,0d0)])
call probe('zero-branch-precedes-mass-branch',8d0)
contains
subroutine probe(label,input)
character(len=*),intent(in)::label
real(kind(1d0)),intent(in)::input
real(kind(1d0))::actual
actual=input
call makeonshell(nmass,massref(1:nmass),actual)
write(*,'(A,1X,2ES26.17)') label,input,actual
end subroutine
subroutine report(label)
character(len=*),intent(in)::label
write(*,'(A,1X,I0,1X,I0,1X,20ES26.17)') label,nmass,merge(1,0,complex_mode),massref(1:nmass)
end subroutine
subroutine build(M2L)
complex(kind(1d0)),intent(in)::M2L(:)
complex(kind(1d0))::masses(size(M2L))
real(kind(1d0))::M2LR(size(M2L)),masses_real(size(M2L)),masses_imag(size(M2L)),threshold
integer::i,j,n,nnonzeromass,NLOOPLINE
logical::exist,comp_mass_scheme,complex_mass,mass_exists
NLOOPLINE=size(M2L)
n=NLOOPLINE
masses=M2L
masses_real=dreal(M2L)
masses_imag=dimag(M2L)
threshold=ZEROTHR_IREGI
! POLICY_INSERTION
! COMPLEX_RESULT_INSERTION
end subroutine
end program
