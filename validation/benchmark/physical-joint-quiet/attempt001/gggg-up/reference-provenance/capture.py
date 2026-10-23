#!/usr/bin/env python3
"""Generate and export graph-isolated MadLoop reduction inputs.

This is optional reference tooling. All generated sources and binaries are kept
under target/physical; no reference checkout is modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "target/physical"
MG = WORK / "madgraph"
OUTPUT = WORK / "ggh"
SOURCE = ROOT.parent / "references/madgraph"
CASES = {
    "ggh": dict(process="g g > h [sqrvirt=QCD]", nloop=3, pdg=6,
                nexternal=3, gluons=2, helicities=4),
    "gghh": dict(process="g g > h h [sqrvirt=QCD]", nloop=4, pdg=6,
                 nexternal=4, gluons=2, helicities=4),
    "gghhh": dict(process="g g > h h h [sqrvirt=QCD]", nloop=5, pdg=6,
                  nexternal=5, gluons=2, helicities=4),
    "gggg-up": dict(process="g g > g g [sqrvirt=QCD]", nloop=4, pdg=2,
                    nexternal=4, gluons=4, helicities=16),
}
CASE_NAME = "ggh"
CASE = CASES[CASE_NAME]
LOGS = WORK / "logs" / CASE_NAME


def run(args: list[str], log: Path) -> None:
    generated_logs = {p: p.exists() for p in [ROOT / "MG5_debug", ROOT / "param.log"]}
    try:
        with log.open("w") as stream:
            subprocess.run(args, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                           check=True)
    finally:
        for path, existed in generated_logs.items():
            if not existed and path.exists():
                path.replace(LOGS / f"{log.stem}-{path.name}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    if not MG.exists():
        subprocess.run(["cp", "-a", "--reflink=auto", str(SOURCE), str(MG)],
                       cwd=ROOT, check=True)
    # MadGraph's -f overwrites files but leaves stale Born sources when changing
    # from interference to squared-loop mode. This directory is build output.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    # Explicitly forbid denominator grouping in the isolated reference copy.
    exporter = MG / "madgraph/loop/loop_exporters.py"
    text = exporter.read_text()
    text = text.replace("    forbid_loop_grouping = False",
                        "    forbid_loop_grouping = True")
    exporter.write_text(text)
    command_file = WORK / f"generate-{CASE_NAME}.mg5"
    command_file.write_text("\n".join([
        "set automatic_html_opening False",
        "set notification_center False",
        "set loop_optimized_output True",
        "set loop_color_flows True",
        "set group_subprocesses False",
        "set ninja ''", "set collier ''", "set golem ''",
        "import model loop_sm",
        f"generate {CASE['process']} --loop_filter='n=={CASE['nloop']} and {CASE['pdg']} in loop_pdgs'",
        f"output standalone {OUTPUT} -f", "quit", "",
    ]))
    entrypoint = MG / "bin/madgraph"
    if not entrypoint.exists():
        entrypoint = MG / "bin/mg5_aMC"
    run([sys.executable, str(entrypoint), str(command_file)],
        LOGS / "generation.log")
    if not list(OUTPUT.glob("SubProcesses/P*/TIR_interface.f")):
        raise RuntimeError("MadGraph did not export TIR_interface.f; inspect generation.log")


def original(path: Path) -> str:
    backup = path.with_suffix(path.suffix + ".iregi-original")
    if not backup.exists():
        backup.write_bytes(path.read_bytes())
    return backup.read_text()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"reference source changed: expected one anchor {old!r}")
    return text.replace(old, new, 1)


def instrument(process: Path) -> str:
    tir = process / "TIR_interface.f"
    text = original(tir)
    prefix = re.search(r"SUBROUTINE (\w+)TIRLOOP", text).group(1)
    if "LOOPCOEFS(J,I_SQSO,I_LOOPGROUP)" in text:
        raise RuntimeError("this exporter requires amplitude-level loop-induced reduction")
    text = replace_once(text, "      INTEGER NLOOPCOEFS\n",
        "      INTEGER NLOOPCOEFS\n"
        "      COMPLEX*16 AUDIT_Q(0:3),AUDIT_VALUE\n")
    export = f"""C     IREGI audit: individual bare loop, before normalization or CT sum.
      WRITE(*,*) 'IREGI_AUDIT_BEGIN',I_LOOPGROUP,NLOOPLINE,RANK,
     $ CTMODE,STABLE
      WRITE(*,'(A,ES26.17E3)') 'IREGI_SCALE ',MU_R
      WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_SHIFT ',0,0D0,0D0,0D0,0D0
      DO J=1,NLOOPLINE-1
        WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_SHIFT ',J,
     $    (PDEN(I,J),I=0,3)
      ENDDO
      DO J=0,NLOOPLINE-1
        WRITE(*,'(A,I4,2ES26.17E3)') 'IREGI_MASS ',J,
     $    DBLE(M2L(J+1)),DIMAG(M2L(J+1))
      ENDDO
      DO J=0,NLOOPCOEFS-1
        WRITE(*,'(A,I4,2ES26.17E3)') 'IREGI_NUM ',J,
     $    DBLE(LOOPCOEFS(J,I_LOOPGROUP)),
     $    DIMAG(LOOPCOEFS(J,I_LOOPGROUP))
        DO I=1,3
          WRITE(*,'(A,2I4,2ES26.17E3)') 'IREGI_TENSOR ',J,I,
     $      DBLE(TIRCOEFS(J,I)),DIMAG(TIRCOEFS(J,I))
        ENDDO
      ENDDO
      DO I=1,3
        WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_RESULT ',I,
     $    DBLE(RES(I)),DIMAG(RES(I)),
     $    DBLE(NORMALIZATION*RES(I)),DIMAG(NORMALIZATION*RES(I))
      ENDDO
