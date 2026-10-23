#!/usr/bin/env python3
"""Time an isolated MadLoop graph inside Fortran, excluding process transport.

Requires run.py's generated case and validation/reference/build.py's O3 objects.
The external HELAS wavefunctions are prepared once, before the timed regions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
import run as capture

ROOT = capture.ROOT
STAGES = {1: "numerator", 2: "numerator_assembly", 3: "reduction", 4: "total"}
ATTEMPT: dict = {}
ARTIFACT_PATHS: list[Path] = []


def write_artifacts(result: dict) -> None:
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    for path in ARTIFACT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(text)
        temporary.replace(path)


def environment(cpu: int | None) -> dict:
    result = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  platform=platform.platform(), python=sys.version.split()[0])
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        match = re.search(r"(?m)^model name\s*:\s*(.*)$", cpuinfo.read_text())
        result["cpu_model"] = match[1] if match else None
    if cpu is not None:
        folder = Path(f"/sys/devices/system/cpu/cpu{cpu}/cpufreq")
        for name in ["scaling_governor", "scaling_cur_freq", "cpuinfo_max_freq", "cpuinfo_min_freq"]:
            path = folder / name
            result[name] = path.read_text().strip() if path.exists() else None
    return result


def statements(text: str) -> list[str]:
    result: list[str] = []
    for line in text.splitlines():
        if not line or line[0] in "cC*!":
            continue
        if len(line) > 5 and line[5] not in " 0":
            result[-1] += line[6:].strip()
        else:
            result.append(line[6:].strip())
    return result


def selected_assembly(process: Path, prefix: str, group: int) -> tuple[str, list[str]]:
    """Replay existing generated calls and their parent DAG, without algebra."""
    calls: dict[int, tuple[int, list[str]]] = {}
    selected = None
    for path in sorted(process.glob("coef_construction_*.f")):
        code = statements(capture.original(path))
        for index, line in enumerate(code):
            match = re.fullmatch(
                r"CALL (\w+)\(PL\(0,(\d+)\),W\((\d+)\),([^,]+),([^,]+),([^,]+),PL\(0,(\d+)\),COEFS\)",
                line)
            if match:
                parent, child = int(match[2]), int(match[7])
                update = code[index + 1]
                if not update.startswith(f"CALL {prefix}UPDATE_WL_"):
                    raise RuntimeError("generated vertex is missing its wavefunction update")
                calls[child] = parent, [line, update]
            match = re.fullmatch(
                rf"CALL {prefix}CREATE_LOOP_COEFS\(WL\(1,0,1,(\d+)\),(\d+),(\d+),(\d+),.*\)", line)
            if match and int(match[4]) == group:
                if selected is not None:
                    raise RuntimeError("selected coefficient group combines multiple diagrams")
                selected = int(match[1]), line
    if selected is None:
        raise RuntimeError("selected graph has no coefficient construction")
    node, final = selected
    chain = []
    while node:
        node, vertex = calls[node]
        chain.append(vertex)
    body = [call for vertex in reversed(chain) for call in vertex] + [final]
    first = capture.original(process / "coef_construction_1.f")
    # Keep the original USE/INCLUDE/type/common declarations and array extents.
    declarations = first[:first.index("C     ----------")]
    declarations = re.sub(r"SUBROUTINE \w+\(P,NHEL,H,IC\)",
                          f"SUBROUTINE {prefix}AUDIT_ASSEMBLE()", declarations, count=1)
    source = declarations + f"""      COMPLEX*16 LOOPCOEFS(0:LOOPMAXCOEFS-1,NLOOPGROUPS)
      COMMON/{prefix}LCOEFS/LOOPCOEFS
C     Replay one exact generated diagram with external wavefunctions fixed.
      LOOPCOEFS(:,{group})=(0D0,0D0)
