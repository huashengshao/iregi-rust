from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path.cwd();base=root/'target/native-master-replay';source=base/'core';assert not source.exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',revision,'crates/iregi-rust'],text=True).splitlines();source_records={};working_differences=[]
for name in tracked:
 p=root/name
 if not p.is_file():continue
 original=subprocess.check_output(['git','show',f'{revision}:{name}'])
 if original!=p.read_bytes():working_differences.append(name)
 dst=source/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(original);source_records[name]=sha(dst)
execution=source/'crates/iregi-rust/src/execution.rs';text=execution.read_text();needle='''                    let evaluated = evaluator.evaluate_batch(&group.input, rows);
                    record_time(started, &mut self.profile.scalar_masters);'''
replacement='''                    let evaluated = evaluator.evaluate_batch(&group.input, rows);
                    crate::master_capture::record(family.name(), self.components, &group.input, &group.requests, &self.valid_lanes, &evaluated);
                    record_time(started, &mut self.profile.scalar_masters);'''
assert text.count(needle)==1;execution.write_text(text.replace(needle,replacement))
lib=source/'crates/iregi-rust/src/lib.rs';lib.write_text(lib.read_text()+'\nmod master_capture;\npub use master_capture::take_master_captures;\n')
shutil.copy2(base/'source/master_capture.rs',source/'crates/iregi-rust/src/master_capture.rs')
closure=root/'target/benchmark/dependency-closures/6b24c03-complete-kinds';manifest=json.loads((closure/'manifest.json').read_text());available={Path(r['retained']).name:r for r in manifest['files']}
filenames={'iregi_masters':'libiregi_masters-736462b347335a0f.rlib','symbolica':'libsymbolica-2ae1abcc9fd9c0db.rlib','oneloop':'liboneloop-6117c7de19c8681b.rlib','serde':'libserde-bde6fd4136f3a6c8.rlib','serde_json':'libserde_json-d5ce7f4fcf58bd84.rlib','thiserror':'libthiserror-7d7ef35ea784c43a.rlib'}
archives={}
for name,file in filenames.items():
 p=closure/'deps'/file;assert sha(p)==available[file]['sha256'];archives[name]={'path':str(p),'sha256':sha(p)}
master_paths=subprocess.check_output(['git','ls-files','crates/iregi-masters'],text=True).splitlines()
assert subprocess.check_output(['git','diff','6b24c03..'+revision,'--','crates/iregi-masters'])==b'', 'default masters changed from frozen closure'
inputs=root/'validation/benchmark/baseline-6b24c03-licensed/results-inputs.json';shutil.copy2(inputs,base/'inputs.json')
records={'source_revision':revision,'source_before':source_records,'working_differences_excluded':working_differences,'private_changes':'One observational record call after public scalar evaluation plus private capture module/re-export; no math or branch rewrite','archives':archives,'dependency_closure_manifest':str(closure/'manifest.json'),'dependency_closure_manifest_sha256':sha(closure/'manifest.json'),'masters_source_unchanged_from':'6b24c03','benchmark_input_source':str(inputs),'benchmark_input_sha256':sha(inputs)}
(base/'preparation.json').write_text(json.dumps(records,indent=2)+'\n')
with (base/'capture.patch').open('w') as out:
 for name in ['execution.rs','lib.rs']:
  subprocess.run(['diff','-u',str(root/'crates/iregi-rust/src'/name),str(source/'crates/iregi-rust/src'/name)],stdout=out,check=False)
print(json.dumps({'source_revision':revision,'sources':len(source_records),'archives':len(archives),'inputs_sha256':sha(inputs)},indent=2))
