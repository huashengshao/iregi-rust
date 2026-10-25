#!/usr/bin/env python3
"""Independent positive-F defining-integral oracle; source preparation only.

Without --run this prints the finite proposed catalogue and performs no
quadrature. Each explicitly selected run computes twelve integrals in one 4D
Gauss pass. No IREGI/TIRust/reference executable or reduction formula is called.
Expression preparation belongs to Symbolica in the separate Rust driver.
"""
import argparse
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import time

RULE_SOURCE=Path('validation/shifted-pentagon/adjudicate.py')
RULE_SOURCE_SHA256='ef11c91cbdaf453733e8f710237245d647c79dbe5f619c514295d2654444a1ca'
RULE_FUNCTION_SHA256='fd8e964d56aa8519d8ff7fb42083f184ace108a2d8da79016be0799cfb2d5480'
POINTS=((0,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(0,1,1,1))
MASSES=(4,9,16,25,36)
MU=3
SAMPLE_CUBES=(('1/2','1/3','1/4','1/5'),('1/7','2/5','3/8','4/9'),
              ('3/4','1/6','2/7','3/10'))
CATALOG=(('q12-d50',12,50),('q16-d70',16,70),('q20-d90',20,90))
POLES=('uv1','ir1','ir2','finite')

def require(value,message):
    if not value:raise ValueError(message)

def unique_object(pairs):
    result={}
    for name,value in pairs:
        require(name not in result,'duplicate JSON key '+name)
        result[name]=value
    return result

def invalid_constant(text):raise ValueError('nonfinite JSON constant '+text)

def load_json(path):
    raw=Path(path).read_bytes()
    return (json.loads(raw,parse_float=str,parse_constant=invalid_constant,
                       object_pairs_hook=unique_object),hashlib.sha256(raw).hexdigest())

def exact(value):
    require(type(value) in (str,int),'an exact rational string or integer is required')
    return Fraction(value)

def pair_distances(points):
    """Numerical Minkowski input invariants, never symbolic expressions."""
    values=[]
    for i in range(5):
        for j in range(i+1,5):
            difference=[a-b for a,b in zip(points[i],points[j])]
            square=difference[0]**2-sum(value**2 for value in difference[1:])
            values.append((i,j,square))
    return values

BASE_DISTANCES=pair_distances(POINTS)

def cube_map(cube):
    """Evaluate the existing stick-breaking numerical map and Jacobian."""
    u,v,w,z=cube
    a,b,c=1-u,1-v,1-w
    return (u,a*v,a*b*w,a*b*c*z,a*b*c*(1-z)),a**3*b**2*c

def numeric_f(xs,masses,distances):
    """Evaluate the documented one-loop Symanzik pair sum numerically."""
    return sum(x*mass for x,mass in zip(xs,masses))-sum(
        xs[i]*xs[j]*square for i,j,square in distances)

def verify_symbolica_preparation(path):
    """Check exact exported numeric samples, without parsing any polynomial.

    Accept either the preparation object or a full driver result containing it.
    This is a consistency witness for the driver-owned Symbolica preparation;
    the independent integral continues to use the original numerical pair sum.
    """
    document,sha=load_json(path)
    preparation=document.get('oracle_preparation',document)
    require(preparation['schema_version']==1,'Symbolica preparation schema')
    require(preparation['algebra_provider']=='Symbolica','algebra provider')
    require(preparation['cube_variable_order']==['u','v','w','z'],'cube variable order')
    require(preparation['simplex_variable_order']==['x0','x1','x2','x3','x4'],
            'simplex variable order')
    for name in ['F_expression','jacobian_expression']:
        require(isinstance(preparation[name],str) and preparation[name].strip(),
                'missing Symbolica expression provenance '+name)
    evaluations=preparation['evaluations']
    require(isinstance(evaluations,list) and len(evaluations)==3,'three exact Symbolica sample witnesses')
    expected={tuple(map(Fraction,cube)) for cube in SAMPLE_CUBES}
    observed=set()
    for witness in evaluations:
        cube=tuple(map(exact,witness['cube']))
        require(cube in expected and cube not in observed,'sample identity/duplicate')
        observed.add(cube)
        xs,jacobian=cube_map(cube)
        require(len(witness['simplex'])==5 and tuple(map(exact,witness['simplex']))==xs,
                'Symbolica map numeric witness')
        require(exact(witness['F'])==numeric_f(xs,MASSES,BASE_DISTANCES),
                'Symbolica F numeric witness')
        require(exact(witness['jacobian'])==jacobian,'Symbolica Jacobian numeric witness')
        require(sum(xs)==1 and all(x>=0 for x in xs),'simplex sample domain')
    require(observed==expected,'all prescribed Symbolica witnesses')
    return {'path':str(path),'sha256':sha,'exact_numeric_samples_checked':3,
            'expression_strings_interpreted':False}

def reused_unit_rule(mp):
    """Load only the hash-pinned existing unit_rule AST, never its module.

    In particular, adjudicate.py's old reference-capture imports and its main
    function are never imported or executed. The sole extracted function calls
    mpmath's Gauss-Legendre implementation; no roots or polynomials are local.
    """
    raw=RULE_SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==RULE_SOURCE_SHA256,'quadrature helper source changed')
    source=raw.decode()
    tree=ast.parse(source,filename=str(RULE_SOURCE))
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='unit_rule']
    require(len(nodes)==1 and not nodes[0].decorator_list,'single plain unit_rule helper')
    node=nodes[0]
    segment=ast.get_source_segment(source,node)
    require(hashlib.sha256(segment.encode()).hexdigest()==RULE_FUNCTION_SHA256,
            'quadrature helper function changed')
    require([arg.arg for arg in node.args.args]==['order'],'quadrature helper signature')
    isolated=ast.Module(body=[node],type_ignores=[])
    namespace={'mp':mp,'zip':zip,'__builtins__':{}}
    exec(compile(isolated,str(RULE_SOURCE)+'::unit_rule','exec'),namespace)
    return namespace['unit_rule']