""" + "\n".join("      " + line for line in body) + "\n      END\n"
    if any(len(line) > 132 for line in source.splitlines()):
        raise RuntimeError("generated audit source needs fixed-form line wrapping")
    return source, body


def timer_source(prefix: str, group: int, args: argparse.Namespace) -> str:
    widths = ",".join(map(str, args.batch_widths))
    return f"""
      SUBROUTINE {prefix}AUDIT_BENCH(N,RANK,NC,PDEN,M2L,MU,
     $ CTMODE,IMODE,EXPECTED_TENSORS,EXPECTED_RESULT)
      USE, INTRINSIC :: IEEE_ARITHMETIC
      IMPLICIT NONE
      INCLUDE 'loop_max_coefs.inc'
      INTEGER N,RANK,NC,CTMODE,IMODE,I,J,L,B,REP,STAGE,IB,IT
      INTEGER ITERATIONS,WIDTHS({len(args.batch_widths)})
      INTEGER*8 T0,T1,RATE
      DATA WIDTHS /{widths}/
      DOUBLE PRECISION PDEN(0:3,N-1),MU,ELAPSED,NS,ERR,DIFF
      COMPLEX*16 M2L(N),EXPECTED_TENSORS(0:LOOPMAXCOEFS-1,3)
      COMPLEX*16 EXPECTED_RESULT(3),PJ(0:LOOPMAXCOEFS-1,3)
      COMPLEX*16 TT(0:LOOPMAXCOEFS-1,3),ANSWER(3),Q(0:3),VALUE
      COMPLEX*16 SAVED(0:LOOPMAXCOEFS-1),SINK
      INTEGER NLOOPGROUPS
      PARAMETER (NLOOPGROUPS={args.n_groups})
      COMPLEX*16 LOOPCOEFS(0:LOOPMAXCOEFS-1,NLOOPGROUPS)
      COMMON/{prefix}LCOEFS/LOOPCOEFS
      LOGICAL STABLE,DONE
      SAVE DONE
      DATA DONE /.FALSE./
      IF(DONE) RETURN
      DONE=.TRUE.
      SAVED=LOOPCOEFS(:,{group})
      Q=(/DCMPLX(2D0,0.25D0),DCMPLX(-3D0,0.125D0),
     $ DCMPLX(5D0,-0.5D0),DCMPLX(7D0,0.75D0)/)
      SINK=(0D0,0D0)
      ERR=0D0
C     Match the original-reference policy: recycle inside each sample only.
      CALL IREGI_FREE_PS()
      CALL INITIREGI(.TRUE.,2,1D-6)
      CALL {prefix}AUDIT_ASSEMBLE()
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(SAVED(0:NC-1))))) STOP 20
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(SAVED(0:NC-1))))) STOP 20
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(LOOPCOEFS(0:NC-1,{group})))))
     $ STOP 21
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(LOOPCOEFS(0:NC-1,{group})))))
     $ STOP 21
      DO J=0,NC-1
        DIFF=ABS(LOOPCOEFS(J,{group})-SAVED(J))/(1D0+ABS(SAVED(J)))
        ERR=MAX(ERR,DIFF)
      ENDDO
      CALL IMLOOP(CTMODE,IMODE,N,LOOPMAXCOEFS,RANK,PDEN,M2L,
     $ MU,PJ,STABLE)
      IF(.NOT.STABLE) STOP 11
      CALL {prefix}CONVERT_IREGI_COEFFS(RANK,PJ,TT)
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(TT(0:NC-1,:))))) STOP 22
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(TT(0:NC-1,:))))) STOP 22
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(EXPECTED_TENSORS(0:NC-1,:)))))
     $ STOP 23
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(EXPECTED_TENSORS(0:NC-1,:)))))
     $ STOP 23
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(EXPECTED_RESULT)))) STOP 24
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(EXPECTED_RESULT)))) STOP 24
      DO I=1,3
        ANSWER(I)=(0D0,0D0)
        DO J=0,NC-1
          DIFF=ABS(TT(J,I)-EXPECTED_TENSORS(J,I))
     $      /(1D0+ABS(EXPECTED_TENSORS(J,I)))
          ERR=MAX(ERR,DIFF)
          ANSWER(I)=ANSWER(I)+LOOPCOEFS(J,{group})*TT(J,I)
        ENDDO
        DIFF=ABS(ANSWER(I)-EXPECTED_RESULT(I))
     $    /(1D0+ABS(EXPECTED_RESULT(I)))
        ERR=MAX(ERR,DIFF)
      ENDDO
      IF(.NOT.ALL(IEEE_IS_FINITE(DBLE(ANSWER)))) STOP 25
      IF(.NOT.ALL(IEEE_IS_FINITE(DIMAG(ANSWER)))) STOP 25
      CALL IREGI_FREE_PS()
      WRITE(*,'(A,ES26.17E3)') 'IREGI_BENCH_CHECK ',ERR
      IF(ERR.GT.1D-10.OR.ERR.NE.ERR) STOP 12
      CALL SYSTEM_CLOCK(COUNT_RATE=RATE)
      IF(RATE.LE.0) STOP 13
      WRITE(*,*) 'IREGI_BENCH_CLOCK',RATE
      DO IB=1,{len(args.batch_widths)}
        B=WIDTHS(IB)
        DO STAGE=1,4
