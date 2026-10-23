"""Inspect a built TIRust wheel before the first native import.

This is a local qualification helper, not part of the distributed interface.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stream_digest(stream) -> str:
    value = hashlib.sha256()
    while block := stream.read(1024 * 1024):
        value.update(block)
    return value.hexdigest()


wheel = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
root = Path.cwd()
checks: list[dict[str, object]] = []
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
    assert len(names) == len(set(names)), "duplicate wheel members"
    assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
    native = [name for name in names if name.endswith((".so", ".pyd", ".dylib"))]
    assert len(native) == 1 and native[0].startswith("tirust/_tirust."), native
    expected = [path for path in (root / "python/tirust").rglob("*") if path.is_file()]
    for path in expected:
        member = path.relative_to(root / "python").as_posix()
        source = path.read_bytes()
        packaged = archive.read(member)
        assert packaged == source, f"packaged bytes differ: {member}"
        checks.append({"path": member, "bytes": len(source), "sha256": digest(source)})
    assert any(item["path"] == "tirust/py.typed" for item in checks)
    assert sum(str(item["path"]).endswith(".pyi") for item in checks) >= 9
    secret = os.environ.get("SYMBOLICA_LICENSE", "").encode()
    for member in names:
        assert not any(part in {".env", "__pycache__", "site-packages"} for part in Path(member).parts)
        assert not member.endswith((".pyc", ".rlib", ".rmeta", ".o", ".a")), member
        if secret:
            with archive.open(member) as stream:
                tail = b""
                while block := stream.read(1024 * 1024):
                    combined = tail + block
                    assert secret not in combined, f"license credential in {member}"
                    tail = combined[-(len(secret) - 1):] if len(secret) > 1 else b""
    with archive.open(native[0]) as stream:
        native_sha256 = stream_digest(stream)
    with wheel.open("rb") as stream:
        wheel_sha256 = stream_digest(stream)
    receipt = {
        "scope": "built wheel ZIP/source/assets/stubs/credential inspection; no runtime assertion",
        "wheel": str(wheel.relative_to(root)),
        "wheel_sha256": wheel_sha256,
        "wheel_bytes": wheel.stat().st_size,
        "native_member": native[0],
        "native_sha256": native_sha256,
        "native_bytes": archive.getinfo(native[0]).file_size,
        "entry_count": len(names),
        "exact_source_member_count": len(checks),
        "credential_scan_performed": bool(secret),
        "pass": True,
        "members": checks,
        "zip_entries": names,
    }
output.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({key: value for key, value in receipt.items() if key not in {"members", "zip_entries"}}))
