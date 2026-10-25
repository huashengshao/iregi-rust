#!/usr/bin/env python3
"""Portable capsule integrity only; no producer imports or execution."""
from pathlib import Path
import argparse,hashlib,json
def sha(path):
    with path.open("rb") as stream:return hashlib.file_digest(stream,"sha256").hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--origins",action="store_true");args=parser.parse_args()
    capsule=Path(__file__).resolve().parent;root=capsule.parents[1]
    manifest=json.loads((capsule/"manifest.json").read_text())
    actual={str(p.relative_to(capsule)) for p in capsule.rglob("*") if p.is_file()}
    assert actual==set(manifest["payloads"])|{"manifest.json"},"capsule membership differs"
    for relative,item in manifest["payloads"].items():
        path=capsule/relative;assert path.stat().st_size==item["bytes"] and sha(path)==item["sha256"],relative
        if args.origins and item["kind"]=="exact-copy":assert sha(root/item["origin"])==item["sha256"],item["origin"]
    parent=json.loads((capsule/"parent.json").read_text())
    for name in ("parent_archive","parent_manifest"):
        item=parent[name];assert sha(root/item["path"])==item["sha256"],name
    q=json.loads((capsule/"qualification.json").read_text());r=json.loads((capsule/"runtime/results.json").read_text())
    assert q["status"]=="private-constructor-cohort-qualified" and r["status"]=="passed"
    assert len(r["cases"])==7 and len(r["listings"])==2 and len(r["input_sha256"])==646
    assert all(x["status"]=="passed" for x in r["cases"]) and all(x["inventory_verified"] for x in r["listings"])
    assert r["inputs_unchanged"] and not r["deadline_exceeded"] and not r["cleanup_errors"]
    assert r["elapsed_seconds"]<292 and q["historical_ordinary_execution"]["newly_rerun"] is False
    assert all(q["not_qualified"].values()) and q["compiler_or_cargo_execution"] is False and q["production_mutations"] is False
    print(json.dumps({"status":"passed","payloads":len(manifest["payloads"]),"source_origins_checked":args.origins,"new_tests":7,"historical_tests_not_rerun":20,"no_integral_or_benchmark_executed":True}))
if __name__=="__main__":main()