C         Pilot doubling sets a block duration; no pilot enters statistics.
          ITERATIONS=1
          DO
            CALL SYSTEM_CLOCK(T0)
            DO IT=1,ITERATIONS
              DO L=1,B
                CALL {prefix}AUDIT_STEP(STAGE,N,RANK,NC,PDEN,
     $            M2L,MU,CTMODE,IMODE,Q,SINK)
              ENDDO
            ENDDO
            CALL SYSTEM_CLOCK(T1)
            ELAPSED=DBLE(T1-T0)/DBLE(RATE)
            IF(ELAPSED.GE.{args.target_ms / 1000:.12f}D0) EXIT
            IF(ITERATIONS.GE.1048576) EXIT
            ITERATIONS=2*ITERATIONS
          ENDDO
          DO REP=1,{args.warmup + args.repeats}
            CALL SYSTEM_CLOCK(T0)
            DO IT=1,ITERATIONS
              DO L=1,B
                CALL {prefix}AUDIT_STEP(STAGE,N,RANK,NC,PDEN,
     $            M2L,MU,CTMODE,IMODE,Q,SINK)
              ENDDO
            ENDDO
            CALL SYSTEM_CLOCK(T1)
            NS=DBLE(T1-T0)*1D9/DBLE(RATE)/DBLE(ITERATIONS)
            IF(REP.GT.{args.warmup}) WRITE(*,'(A,4I12,ES26.17E3)')
     $        'IREGI_BENCH_SAMPLE ',B,STAGE,REP-{args.warmup},
     $        ITERATIONS,NS
          ENDDO
        ENDDO
      ENDDO
      IF(.NOT.IEEE_IS_FINITE(DBLE(SINK))) STOP 26
      IF(.NOT.IEEE_IS_FINITE(DIMAG(SINK))) STOP 26
      WRITE(*,'(A,2ES26.17E3)') 'IREGI_BENCH_SINK ',
     $ DBLE(SINK),DIMAG(SINK)
      LOOPCOEFS(:,{group})=SAVED
      END

      SUBROUTINE {prefix}AUDIT_STEP(STAGE,N,RANK,NC,PDEN,
     $ M2L,MU,CTMODE,IMODE,Q,SINK)
      IMPLICIT NONE
      INCLUDE 'loop_max_coefs.inc'
      INTEGER STAGE,N,RANK,NC,CTMODE,IMODE,I,J
      INTEGER NLOOPGROUPS
      PARAMETER (NLOOPGROUPS={args.n_groups})
      DOUBLE PRECISION PDEN(0:3,N-1),MU
      COMPLEX*16 M2L(N),Q(0:3),SINK,VALUE,ANSWER(3)
      COMPLEX*16 PJ(0:LOOPMAXCOEFS-1,3),TT(0:LOOPMAXCOEFS-1,3)
      COMPLEX*16 LOOPCOEFS(0:LOOPMAXCOEFS-1,NLOOPGROUPS)
      COMMON/{prefix}LCOEFS/LOOPCOEFS
      LOGICAL STABLE
      IF(STAGE.EQ.1) THEN
        CALL {prefix}EVAL_POLY(LOOPCOEFS(0,{group}),RANK,Q,VALUE)
        SINK=SINK+VALUE
        RETURN
      ENDIF
      IF(STAGE.EQ.2.OR.STAGE.EQ.4) THEN
        CALL {prefix}AUDIT_ASSEMBLE()
        SINK=SINK+LOOPCOEFS(0,{group})
      ENDIF
      IF(STAGE.EQ.3.OR.STAGE.EQ.4) THEN
        CALL IMLOOP(CTMODE,IMODE,N,LOOPMAXCOEFS,RANK,PDEN,M2L,
     $    MU,PJ,STABLE)
        IF(.NOT.STABLE) STOP 14
        CALL {prefix}CONVERT_IREGI_COEFFS(RANK,PJ,TT)
        DO I=1,3
          ANSWER(I)=(0D0,0D0)
          DO J=0,NC-1
            ANSWER(I)=ANSWER(I)+LOOPCOEFS(J,{group})*TT(J,I)
          ENDDO
        ENDDO
        SINK=SINK+SUM(ANSWER)
        CALL IREGI_FREE_PS()
      ENDIF
      END