def load_mpmath():
    try:
        import mpmath
    except ModuleNotFoundError:
        # Existing validation tooling uses the same optional pinned Nix package.
        import glob
        version=f'{sys.version_info.major}.{sys.version_info.minor}'
        candidates=glob.glob(f'/nix/store/*-python{version}-mpmath-*/lib/python{version}/site-packages')
        require(len(candidates)==1,'provide one mpmath installation in the validation environment')
        sys.path.insert(0,candidates[0])
        import mpmath
    return mpmath

def catalogue():
    return {'status':'proposed_unexecuted_finite_oracle_catalogue',
      'runs':[{'id':name,'order_per_axis':order,'working_decimal_digits':digits,
               'four_dimensional_nodes':order**4,'simultaneous_integrals':12}
              for name,order,digits in CATALOG],
      'base_fixture':{'shifts':[list(point) for point in POINTS],
                      'mass_squared':list(MASSES),'mu':MU},
      'requests':[{'id':'h1-unit','h':1,'powers':[1]*5}]+[
          {'id':f'h{h}-dot{i}','h':h,'powers':[2 if j==i else 1 for j in range(5)]}
          for h in [0,1] for i in range(5)],
      'additional_control':'h0 unit integral, simultaneously accumulated',
      'amplitude_targets':{'Rust_vs_independent_oracle':'1e-10 dimensionally normalized',
          'proposed_oracle_refinement':'1e-12 dimensionally normalized, an empirical convergence gate only',
          'Rust128_vs_Rust256':'2^-80; distinct from quadrature and finite-difference convergence'},
      'mixed_norm_squared':'|actual-reference|^2/max((Q²)^(4+2h-2*sum(powers)),|reference|²); Q²=max(1,|m_i²|,|(p_i-p_j)²|); use native coefficients and finer oracle as reference',
      'no_automatic_refinement_retry_or_qualification':True,
      'note':'Orders/digits are a finite proposal, not executed evidence or guaranteed accuracy. Root must authorize each bounded capture.'}

