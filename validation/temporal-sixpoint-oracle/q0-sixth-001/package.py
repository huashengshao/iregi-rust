"""Package only saved component evidence; execute no numerical programs."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path.cwd()
HERE = ROOT / "target/temporal-sixpoint-oracle"
OUTPUT = ROOT / "validation/temporal-sixpoint-oracle/q0-sixth-001"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    result_path = HERE / "quadrature001/results.json"
    result = json.loads(result_path.read_text())
    review_path = HERE / "quadrature001/result-review.json"
    review = json.loads(review_path.read_text())
    assert review["status"] == "independent_saved_data_result_review_passed"
    assert sha(result_path.read_bytes()) == review["quadrature_result_sha256"]
    assert result["status"] == "estimated-converged" and result["guards_unchanged"] is True
    assert not OUTPUT.exists(), "Preserve existing durable capsule"
    protocol = json.loads((HERE / "protocol.json").read_text())
    for name, expected in protocol["bindings_sha256"].items():
        assert sha((ROOT / name).read_bytes()) == expected, "Bound saved input changed"
    paths = {p for p in HERE.rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".md", ".log", ".dot")}
    for name in protocol["bindings_sha256"]:
        path = ROOT / name
        if path.suffix in (".py", ".rs", ".json", ".md", ".log", ".dot"):
            paths.add(path)
    stream, members = io.BytesIO(), {}
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(paths):
            name, blob = str(path.relative_to(ROOT)), path.read_bytes()
            assert not blob.startswith((b"\x7fELF", b"!<arch>\n")), "Compiled assets prohibited"
            item = tarfile.TarInfo(name)
            item.size, item.mode, item.mtime = len(blob), 0o644, 0
            archive.addfile(item, io.BytesIO(blob))
            members[name] = sha(blob)
    OUTPUT.mkdir(parents=True)
    packed = gzip.compress(stream.getvalue(), compresslevel=9, mtime=0)
    (OUTPUT / "artifacts.tar.gz").write_bytes(packed)
    summary = {"status": "component-only-estimated-quadrature-agreement", "moment_index": 126,
        "monomial": [6, 0, 0, 0], "requested_array_rank": 7, "numerator_degree": 6,
        "selected_native_finite": result["selected_native_finite"],
        "estimated_uncertainty_native": result["estimated_uncertainty_native"],
        "estimated_uncertainty_dimensionally_normalized": result["estimated_uncertainty_dimensionally_normalized"],
        "normalization_unit": "1/4", "configurations": 6, "points": 8994816,
        "comparisons": result["comparisons"], "order_changes_native": result["order_changes_native"],
        "final_mapping_difference_native": result["final_mapping_difference_native"],
        "native_rejected_original_pv_retained": True, "original_full_array_gate": "failed-unchanged",
        "historical_eight_test_status_failure": "preserved; exactSuccess adapter correction independently reviewed before fresh granted run",
        "uncertainty_kind": "Empirical fixed-order/mapping and roundoff estimate; not an interval-certified bound",
        "scope": "One synthetic massive N6 base component126 only; no other 329 moments, full array, causal, physical or performance qualification"}
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (OUTPUT / "README.md").write_text("""# Conditioned N6 temporal sixth moment

The six independently parameterized SciPy Jacobi rule evaluations give native
finite `(0, -0.05166894942216114)` for raw `q0^6`, zero-based component126 of the
rank-seven array. The numerator degree is six. The estimated absolute native
uncertainty is `7.780455047365738e-16`, or `3.1121820189462953e-15` after dividing
by the dimensional unit `U=1/4`. These empirical order/mapping and roundoff
estimates are **nonrigorous**; no interval certificate is claimed.

| Candidate / reference operand | Mixed error plus estimated uncertainty |
| --- | ---: |
| TIRust PV Float128 / independent oracle | 3.248856945702998e-15 |
| Original IREGI IBP / independent oracle | 4.273454476687555e-10 |
| Original IREGI Hybrid / independent oracle | 4.266824937506172e-10 |
| Original IREGI PV / independent oracle | native-rejected diagnostic |

The strict `1e-10` gate is unchanged. The original 330-moment/1320-complex-slot
array comparison remains failed. This component favors the saved TIRust value
against the original reference; it does not establish a cause or qualify the
other 329 moments, physical graphs, precision convergence, or performance. The
separate original-reference comparator argument order and denominator are also
preserved in `summary.json`; they are not silently exchanged with the oracle.

Symbolica performs the shifted-numerator binomial expansion, Gaussian-kernel
coefficient multiplication/extraction, and an exact-zero identity check in
exactly three CLI calls. SciPy supplies the existing Jacobi rules at orders
12/16/20 for identity/reversed simplex coordinates, totaling 8,994,816 nodes.
The reversed map changes only integration coordinates, not physical routing.
`Gamma(6)` is already in the Gaussian coefficients; the weights supply simplex
volume 1/120. The recorded positive-F bound is 15/16, so poles vanish and native
finite normalization is `i*pi^2` times the real OneLoop simplex integral.

The artifact archive retains exact final sources, root/peer reviews, both
unexecuted source drafts, the initial failed eight-test run, its exactSuccess
schema diagnosis, the freshly granted corrected eight-test pass, all three
Symbolica DOT/stdout/stderr tables and zero witness, all six numerical rule
outputs and statistics, saved raw native operands, and process/guard receipts.
All owned groups are gone. No compiled libraries, executables, Python bytecode,
license contents, or performance measurements are packaged. Historical
readiness/failed labels are preserved unchanged as chronological evidence.

The existing CLI binary is hash-pinned. Contextual preparation sources in the
archive do not claim a newly source-matched CLI build. The saved original data
and failed whole-array comparison are retained with their original hashes.
Reproduction commands and phase-specific root review requirements are included
under `target/temporal-sixpoint-oracle/commands.json` inside the archive. Earlier
failures and current successes must remain separate when reproducing them.
""")
    shutil.copyfile(Path(__file__), OUTPUT / "package.py")
    qualification = {"kind": "temporal-sixth-independent-component-capsule",
        "status": "peer-reviewed-component-only-estimated-quadrature-agreement",
        "archive": {"path": str((OUTPUT / "artifacts.tar.gz").relative_to(ROOT)), "sha256": sha(packed),
            "uncompressed_sha256": sha(stream.getvalue()), "members_sha256": members},
        "source_result_sha256": sha(result_path.read_bytes()),
        "preparation_sha256": sha((HERE / "preparation002/preparation.json").read_bytes()),
        "peer_result_review_sha256": sha(review_path.read_bytes()),
        "root_quadrature_review_sha256": sha((HERE / "root-oracle-review.json").read_bytes()),
        "corrected_tests_receipt_sha256": sha((HERE / "saved-data-tests002/receipt.json").read_bytes()),
        "retained_initial_failed_tests_sha256": sha((HERE / "saved-data-tests001/receipt.json").read_bytes()),
        "files_sha256": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(OUTPUT.iterdir()) if p.is_file()},
        "component_index": 126, "configuration_count": 6, "points": 8994816,
        "original_full_array_gate": "failed-unchanged", "interval_certificate": False,
        "full_array_qualification": False, "causal_claim": False, "performance_evidence": False,
        "compiled_assets_packaged": False}
    (OUTPUT / "qualification.json").write_text(json.dumps(qualification, indent=2) + "\n")
    print(json.dumps({"path": str((OUTPUT / "qualification.json").relative_to(ROOT)),
                      "sha256": sha((OUTPUT / "qualification.json").read_bytes()), "archive_members": len(members)}, indent=2))


if __name__ == "__main__":
    main()