"""


def optimized_reference_library(folder: Path) -> Path:
    spec = importlib.util.spec_from_file_location("reference_build", ROOT / "validation/reference/build.py")
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    objects = ROOT / "target/reference/objects"
    names = [*reference.MODULES, "avh_olo_foriregi"]
    paths = [objects / f"{name}.o" for name in names]
    paths += sorted(objects.glob("ff_*.o")) + sorted(objects.glob("ql_*.o"))
    if not all(p.exists() for p in paths) or not (ROOT / "target/reference/provenance.json").exists():
        raise RuntimeError("run python3 validation/reference/build.py first")
    library = folder / "libiregi-benchmark.a"
    if library.exists():
        library.unlink()
    capture.run(["ar", "rcs", str(library), *map(str, paths)], folder / "archive.log")
    return library


def main() -> None:
    global ATTEMPT, ARTIFACT_PATHS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=list(capture.CASES), default="ggh")
    parser.add_argument("--helicity", type=int, default=1)
    parser.add_argument("--cpu", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=21)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--target-ms", type=float, default=30)
    parser.add_argument("--batch-widths", type=int, nargs="+", default=[1, 32])
    args = parser.parse_args()
    if Path.cwd().resolve() != ROOT:
        parser.error(f"run from {ROOT}")
    if (min([args.repeats, args.warmup + 1, *args.batch_widths]) < 1
            or not math.isfinite(args.target_ms) or args.target_ms <= 0):
        parser.error("counts, batch widths, and target milliseconds must be positive")
    if len(set(args.batch_widths)) != len(args.batch_widths):
        parser.error("batch widths must be distinct")
    if not 1 <= args.helicity <= capture.CASES[args.case]["helicities"]:
        parser.error("helicity index is outside the selected case")
    if args.cpu is not None and args.cpu not in os.sched_getaffinity(0):
        parser.error("requested CPU is outside the available affinity mask")
    capture.CASE_NAME = args.case
    capture.CASE = capture.CASES[args.case]
    capture.OUTPUT = capture.WORK / args.case
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    capture.LOGS = capture.WORK / "logs" / args.case / "benchmark" / timestamp
    capture.LOGS.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATHS = [capture.WORK / "benchmarks" / args.case / f"{timestamp}.json",
                      capture.WORK / f"{args.case}-benchmark.json"]
    ATTEMPT = dict(schema_version=1, case=args.case, attempt_id=timestamp,
                   timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   requested_options=vars(args).copy(), log_directory=str(capture.LOGS),
                   script_sha256=capture.sha256(Path(__file__)))
    write_artifacts(dict(ATTEMPT, status="running", measurement_status="pending"))
    processes = list(capture.OUTPUT.glob("SubProcesses/P*"))
    if len(processes) != 1:
        raise RuntimeError("generate the case with run.py first")
    process = processes[0]
    prefix = capture.instrument(process)
    capture.driver(process, prefix, args.helicity)
    mapping = capture.graph_map(process, prefix)
    selected = [g for g in mapping if g["external_vertex_order"] == list(range(1, capture.CASE["nexternal"] + 1))
                and all("L1_2" in v for v in g["vertex_calls"])]
    if len(selected) != 1:
        raise RuntimeError("could not isolate an oriented graph")
    graph = selected[0]
    group = graph["group"]
    args.n_groups = len(mapping)
    assembly, calls = selected_assembly(process, prefix, group)
    coefficients = process / "coef_construction_1.f"
    coefficients.write_text(coefficients.read_text() + assembly)
    tir = process / "TIR_interface.f"
    source = capture.replace_once(tir.read_text(), "      WRITE(*,*) 'IREGI_AUDIT_END'\n",
        f"""      WRITE(*,*) 'IREGI_AUDIT_END'
      IF(I_LOOPGROUP.EQ.{group}) CALL {prefix}AUDIT_BENCH(
     $ NLOOPLINE,RANK,NLOOPCOEFS,PDEN,M2L,MU_R,CTMODE,IREGIMODE,
     $ TIRCOEFS,RES)
