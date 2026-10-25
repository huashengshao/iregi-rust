"""Prepare immutable deferred preflight/timing protocol; never executes a probe."""
from pathlib import Path
import argparse
import ast
import datetime
import json
import sys
sys.dont_write_bytecode=True
import common as c
ROOT=Path('/shared/external/iregi/iregi-rust')
HERE=Path(__file__).resolve().parent
BASE=HERE.parent

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--mode',choices=['preflight','timing'],required=True);parser.add_argument('--cpu',type=int,required=True)
 parser.add_argument('--run-id',required=True)
 parser.add_argument('--captured-protocol',type=Path,default=BASE/'fresh-captured-runtime/protocol.json')
 parser.add_argument('--uncaptured-protocol',type=Path,default=BASE/'fresh-uncaptured-proposal/protocol.json')
 parser.add_argument('--captured-independent-admission',type=Path,required=True);parser.add_argument('--captured-independent-admission-sha256',required=True)
 parser.add_argument('--uncaptured-independent-admission',type=Path,required=True);parser.add_argument('--uncaptured-independent-admission-sha256',required=True)
 parser.add_argument('--preflight-independent-admission',type=Path);parser.add_argument('--preflight-independent-admission-sha256')
 parser.add_argument('--quiet-grant',type=Path);parser.add_argument('--quiet-grant-sha256')
 args=parser.parse_args();assert Path.cwd()==ROOT and args.cpu>=0
 assert args.run_id and all(value.isalnum()or value in'-_'for value in args.run_id)
 destination=HERE/(args.mode+'-'+args.run_id+'-protocol.json');assert not destination.exists()
 attempt=HERE/(args.mode+'-'+args.run_id);assert not attempt.exists()
 template=c.read(HERE/'protocol-template.json');bindings={}
 def add(path,wanted=None):
  path=Path(path).resolve();actual=c.ref.sha(path)
  if wanted is not None:assert actual==wanted,str(path)
  key=str(path);assert key not in bindings or bindings[key]==actual
  bindings[key]=actual;return path
 qualifications={};source_protocols={};verdicts={}
 for name,protocol_path,admission_path,admission_sha in [('captured',args.captured_protocol,args.captured_independent_admission,args.captured_independent_admission_sha256),('uncaptured',args.uncaptured_protocol,args.uncaptured_independent_admission,args.uncaptured_independent_admission_sha256)]:
  protocol_path=add(protocol_path);protocol=c.read(protocol_path);source_protocols[name]=protocol
  assert protocol['pinned_source_revision']==c.PIN
  receipt_path=protocol_path.parent/'qualification-001/results.json';raw_path=protocol_path.parent/'qualification-001/responses.jsonl'
  receipt=c.read(receipt_path);add(receipt_path);add(raw_path,receipt['raw_sha256'])
  assert receipt['protocol_sha256']==c.ref.sha(protocol_path)and receipt['status']=='passed-awaiting-independent-saved-data-review'
  assert receipt['guard_before']is True and receipt['guard_after']is True and receipt['cleanup_errors']==[]and receipt['deadline_exceeded']is False
  assert receipt['request_count']==60 and len(c.raw(raw_path))==120
  admission_path=add(admission_path,admission_sha);admission=c.read(admission_path);verdicts[name]=admission
  assert admission['status']=='passed'and admission['receipt_sha256']==c.ref.sha(receipt_path)and admission['raw_sha256']==c.ref.sha(raw_path)
  assert admission['request_count']==60 and admission['raw_event_count']==120 and admission['all_complete_records_and_controls_checked']is True
  assert admission['pinned_source_revision']==c.PIN
  add(admission['full_review_path'],admission['full_review_sha256'])
  if name=='uncaptured':assert admission['normal_projections']==52 and receipt['captured_projection']['normal_responses_checked']==52
  for path,wanted in {**protocol['protected_sha256'],**protocol['tool_sha256'],**receipt['input_sha256']}.items():add(Path(path)if Path(path).is_absolute()else ROOT/path,wanted)
  for item in receipt['executed_executables'].values():add(item['path'],item['sha256'])
  qualifications[name]={'protocol':str(protocol_path),'protocol_sha256':c.ref.sha(protocol_path),'receipt':str(receipt_path.resolve()),'receipt_sha256':c.ref.sha(receipt_path),'raw':str(raw_path.resolve()),'raw_sha256':c.ref.sha(raw_path),'independent_admission':str(admission_path),'independent_admission_sha256':c.ref.sha(admission_path)}
 assert verdicts['uncaptured']['captured_receipt_sha256']==qualifications['captured']['receipt_sha256']
 assert source_protocols['uncaptured']['captured_anchor']['receipt_sha256']==qualifications['captured']['receipt_sha256']
 build_path=Path(source_protocols['captured']['build_receipt']);build=c.read(build_path);add(build_path)
 assert source_protocols['captured']['build_receipt_sha256']==source_protocols['uncaptured']['build_receipt_sha256']==c.ref.sha(build_path)
 assert build['status']=='passed'and build['success']is True and len(build['steps'])==14 and all(step['status']=='passed'for step in build['steps'])
 assert build['guard_before']is True and build['guard_after']is True and build['cleanup_errors']==[]
 processes={}
 for label in c.TIRUST:
  item=build['outputs'][c.variant(label)+'-probe-'+('captured'if c.captured(label)else'uncaptured')]
  assert set(item['archive_binding'])=={'symbolica','oneloop','iregi_masters','iregi_rust'}
  add(item['path'],item['sha256']);processes[label]={key:item[key]for key in['path','sha256','bytes','archive_binding','link_map']}
 for path,wanted in c.ref.bindings().items():add(path,wanted)
 for label,path in [('iregi',c.ref.IREGI_BINARY),('collier',c.ref.COLLIER_BINARY)]:processes[label]={'path':str(path),'sha256':c.ref.sha(path),'bytes':path.stat().st_size}
 source_manifest=HERE/'source-manifest.json';manifest=c.read(source_manifest)
 for relative,wanted in manifest['files_sha256'].items():add(HERE/relative,wanted)
 add(source_manifest)
 for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
 runtime=dict(template);caps=template['fixed_stage_bounds'][args.mode]
 runtime.update(status='SOURCE_REVIEW_REQUIRED_NO_NUMERICAL_OR_TIMING_GRANT',mode=args.mode,cpu=args.cpu,
  pinned_source_revision=c.PIN,scope=template['scope'],recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  aggregate_budget_seconds=caps['aggregate_budget_seconds'],cleanup_postguard_reserve_seconds=caps['cleanup_postguard_reserve_seconds'],
  effective_work_deadline_seconds=caps['aggregate_budget_seconds']-caps['cleanup_postguard_reserve_seconds'],
  attempt_directory=str(attempt),taskset=source_protocols['captured']['taskset'],processes=processes,qualifications=qualifications,
  inputs=source_protocols['captured']['inputs'],control_shapes=str(HERE/'control-shapes.json'),source_manifest_sha256=c.ref.sha(source_manifest),quiet_grant=None,preflight_admission=None)
 assert c.ref.sha(runtime['inputs'])=='65d0d2fd554807478569ac88b6d689c9132ce541e98cfb2a3a55b8ef98e5c7ef'
 if args.mode=='timing':
  assert args.preflight_independent_admission is not None and args.quiet_grant is not None
  pre_path=add(args.preflight_independent_admission,args.preflight_independent_admission_sha256);pre=c.read(pre_path)
  assert pre['status']=='passed'and pre['mode']=='preflight'and pre['all_families_and_controls_checked']is True and pre['six_owned_processes_clean']is True and pre['pinned_source_revision']==c.PIN
  pre_receipt=add(pre['receipt_path'],pre['receipt_sha256']);pre_raw=add(pre_receipt.parent/'raw.jsonl',pre['raw_sha256']);pre_record=c.read(pre_receipt)
  assert pre_record['status']=='completed-preflight'and pre_record['global_lifecycle_clean']is True
  pre_protocol=add(pre_record['protocol'],pre_record['protocol_sha256']);pre_p=c.read(pre_protocol)
  assert pre_p['qualifications']==qualifications and pre_p['cpu']==args.cpu and pre_p['source_manifest_sha256']==c.ref.sha(source_manifest)
  add(pre['full_review_path'],pre['full_review_sha256'])
  runtime['preflight_admission']={'path':str(pre_path),'sha256':c.ref.sha(pre_path)}
  grant_path=add(args.quiet_grant,args.quiet_grant_sha256);grant=c.read(grant_path)
  assert grant['status']=='granted'and grant['mode']=='timing'and grant['pinned_source_revision']==c.PIN
  assert type(grant['cpu'])is int and grant['cpu']==args.cpu and grant['allowed_process_labels']==c.LABELS
  assert grant['source_manifest_sha256']==c.ref.sha(source_manifest)
  assert grant['aggregate_budget_seconds']==caps['aggregate_budget_seconds']and grant['cleanup_postguard_reserve_seconds']==caps['cleanup_postguard_reserve_seconds']
  assert grant['cpu_exclusive']is True and grant['no_other_project_compilers_or_numerics']is True
  assert type(grant['smt_siblings'])is list and all(type(cpu)is int and cpu>=0 for cpu in grant['smt_siblings'])
  assert type(grant['grant_id'])is str and grant['grant_id']
  runtime['quiet_grant']={'path':str(grant_path),'sha256':c.ref.sha(grant_path),'grant_id':grant['grant_id']}
 runtime['protected_sha256']=bindings
 runtime['tool_sha256']=dict(source_protocols['captured']['tool_sha256'])
 runtime['tool_sha256'][str(Path(sys.executable).resolve())]=c.ref.sha(Path(sys.executable).resolve())
 # Validate actual saved corpus and exact capture projections, without executing
 # an integral. This does not substitute for the independent review receipts.
 c.Context(runtime)
 with destination.open('x')as stream:stream.write(json.dumps(runtime,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'status':runtime['status'],'protocol':str(destination),'protocol_sha256':c.ref.sha(destination),'owned_processes':6,'timed_engines':4,'no_probe_compiler_or_timing_launched':True}))
if __name__=='__main__':main()