def evaluate(run_id,preparation_path,mass_shifts,scale):
    selected=[entry for entry in CATALOG if entry[0]==run_id]
    require(len(selected)==1,'run must belong to the fixed finite catalogue')
    _,order,digits=selected[0]
    preparation=verify_symbolica_preparation(preparation_path)
    require(len(mass_shifts)==5,'five exact squared-mass offsets required')
    require(scale>0 and min(Fraction(mass)+shift for mass,shift in zip(MASSES,mass_shifts))>0,
            'strictly positive real Feynman-parameter endpoint required')
    mp=load_mpmath()
    started=time.monotonic()
    with mp.workdps(digits):
        number=lambda value:mp.mpf(value.numerator)/mp.mpf(value.denominator)
        scaled_points=[tuple(Fraction(value)*scale for value in point) for point in POINTS]
        masses=[(Fraction(mass)+shift)*scale**2 for mass,shift in zip(MASSES,mass_shifts)]
        distances=[(i,j,number(square)) for i,j,square in pair_distances(scaled_points)]
        numeric_masses=[number(mass) for mass in masses]
        rule=reused_unit_rule(mp)(order)
        require(len(rule)==order and all(0<x<1 and weight>0 for x,weight in rule),
                'valid positive interior Gauss-Legendre rule')
        totals=[mp.mpf(0) for _ in range(12)]
        nodes=0
        for u,wu in rule:
            a=1-u
            for v,wv in rule:
                b=1-v
                for w,ww in rule:
                    c=1-w
                    # Same stick-breaking loop/Jacobian as existing independent
                    # parameter_integrals; this is numerical map evaluation.
                    prefix=wu*wv*ww*a**3*b**2*c
                    for z,wz in rule:
                        xs=(u,a*v,a*b*w,a*b*c*z,a*b*c*(1-z))
                        f=numeric_f(xs,numeric_masses,distances)
                        require(mp.isfinite(f) and f>0,'invalid parameter denominator')
                        inv=1/f
                        weighted2=prefix*wz*inv**2
                        weighted3=weighted2*inv
                        weighted4=weighted3*inv
                        totals[0]-=2*weighted3
                        totals[1]-=weighted2
                        for i,x in enumerate(xs):
                            totals[2+i]+=6*x*weighted4
                            totals[7+i]+=2*x*weighted3
                        nodes+=1
        require(nodes==order**4 and all(mp.isfinite(value) for value in totals),
                'complete finite twelve-integral capture')
        text=lambda value:mp.nstr(value,digits-8)
        requests=[]
        for request in catalogue()['requests']:
            index=1 if request['id']=='h1-unit' else 2+int(request['id'][-1])+5*request['h']
            j=totals[index]
            # This positive-F family has no UV/IR poles. Multiplication by the
            # finite native factor introduces no Laurent pole-to-finite mixing.
            native_imaginary=mp.pi**(2+request['h'])*j
            requests.append({**request,'J':text(j),'native_Laurent_order':list(POLES),
                'native_slots':[['0','0'],['0','0'],['0','0'],['0',text(native_imaginary)]],
                'known_poles':'zero by massive positive-F defining-integral domain, not by projecting reducer output'})
        result={'schema_version':1,'status':'complete_finite_parameter_capture_not_yet_qualified',
          'run_id':run_id,'order_per_axis':order,'working_decimal_digits':digits,
          'serialized_decimal_digits':digits-8,'nodes_evaluated':nodes,'simultaneous_integrals':12,
          'integral_names':['J_h0_unit','J_h1_unit']+[f'J_h0_dot{i}' for i in range(5)]+[f'J_h1_dot{i}' for i in range(5)],
          'finite_integrals':[text(value) for value in totals],'requests':requests,
          'h0_unit_derivative_control':text(totals[0]),
          'h0_unit_control':{'id':'h0-unit-control','h':0,'powers':[1]*5,'J':text(totals[0]),
              'native_Laurent_order':list(POLES),
              'native_slots':[['0','0'],['0','0'],['0','0'],['0',text(mp.pi**2*totals[0])]]},
          'common_mass_identity':{'expression':'sum_i J_h1_dot_i + J_h0_unit',
              'residual':text(mp.fsum(totals[7:12])+totals[0]),
              'independent_derivative_qualification':False,
              'reason':'These integrands share nodes; this is a correlated normalization/accumulation diagnostic.'},
          'fixture':{'shifts':[[str(value) for value in point] for point in scaled_points],
                     'mass_squared':[str(mass) for mass in masses],'mu':str(MU*scale),
                     'mass_offsets_before_scaling':[str(value) for value in mass_shifts],
                     'scale':str(scale),'F_lower_bound':str(min(masses))},
          'normalization':'J_h=pi^(-h) I_D with common i*pi^2 stripped; native finite=i*pi^(2+h)*J_h',
          'symbolica_preparation':preparation,
          'quadrature_reuse':{'path':str(RULE_SOURCE),'source_sha256':RULE_SOURCE_SHA256,
              'function':'unit_rule','function_source_sha256':RULE_FUNCTION_SHA256,
              'full_producer_module_imported':False},
          'mpmath_version':mp.__version__,'oracle_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'diagnostic_wall_seconds':str(time.monotonic()-started),
          'independent_of_reduction':True,'numerator_or_tensor_reduction_used':False,
          'quadrature_convergence_checked':False,'rigorous_error_bound':False,
          'public_generalized_numeric_domain_qualified':False,'performance_qualified':False,
          'automatic_retry_or_refinement':False}
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',choices=[entry[0] for entry in CATALOG],
                        help='explicitly execute one separately authorized finite quadrature run')
    parser.add_argument('--preparation-json',type=Path,help='driver Symbolica expressions and exact sample witnesses')
    parser.add_argument('--output',type=Path,help='new capture JSON; existing captures are never overwritten')
    parser.add_argument('--mass-shifts',default='0,0,0,0,0',help='five rational mass-squared offsets, before scaling; extra runs require separate authorization')
    parser.add_argument('--scale',default='1',help='positive exact momentum scale; extra runs require separate authorization')
    args=parser.parse_args()
    if args.run is None:
        print(json.dumps(catalogue(),indent=2,sort_keys=True));return 0
    require(args.output is not None and args.preparation_json is not None,
            '--run requires --output and --preparation-json')
    require(not args.output.exists(),'preserve prior capture; no retry/overwrite')
    try:
        result=evaluate(args.run,args.preparation_json,
                        [exact(value) for value in args.mass_shifts.split(',')],exact(args.scale))
    except Exception as error:
        result={'schema_version':1,'status':'failed_parameter_capture','run_id':args.run,
                'error_type':type(error).__name__,'error':str(error),
                'requests':None,'quadrature_convergence_checked':False,
                'public_generalized_numeric_domain_qualified':False,'automatic_retry_or_refinement':False}
    with args.output.open('x') as stream:
        json.dump(result,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    print(json.dumps({'status':result['status'],'output':str(args.output),
                      'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))
    return 0 if result['status'].startswith('complete_') else 2

if __name__=='__main__':raise SystemExit(main())