""")
    tir.write_text(source + timer_source(prefix, group, args))
    library = optimized_reference_library(capture.LOGS)
    flags = "-O3 -w -fPIC -ffixed-line-length-132"
    includes = f" -I{capture.OUTPUT / 'Source/MODEL'} -I{capture.OUTPUT / 'Source/DHELAS'}"
    # Rebuild every generated numerical HELAS routine and process object using
    # the same optimization level. Reference objects are independently O3.
    make = ["make", f"SHELL={shutil.which('bash')}", f"FFLAGS={flags + includes}"]
    for subdir in ["Source/MODEL", "Source/DHELAS"]:
        capture.run([*make, "-C", str(capture.OUTPUT / subdir), "-B", "-j2"],
                    capture.LOGS / (subdir.split("/")[-1] + "-build.log"))
    # Include paths must be explicit because command-line FFLAGS override +=.
    process_flags = flags + includes
    capture.run(["make", "-C", str(process), f"SHELL={shutil.which('bash')}",
                 f"FFLAGS={process_flags}", f"LINK_LOOP_LIBS=-L{capture.OUTPUT / 'lib'} -lcts {library}",
                 "-B", "-j2", "check"], capture.LOGS / "process-build.log")
    command = [str(process / "check")]
    if args.cpu is not None:
        command = ["taskset", "-c", str(args.cpu), *command]
    log = capture.LOGS / "evaluation.log"
    before = environment(args.cpu)
    capture.run(command, log)
    after = environment(args.cpu)
    records, metadata = capture.parse(log)
    samples: dict[int, dict] = {}
    error = None
    rate = None
    for line in log.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "IREGI_BENCH_CHECK":
            error = float(fields[1])
        elif fields[0] == "IREGI_BENCH_CLOCK":
            rate = int(fields[1])
        elif fields[0] == "IREGI_BENCH_SAMPLE":
            width, stage, repeat, iterations = map(int, fields[1:5])
            entry = samples.setdefault(width, {}).setdefault(STAGES[stage],
                dict(samples_ns=[], iterations_per_block=iterations, unit="ns/batch"))
            if repeat != len(entry["samples_ns"]) + 1:
                raise RuntimeError("missing or duplicate timed block")
            elapsed_ns = float(fields[5])
            if not math.isfinite(elapsed_ns) or elapsed_ns <= 0:
                raise RuntimeError("nonfinite or nonpositive timed interval")
            entry["samples_ns"].append(elapsed_ns)
    if (error is None or not math.isfinite(error) or error > 1e-10
            or rate is None or rate <= 0 or len(samples) != len(args.batch_widths)):
        raise RuntimeError("incomplete timer output")
    for stages in samples.values():
        if set(stages) != set(STAGES.values()) or any(len(s["samples_ns"]) != args.repeats for s in stages.values()):
            raise RuntimeError("incomplete repeated measurements")
        stages.update(preparation=None, masters=None)
    selected_record = next(r for r in records if r["group"] == group)
    fixture = ROOT / f"validation/physical/madloop/fixtures/{args.case}-helicity-{args.helicity}.json"
    fixture_error = None
    if fixture.exists():
        saved = json.loads(fixture.read_text())
        expected = next(r for r in saved["records"] if r["group"] == group)
        def number(pair):
            value = complex(*map(float, pair))
            if not math.isfinite(value.real) or not math.isfinite(value.imag):
                raise RuntimeError("nonfinite optimized or committed reference result")
            return value
        pairs = list(zip(selected_record["numerator"], expected["numerator"], strict=True))
        pairs += [(a["value"], b["value"]) for a, b in
                  zip(selected_record["tensors"], expected["tensors"], strict=True)]
        pairs += list(zip(selected_record["raw_result"], expected["raw_result"], strict=True))
        fixture_error = max(abs(number(a) - number(b)) / (1 + abs(number(b))) for a, b in pairs)
        if not math.isfinite(fixture_error) or fixture_error > 1e-10:
            raise RuntimeError(f"optimized reference differs from committed capture: {fixture_error}")
    result = dict(ATTEMPT, status="measured", precision="binary64", mode="Hybrid",
        helicity_index=args.helicity, graph=graph, rank=graph["rank"], n=capture.CASE["nloop"],
        mass_class="massive" if capture.CASE["pdg"] == 6 else "massless",
        reference="MadLoop generated HELAS and original IREGI O3",
        cpu_affinity=[args.cpu] if args.cpu is not None else sorted(os.sched_getaffinity(0)),
        environment_before=before, environment_after=after,
        warmup_blocks=args.warmup, repeats=args.repeats, target_block_ms=args.target_ms,
        clock="Fortran SYSTEM_CLOCK(integer*8)", clock_rate=rate,
        cache_policy="RECYCLING=true within sample; IREGI_FREE_PS after each sample inside timer",
        input_policy="original MadLoop INITIREGI: legacy on-shell snapping enabled, threshold 1e-6",
        phase_space_policy="MadLoop ImprovePSPoint=2 before timing; use metadata.evaluated_external_momenta",
        external_wavefunctions="precomputed HELAS; excluded from all stages",
        stage_definitions={"numerator": "original EVAL_POLY at the fixture complex probe",
            "numerator_assembly": "selected generated HELAS vertex/update/merge DAG; external wavefunctions fixed",
            "reduction": "IMLOOP, Laurent/tensor ordering conversion, contraction, numerical cache cleanup; includes masters",
            "total": "numerator_assembly plus reduction; excludes EVAL_POLY and symbolic preparation",
            "preparation": None, "masters": None},
        measurement_status="pinned" if args.cpu is not None else "unqualified_unpinned",
        correctness=dict(status="passed", max_error=error,
            committed_fixture_max_error=fixture_error,
            scope="reference replay only: coefficients, every tensor coefficient, contracted Laurent output; Rust agreement is a separate gate"),
        samples={str(k): v for k, v in samples.items()}, metadata=metadata,
        reference_record=selected_record,
        generated_calls=calls, flags=flags,
        provenance=dict(script_sha256=capture.sha256(Path(__file__)),
            capture_script_sha256=capture.sha256(Path(capture.__file__)),
            executable_sha256=capture.sha256(process / "check"),
            compiler=subprocess.check_output([os.environ.get("FC", "gfortran"), "--version"],
                cwd=ROOT, text=True).splitlines()[0],
            reference_build=json.loads((ROOT / "target/reference/provenance.json").read_text()),
            generated_sources={str(p.relative_to(capture.OUTPUT)): capture.sha256(p)
                for p in [tir, coefficients, process / "polynomial.f"]},
            linked_archives={str(p.relative_to(capture.OUTPUT)): capture.sha256(p)
                for p in [capture.OUTPUT / "lib/libmodel.a", capture.OUTPUT / "lib/libdhelas.a",
                          capture.OUTPUT / "lib/libcts.a"]},
            parameters_sha256=capture.sha256(capture.OUTPUT / "Cards/param_card.dat"),
            reduction_card_sha256=capture.sha256(capture.OUTPUT / "SubProcesses/MadLoop5_resources/MadLoopParams.dat"),
            fixture_sha256=capture.sha256(fixture) if fixture.exists() else None,
            library_sha256=capture.sha256(library)))
    write_artifacts(result)
    print(ARTIFACT_PATHS[-1])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if ATTEMPT:
            write_artifacts(dict(ATTEMPT, status="failed", measurement_status="failed",
                failed_at_utc=datetime.now(timezone.utc).isoformat(),
                error=f"{type(exc).__name__}: {exc}"))
        raise
