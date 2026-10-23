#!/usr/bin/env python3
"""Copy immutable correctness evidence; never package compiled binaries or secrets."""
import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path.cwd()
HERE = ROOT / "target/raw-distance-lazy-capture-candidate"
DEST = ROOT / "validation/raw-distance-lazy-capture"


def sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


assert not DEST.exists(), "durable package is immutable once created"
review = read(HERE / "review/runtime-review.json")
assert review["status"] == "passed"
source = read(HERE / "source-manifest.json")
build = read(HERE / "build-001/build.json")
assert build["status"] == "passed" and build["inputs_unchanged"]
for path, digest in {**build["inputs"], **build["outputs"]}.items():
    assert sha(ROOT / path) == digest, path
groups = {name: read(HERE / f"build-001/runs/{name}.json") for name in ["receipts", "accounting", "snapshots"]}
for group in groups.values():
    assert group["status"] == "passed" and group["inputs_unchanged"]
DEST.mkdir()
mapping = {}


def copy(src, relative):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)
    assert sha(src) == sha(target)
    mapping[str(src.relative_to(ROOT))] = str(target.relative_to(ROOT))


for name in ["source-manifest.json", "input-manifest.json", "test-harness-mapping.json", "candidate.patch", "snapshots.rs", "freeze.py", "build.py", "run.py", "package.py"]:
    copy(HERE / name, name)
for name in ["final-review.json", "runtime-review.json"]:
    copy(HERE / "review" / name, "review/" + name)
for path in sorted((HERE / "build-001").glob("*.json")):
    copy(path, "build/" + path.name)
for path in sorted((HERE / "build-001").glob("*.log")):
    copy(path, "build/" + path.name)
for path in sorted((HERE / "build-001/runs").iterdir()):
    assert path.suffix in {".json", ".log"}
    copy(path, "runs/" + path.name)
for original, relative in [
    ("target/e6-direct-n2/preparation.json", "dependencies/native-closure-preparation.json"),
    ("target/core-fused-cse-census/supplemental-deps.json", "dependencies/supplemental-deps.json"),
    ("target/core-fused-cse-census/thiserror-metadata.txt", "dependencies/thiserror-metadata.txt"),
    ("target/core-fused-cse-census/thiserror-cargo-fingerprint.json", "dependencies/thiserror-cargo-fingerprint.json"),
    ("target/raw-distance-final-performance/source-manifest.json", "upstream/source-manifest.json"),
    ("validation/automatic-planar/final/adoption.patch", "upstream/adoption.patch"),
]:
    copy(ROOT / original, relative)
archive = DEST / "source-snapshots.tar.gz"
with open(archive, "wb") as raw:
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w") as tar:
            for tree in ["baseline", "candidate", "test-source"]:
                for path in sorted((HERE / tree).rglob("*")):
                    if not path.is_file():
                        continue
                    data = path.read_bytes()
                    info = tarfile.TarInfo(str(path.relative_to(HERE)))
                    info.size = len(data)
                    info.mode = 0o644
                    info.mtime = 0
                    tar.addfile(info, io.BytesIO(data))
with tarfile.open(archive, "r:gz") as tar:
    members = tar.getmembers()
    assert len(members) == 92
    for member in members:
        assert member.isfile()
        relative = "target/raw-distance-lazy-capture-candidate/" + member.name
        assert hashlib.sha256(tar.extractfile(member).read()).hexdigest() == source["bindings"][relative]
qualification = read(HERE / "qualification.json")


def remap(value):
    if isinstance(value, dict):
        return {key: remap(item) for key, item in value.items()}
    if isinstance(value, list):
        return [remap(item) for item in value]
    if isinstance(value, str):
        return mapping.get(value, value)
    return value


qualification = remap(qualification)
qualification.update(
    status="correctness_qualified_private_unmeasured",
    recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    independent_runtime_review={"path": str((DEST / "review/runtime-review.json").relative_to(ROOT)), "sha256": sha(DEST / "review/runtime-review.json")},
    source_archive={"path": str(archive.relative_to(ROOT)), "sha256": sha(archive), "files": 92, "verified_against_source_manifest": True},
)
qualification["limitations"].append("The PARITY_PASS fixed_iterations fields are inert labels inherited from the earlier probe. This driver has no timed mode and makes exactly seven snapshot calls per implementation per case.")
save(DEST / "qualification.json", qualification)
save(DEST / "copy-map.json", mapping)
readme = """# Private lazy receipt capture: correctness only

The candidate leaves outgoing distance-proof receipts absent until the first
certified zero or validated incoming-covered pair needs retaining. It preserves
conditioning, complete Taylor selections, source identity, ordered schema,
precision context, checked counters, and error harvesting. Production is unchanged.

The independent review passed. The bounded native-debug build passed, followed by
20 receipt/lifecycle tests (12 existing + 8 new), 6 accounting tests, and all 14
paired workload cases. Every cold/warm/final comparison includes exact input and
output bits, context, metadata/status/flags, public statistics/diagnostics and
private proof-work counters. Both sides confirm inactive N5 fallback counters.
The corpus contains 10,560 distinct complex output slots over 231 lane instances,
with seven calls per implementation per case. `fixed_iterations` log values are
inert inherited labels, not loop counts executed by this correctness-only driver.

This uses the retained current debug native dependency closure and supplemental
thiserror archive described in `dependencies/`. It is a different build scope from
the earlier optimized performance cohort. The supplemental thiserror record has
completed metadata/proc-macro events and source/fingerprint/native ELF evidence;
it does not claim a completed rlib Cargo event. No numerical dependency was rebuilt.

No timing, reference comparison or production adoption is qualified here. Build
and test elapsed times are diagnostics only. The preceding final performance
cohort, including its two regressions, remains unchanged. Lazy setup now occurs
inside the arguments-stage timer; any future performance decision must use total
time rather than infer improvement from stage boundaries.

`source-snapshots.tar.gz` retains 30 baseline, 31 candidate, and 31 narrow test-source
files. `source-manifest.json` and the reviews bind their hashes and the compact
test-module mapping. The scripts and logs retain exact commands, bounds and
pre/post input checks. Reproduction requires the recorded frozen native dependency
artifacts; those compiled files are intentionally not copied into this package.
Restore source/script files to `target/raw-distance-lazy-capture-candidate`, keep
the prior input/dependency paths from the manifests, source `scripts/env.sh` and
the untracked license environment, then use a fresh numbered build attempt:

```
python3 target/raw-distance-lazy-capture-candidate/build.py 002
python3 target/raw-distance-lazy-capture-candidate/run.py 002 receipts
python3 target/raw-distance-lazy-capture-candidate/run.py 002 accounting
python3 target/raw-distance-lazy-capture-candidate/run.py 002 snapshots
```

The first command enforces an overall 180-second compilation bound; each runtime
group has a 120-second bound. Existing records are never overwritten. The license
value is neither recorded nor included in this package.
"""
(DEST / "README.md").write_text(readme)
files = {str(p.relative_to(DEST)): sha(p) for p in sorted(DEST.rglob("*")) if p.is_file()}
save(DEST / "files.json", {"scope": "All durable payload files; self excluded", "files": files})
for relative, digest in files.items():
    assert sha(DEST / relative) == digest
print(json.dumps({"path": str(DEST.relative_to(ROOT)), "qualification_sha256": sha(DEST / "qualification.json"), "files": len(files), "archive_members": len(members)}))
