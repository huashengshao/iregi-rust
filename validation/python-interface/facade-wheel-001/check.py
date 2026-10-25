"""Portable saved-only replay; no compiler, native host, process or kernel calls."""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import json
import tarfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PREFIX = "target/python-facade-wiring/"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def restore_files(manifest):
    files = {}
    for field in ("source_archive", "evidence_archive"):
        item = manifest[field]
        data = (HERE / item["path"]).read_bytes()
        assert len(data) == item["bytes"] and digest(data) == item["sha256"]
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(data)), mode="r:") as archive:
            members = archive.getmembers()
            assert len(members) == len(item["members"])
            assert {member.name for member in members} == set(item["members"])
            for member in members:
                assert member.isfile() and not PurePosixPath(member.name).is_absolute()
                assert ".." not in PurePosixPath(member.name).parts
                value = archive.extractfile(member).read()
                expected = item["members"][member.name]
                assert len(value) == expected["bytes"] and digest(value) == expected["sha256"]
                if member.name in files:
                    assert files[member.name] == value
                files[member.name] = value
    return files


def main():
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert digest(Path(__file__).read_bytes()) == manifest["checker_sha256"]
    files = restore_files(manifest)
    read = lambda name: json.loads(files[PREFIX + name])
    stages = ["build", "install", "import", "collect", "historical", "generic", "n6", "n7", "typing"]
    groups = []
    for name in stages:
        receipt = read(name + "-001/receipt.json")
        assert receipt["status"] == "passed" and not receipt["cleanup_errors"]
        assert receipt["cancellation"] is None
        assert receipt["elapsed_seconds"] <= receipt["total_seconds"]
        assert receipt["live_main_source_lease"] == (name == "build")
        for step in receipt["steps"]:
            assert step["status"] == "exited" and step["returncode"] == 0
            assert step["owned_group_gone"] is True and not step.get("timeout", False)
            groups.append(step["owned_process_group"])
    assert len(groups) == len(set(groups)) == 10
    counts = {"historical": 29, "generic": 4, "n6": 1, "n7": 1}
    for name, count in counts.items():
        cases = list(ET.fromstring(files[PREFIX + name + "-001/tests.xml"]).iter("testcase"))
        assert len(cases) == count and all(not list(case) for case in cases)
        assert len(read(name + "-001/receipt.json")["test_names"]) == count
    assert len(read("collect-001/receipt.json")["test_names"]) == 6
    identity = read("import-001/identity.json")
    coercion = identity["upstream_complex_integer_coercion"]
    assert coercion["real_bits"] == coercion["integer_scaled_imaginary_bits"] == 2
    assert coercion["imaginary_bits"] == coercion["float_scaled_imaginary_bits"] == 128
    assert coercion["integer_scaled_imaginary_ratio"] != coercion["float_scaled_imaginary_ratio"]
    assert coercion["lost_imaginary_digits"] is True
    typing = read("typing-001/receipt.json")["typing_summary"]
    assert typing["errorCount"] == typing["warningCount"] == 0
    assert read("build-001/wheel.json") == manifest["wheel"]
    source = manifest["source_archive"]["members"]
    assert len(source) == 116
    assert source["crates/iregi-python/src/numerical.rs"]["sha256"] == "f61088b6af21ddb3cb0634d1f9776722683def57956ff5a40a018e4855b1f6e5"
    assert source["tests/python/test_tirust_dispatch.py"]["sha256"] == "c92123ec9a24d8e97a01e20ce6eb4cae3ffc44395ea244f1f1fd1567fdd8823c"
    print(json.dumps({"status": "passed_saved_only", "restored_files": len(files), "source_files": 116,
        "passed_installed_tests": sum(counts.values()), "typing_errors": 0, "typing_warnings": 0,
        "original_integer_coercion_loss_retained": True, "later_corrected_wheel_qualified": False,
        "native_or_process_execution": False}))


if __name__ == "__main__":
    main()