C     Use MadLoop's own polynomial evaluator for the pointwise reference.
      AUDIT_Q(0)=DCMPLX(2.0D0,0.25D0)
      AUDIT_Q(1)=DCMPLX(-3.0D0,0.125D0)
      AUDIT_Q(2)=DCMPLX(5.0D0,-0.5D0)
      AUDIT_Q(3)=DCMPLX(7.0D0,0.75D0)
      CALL {prefix}EVAL_POLY(LOOPCOEFS(0,I_LOOPGROUP),RANK,
     $ AUDIT_Q,AUDIT_VALUE)
      WRITE(*,'(A,2ES26.17E3)') 'IREGI_PROBE ',
     $ DBLE(AUDIT_VALUE),DIMAG(AUDIT_VALUE)
      WRITE(*,*) 'IREGI_AUDIT_END'
"""
    text = replace_once(text, "      RES(1)=NORMALIZATION*RES(1)\n",
                        export + "      RES(1)=NORMALIZATION*RES(1)\n")
    tir.write_text(text)
    wavefunctions = f"""C     IREGI audit: actual HELAS external polarization components.
      WRITE(*,*) 'IREGI_HELICITY',H,NHEL
C     MadLoop may project the requested phase-space point before HELAS.
C     All cases here have two incoming particles. HELAS stores their
C     momenta with the opposite sign, and outgoing momenta with + sign.
      DO I=1,{CASE['nexternal']}
        WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_SEAM_EXTERNAL ',I,
     $    (P(J,I),J=0,3)
        IF(I.LE.2) THEN
          WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_EVALUATED_EXTERNAL ',I,
     $      (-DBLE(W(I)%P(J)),J=0,3)
        ELSE
          WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_EVALUATED_EXTERNAL ',I,
     $      (DBLE(W(I)%P(J)),J=0,3)
        ENDIF
        DO J=0,3
          WRITE(*,'(A,2I4,2ES26.17E3)') 'IREGI_WAVEFUNCTION_P ',I,J,
     $      DBLE(W(I)%P(J)),DIMAG(W(I)%P(J))
        ENDDO
      ENDDO
      DO I=1,{CASE['gluons']}
        DO J=1,4
          WRITE(*,'(A,2I4,2ES26.17E3)') 'IREGI_WAVEFUNCTION ',I,J,
     $      DBLE(W(I)%W(J)),DIMAG(W(I)%W(J))
        ENDDO
      ENDDO
