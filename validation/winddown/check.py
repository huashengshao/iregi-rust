#!/usr/bin/env python3
"""Read-only archive/report preservation checks; no numerical-library imports."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import subprocess
import tarfile

ROOT = Path.cwd()
BASE = "007ca9f7b1f3cd2005e0d4df1fcfb24f55aaecc7"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def raw_values(text):
    decoder = json.JSONDecoder()
    position = text.index("{") + 1
    values = {}
    while True:
        while text[position].isspace():
            position += 1
        if text[position] == "}":
            assert not text[position + 1:].strip()
            return values
        key, position = decoder.raw_decode(text, position)
        assert key not in values
        while text[position].isspace():
            position += 1
        assert text[position] == ":"
        position += 1
        while text[position].isspace():
            position += 1
        start = position
        _, position = decoder.raw_decode(text, position)
        values[key] = text[start:position]
        while text[position].isspace():
            position += 1
        if text[position] == ",":
            position += 1
        else:
            assert text[position] == "}"


baseline_text = subprocess.check_output(
    ["git", "show", f"{BASE}:docs/data/results.json"], text=True
)
current_text = (ROOT / "docs/data/results.json").read_text()
baseline = raw_values(baseline_text)
current = raw_values(current_text)
assert len(baseline) == 279
assert all(current.get(key) == value for key, value in baseline.items())
data = json.loads(current_text)
assert set(data) - set(baseline) == {
    "private_n7_rank0_numeric_qualification",
    "private_uniform_branch_dependent_qualification",
    "winddown_work_in_progress",
}
bound = exact = 0
for key, value in data.items():
    if not isinstance(value, dict):
        continue
    if not isinstance(value.get("source"), str) or not isinstance(value.get("sha256"), str):
        continue
    source = ROOT / value["source"]
    assert digest(source.read_bytes()) == value["sha256"], key
    bound += 1
    if "snapshot" in value and source.suffix == ".json":
        if json.loads(source.read_text()) == value["snapshot"]:
            exact += 1
        else:
            assert key == "symbolica_production_qualification", key

archives = json.loads((ROOT / "validation/winddown/manifest.json").read_text())
archive_members = 0
for name, item in archives["archives"].items():
    path = ROOT / "validation/winddown" / item["path"]
    content = path.read_bytes()
    assert digest(content) == item["sha256"] and len(content) == item["bytes"], name
    actual = {}
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
        for member in archive:
            assert member.isfile() and not member.name.startswith("/")
            assert ".." not in Path(member.name).parts
            assert member.name not in actual
            body = archive.extractfile(member).read()
            assert not body.startswith((b"\x7fELF", b"!<arch>"))
            actual[member.name] = {"sha256": digest(body), "bytes": len(body)}
            archive_members += 1
    assert actual == item["members"], name

capsule_payloads = 0
for directory, index_name, key in [
    ("highpoint-thin-n7-rank0-rational-numeric", "manifest.json", "files"),
    ("uniform-branch-dependent", "qualification.json", "files"),
]:
    folder = ROOT / "validation" / directory
    index = json.loads((folder / index_name).read_text())[key]
    actual = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
    assert actual == set(index) | {index_name}
    for relative, item in index.items():
        content = (folder / relative).read_bytes()
        assert digest(content) == item["sha256"] and len(content) == item["bytes"]
        capsule_payloads += 1

print(json.dumps({
    "status": "passed",
    "historical_raw_objects_preserved": len(baseline),
    "bound_report_sources": bound,
    "exact_report_json_snapshots": exact,
    "winddown_archives": len(archives["archives"]),
    "winddown_archive_members": archive_members,
    "new_sealed_capsule_payloads": capsule_payloads,
    "no_integral_or_benchmark_executed": True,
}))