"""
    coefficients = process / "coef_construction_1.f"
    text = original(coefficients)
    first_diagram = re.search(r"^C     Coefficient construction for loop diagram with ID \d+\n",
                             text, re.MULTILINE)
    if first_diagram is None:
        raise RuntimeError("could not identify first loop coefficient construction")
    text = replace_once(text, first_diagram[0], wavefunctions + first_diagram[0])
    coefficients.write_text(text)
    # Zero every CT amplitude in both precisions, retaining external HELAS
    # wavefunctions. Loop amplitudes occupy slots above NCTAMPS.
    for helas in process.glob("*helas_calls_ampb_*.f"):
        text = original(helas)
        text = replace_once(text, " 1001 CONTINUE\n",
            " 1001 CONTINUE\n      AMPL(:,1:NCTAMPS)=0\n")
        helas.write_text(text)
    return prefix


def driver(process: Path, prefix: str, helicity: int) -> None:
    resource = OUTPUT / "SubProcesses/MadLoop5_resources"
    if CASE_NAME == "ggh":
        kinematics = """      E=MDL_MH/2D0
      P(0,3)=MDL_MH
"""
    elif CASE_NAME == "gghh":
        kinematics = """      E=300D0
      K=DSQRT(E**2-MDL_MH**2)
      P(:,3)=(/E,0.8D0*K,0D0,0.6D0*K/)
      P(:,4)=(/E,-0.8D0*K,0D0,-0.6D0*K/)
"""
    elif CASE_NAME == "gghhh":
        kinematics = """      E=375D0
      K=DSQRT(250D0**2-MDL_MH**2)
      P(:,3)=(/250D0,K,0D0,0D0/)
      P(:,4)=(/250D0,-K/2D0,DSQRT(3D0)*K/2D0,0D0/)
      P(:,5)=(/250D0,-K/2D0,-DSQRT(3D0)*K/2D0,0D0/)
"""
    else:
        kinematics = """      E=200D0
      P(:,3)=(/E,0.8D0*E,0D0,0.6D0*E/)
      P(:,4)=(/E,-0.8D0*E,0D0,-0.6D0*E/)
"""
    coupling_export = """      WRITE(*,'(A,2ES26.17E3)') 'IREGI_COUPLINGS ',
     $ DBLE(GC_5),DIMAG(GC_5)
"""
    if CASE["pdg"] == 6:
        coupling_export = """      WRITE(*,'(A,4ES26.17E3)') 'IREGI_COUPLINGS ',
     $ DBLE(GC_5),DIMAG(GC_5),DBLE(GC_37),DIMAG(GC_37)
"""
    (process / "check_sa.f").write_text(f"""      PROGRAM IREGI_GRAPH_EXPORT
      IMPLICIT NONE
      INCLUDE 'coupl.inc'
      DOUBLE PRECISION P(0:3,{CASE['nexternal']}),E,K
      DOUBLE PRECISION,ALLOCATABLE :: ANS(:,:),PREC(:)
      INTEGER NDIM,NSQ,RET,I
      CHARACTER*512 RESOURCEPATH
      CALL {prefix}GET_ANSWER_DIMENSION(NDIM)
      CALL {prefix}GET_NSQSO_LOOP(NSQ)
      ALLOCATE(ANS(0:3,0:NDIM),PREC(0:NSQ))
      CALL SETPARAMLOG(.FALSE.)
      CALL SETPARA('{OUTPUT}/Cards/param_card.dat')
      RESOURCEPATH='{resource}'
      CALL SETMADLOOPPATH(RESOURCEPATH)
      CALL SET_FORBID_HEL_DOUBLECHECK(.TRUE.)
      P=0D0
{kinematics}      P(0,1)=E
      P(3,1)=E
      P(0,2)=E
      P(3,2)=-E
      MU_R=2D0*E
      CALL UPDATE_AS_PARAM(1)
      WRITE(*,'(A,3ES26.17E3)') 'IREGI_PARAMETERS ',MDL_MT,MDL_MH,G
{coupling_export}      DO I=1,{CASE['nexternal']}
        WRITE(*,'(A,I4,4ES26.17E3)') 'IREGI_EXTERNAL ',I,P(:,I)
      ENDDO
      CALL {prefix}SLOOPMATRIXHEL_THRES(P,{helicity},ANS,-1D0,PREC,RET)
      WRITE(*,*) 'IREGI_RETURN_CODE',RET
      END
""")
    # Resolve every include and resource from the generated checkout. The
    # executable itself runs with cwd=ROOT and writes only under target.
    card = resource / "MadLoopParams.dat"
    text = card.read_text()
    for name, value in {"MLReductionLib": "3", "CTModeRun": "1",
                        "IREGIMODE": "2", "IREGIRECY": ".TRUE.",
                        "CTLoopLibrary": "2",
                        "ImprovePSPoint": "2",
                        "HelicityFilterLevel": "0", "WriteOutFilters": ".FALSE.",
                        "DoubleCheckHelicityFilter": ".FALSE."}.items():
        text, count = re.subn(rf"(?m)^#{name}\n[^\n]*", f"#{name}\n{value}", text)
        if count != 1:
            raise RuntimeError(f"missing MadLoop card setting {name}")
    card.write_text(text)


def parse(log: Path) -> tuple[list[dict], dict]:
    records: list[dict] = []
    metadata: dict = {}
    record = None
    for line in log.read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        tag, *values = fields
        if tag == "IREGI_AUDIT_BEGIN":
            if record is not None:
                raise RuntimeError("nested export start")
            group, n, rank, mode = map(int, values[:4])
            record = dict(group=group, propagators=n, rank=rank, mode=mode,
                          stable=values[4] == "T", shifts=[], masses_squared=[],
                          numerator=[], tensors=[], raw_result=[], normalized_result=[])
        elif tag == "IREGI_AUDIT_END":
            if record is None:
                raise RuntimeError("unpaired export end")
            records.append(record)
            record = None
        elif tag in {"IREGI_PARAMETERS", "IREGI_COUPLINGS"}:
            metadata[tag.removeprefix("IREGI_").lower()] = values
        elif tag == "IREGI_EXTERNAL":
            metadata.setdefault("external_momenta", []).append(values[1:])
        elif tag in {"IREGI_EVALUATED_EXTERNAL", "IREGI_SEAM_EXTERNAL"}:
            name = ("evaluated_external_momenta" if tag == "IREGI_EVALUATED_EXTERNAL"
                    else "coefficient_construction_momenta")
            index = int(values[0]) - 1
            points = metadata.setdefault(name, [])
            if index == len(points):
                points.append(values[1:])
            elif index >= len(points) or points[index] != values[1:]:
                raise RuntimeError("multiple distinct or incomplete numerator working points")
        elif tag == "IREGI_WAVEFUNCTION_P":
            key = "_".join(values[:2])
            points = metadata.setdefault("wavefunction_momenta", {})
            if key in points and points[key] != values[2:]:
                raise RuntimeError("wavefunction momentum changed between coefficient calls")
            points[key] = values[2:]
        elif tag == "IREGI_RETURN_CODE":
            metadata["madloop_return_code"] = int(values[0])
        elif tag == "IREGI_HELICITY":
            metadata["helicity"] = list(map(int, values[1:]))
        elif tag == "IREGI_WAVEFUNCTION":
            metadata.setdefault("wavefunctions", {})["_".join(values[:2])] = values[2:]
        elif record is not None:
            if tag == "IREGI_SCALE":
                record["mu"] = values[0]
            elif tag == "IREGI_SHIFT":
                record["shifts"].append(values[1:])
            elif tag == "IREGI_MASS":
                record["masses_squared"].append(values[1:])
            elif tag == "IREGI_NUM":
                record["numerator"].append(values[1:])
            elif tag == "IREGI_TENSOR":
                record["tensors"].append(dict(coefficient=int(values[0]),
                    laurent_slot=int(values[1])-1, value=values[2:]))
            elif tag == "IREGI_RESULT":
                record["raw_result"].append(values[1:3])
                record["normalized_result"].append(values[3:5])
            elif tag == "IREGI_PROBE":
                record["probe_value"] = values
    if record is not None or not records:
        raise RuntimeError("missing or incomplete graph exports; inspect evaluation.log")
    if len(metadata.get("evaluated_external_momenta", [])) != CASE["nexternal"]:
        raise RuntimeError("missing evaluated external momenta at numerator seam")
    if metadata["evaluated_external_momenta"] != metadata.get("coefficient_construction_momenta"):
        # The sign mapping is independently checked against the generated
        # coefficient routine's physical-sign numerical momentum argument.
        for actual, argument in zip(metadata["evaluated_external_momenta"],
                                    metadata.get("coefficient_construction_momenta", []), strict=True):
            if list(map(float, actual)) != list(map(float, argument)):
                raise RuntimeError("HELAS and coefficient-construction momenta disagree")
    if len(metadata.get("wavefunction_momenta", {})) != 4*CASE["nexternal"]:
        raise RuntimeError("incomplete raw HELAS momentum export")
    if any(float(pair[1]) != 0 for pair in metadata["wavefunction_momenta"].values()):
        raise RuntimeError("unexpected complex external HELAS momentum")
    return records, metadata


def graph_map(process: Path, prefix: str) -> list[dict]:
    """Read the generated numerical wavefunction graph; do no symbolic algebra."""
    nodes: dict[int, dict] = {}
    graphs = []
    for path in sorted(process.glob("coef_construction_*.f")):
        statements: list[str] = []
        for line in path.read_text().splitlines():
            diagram = re.match(r"C     Coefficient construction for loop diagram with ID (\d+)", line)
            if diagram:
                statements.append(f"DIAGRAM {diagram[1]}")
            if not line or line[0] in "cC*!":
                continue
            if len(line) > 5 and line[5] not in " 0":
                statements[-1] += line[6:].strip()
            else:
                statements.append(line[6:].strip())
        for statement in statements:
            if statement.startswith("DIAGRAM "):
                current_diagram = int(statement.split()[1])
            vertex = re.fullmatch(
                r"CALL (\w+)\(PL\(0,(\d+)\),W\((\d+)\),([^,]+),([^,]+),([^,]+),PL\(0,(\d+)\),COEFS\)",
                statement)
            if vertex:
                function, parent, external, coupling, mass, width, node = vertex.groups()
                nodes[int(node)] = dict(parent=int(parent), external=int(external),
                    function=function, coupling=coupling, mass=mass, width=width)
            loop = re.fullmatch(
                rf"CALL {prefix}CREATE_LOOP_COEFS\(WL\(1,0,1,(\d+)\),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)(?:,H)?\)",
                statement)
            if not loop:
                continue
            node, rank, spin_size, group, symmetry, multiplier, amplitude = map(int, loop.groups())
            chain = []
            while node:
                if node not in nodes:
                    raise RuntimeError(f"unknown generated wavefunction node {node}")
                chain.append(nodes[node])
                node = nodes[node]["parent"]
            chain.reverse()
            graphs.append(dict(group=group, diagram=current_diagram, amplitude_slot=amplitude,
                rank=rank, spin_size=spin_size, symmetry_factor=symmetry,
                multiplier=multiplier, external_vertex_order=[v["external"] for v in chain],
                vertex_calls=[v["function"] for v in chain],
                couplings=[v["coupling"] for v in chain]))
    if not graphs:
        raise RuntimeError("could not recover individual wavefunction graph map")
    return graphs


def export(helicity: int) -> Path:
    processes = list(OUTPUT.glob("SubProcesses/P*"))
    if len(processes) != 1:
        raise RuntimeError("expected one ggH subprocess; run generation first")
    process = processes[0]
    prefix = instrument(process)
    driver(process, prefix, helicity)
    run(["make", "-C", str(process), f"SHELL={shutil.which('bash')}",
         "-j2", "check"], LOGS / "build.log")
    log = LOGS / "evaluation.log"
    run([str(process / "check")], log)
    records, metadata = parse(log)
    correspondence = graph_map(process, prefix)
    selected = [g["group"] for g in correspondence
        if g["external_vertex_order"] == list(range(1, CASE["nexternal"]+1))
        and all("L1_2" in name for name in g["vertex_calls"])]
    if len(selected) != 1:
        raise RuntimeError("cannot uniquely map the supplied oriented FeynKit graph")
    # Original MadLoop metadata API provides coefficient ordering: no local
    # symbolic polynomial manipulation is implemented by this reference tool.
    sys.path.insert(0, str(MG))
    from madgraph.various.q_polynomial import Polynomial
    max_rank = max(record["rank"] for record in records)
    polynomial = Polynomial(max_rank)
    indices = [polynomial.get_coef_at_position(i) for i in range(len(polynomial.coef_list))]
    for record in records:
        if record["propagators"] != CASE["nloop"]:
            raise RuntimeError("unexpected topology in graph-filtered export")
        ncoefs = len(Polynomial(record["rank"]).coef_list)
        if len(record["numerator"]) != ncoefs or len(record["tensors"]) != 3*ncoefs:
            raise RuntimeError("incomplete coefficient export")
    source_revision = subprocess.check_output(
        ["git", "-C", str(SOURCE), "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result = dict(schema_version=2, case=CASE_NAME, process=CASE["process"],
        loop_filter=f"n=={CASE['nloop']} and {CASE['pdg']} in loop_pdgs", helicity_index=helicity,
        source_revision=source_revision, grouping=False,
        excluded=["R2", "UV counterterm diagrams"],
        laurent_order=["finite", "single_pole", "double_pole"],
        normalization="normalized_result = raw_result / (16*pi^2)",
        polynomial_variable="x=-Q; denominators (Q+PDEN)^2-m^2",
        external_momentum_conventions={
            "external_momenta": "requested driver point, physical incoming/outgoing signs",
            "evaluated_external_momenta": "actual numerator-seam point: incoming -W%P, outgoing +W%P",
            "coefficient_construction_momenta": "independent physical-sign P argument at the same seam",
            "wavefunction_momenta": "raw complex W(i)%P(mu), keys i_mu with one-based legs and zero-based components"},
        phase_space_policy="MadLoop ImprovePSPoint=2; use evaluated_external_momenta for numerator/routing comparisons",
        reduction_convention_for_positive_pden="MadLoop",
        selected_feynkit_group=selected[0],
        feynkit_routing_relation="selected group: x=p1-q, where q is on a->b",
        graph_correspondence=correspondence,
        color_flow_coefficients=(OUTPUT / f"SubProcesses/MadLoop5_resources/{prefix}LoopColorFlowCoefs.dat").read_text(),
        coefficient_indices=indices,
        fixed_equal_gluon_color_factor=("-1/2 (fermion sign times Tr(TaTa))"
            if CASE["gluons"] == 2 else "-1/8 (fermion sign times Tr(T0^4), verified with Spenso)"),
        probe_momentum=[["2", ".25"], ["-3", ".125"], ["5", "-.5"], ["7", ".75"]],
        metadata=metadata, records=records,
        compiler=subprocess.check_output([os.environ.get("FC", "gfortran"), "--version"],
            cwd=ROOT, text=True).splitlines()[0],
        provenance={str(p.relative_to(OUTPUT)): sha256(p) for p in [
            process / "TIR_interface.f", process / "coef_construction_1.f", process / "check_sa.f",
            process / "polynomial.f", process / "loop_matrix.f", process / "improve_ps.f",
            OUTPUT / "Cards/param_card.dat", OUTPUT / "SubProcesses/MadLoop5_resources/MadLoopParams.dat",
            OUTPUT / f"SubProcesses/MadLoop5_resources/{prefix}LoopColorFlowCoefs.dat"]})
    destination = WORK / f"{CASE_NAME}-helicity-{helicity}.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    return destination


def main() -> None:
    global CASE_NAME, CASE, OUTPUT, LOGS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["all", "generate", "export"], default="all")
    parser.add_argument("--case", choices=list(CASES), default="ggh")
    parser.add_argument("--helicity", type=int, default=1)
    args = parser.parse_args()
    if Path.cwd().resolve() != ROOT:
        parser.error(f"run from {ROOT}")
    CASE_NAME = args.case
    CASE = CASES[CASE_NAME]
    OUTPUT = WORK / CASE_NAME
    LOGS = WORK / "logs" / CASE_NAME
    LOGS.mkdir(parents=True, exist_ok=True)
    if not 1 <= args.helicity <= CASE["helicities"]:
        parser.error(f"helicity must be between 1 and {CASE['helicities']}")
    if args.stage in {"all", "generate"}:
        generate()
    if args.stage in {"all", "export"}:
        print(export(args.helicity))


if __name__ == "__main__":
    main()
