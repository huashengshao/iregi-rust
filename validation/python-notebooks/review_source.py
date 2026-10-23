"""Parse gallery source and bind its inputs without importing or executing it."""

import ast
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATION = Path(__file__).resolve().parent


def inspect_notebook(path):
    module = ast.parse(path.read_text(), filename=str(path))
    cells = []
    owners = {}
    for node in module.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = [item.func if isinstance(item, ast.Call) else item
                      for item in node.decorator_list]
        if not any(isinstance(item, ast.Attribute) and item.attr == "cell"
                   for item in decorators):
            continue
        returned = [item for item in node.body if isinstance(item, ast.Return)]
        names = []
        if returned and returned[-1].value is not None:
            value = returned[-1].value
            items = value.elts if isinstance(value, ast.Tuple) else [value]
            if not all(isinstance(item, ast.Name) for item in items):
                raise ValueError(f"{path}:{node.lineno}: unexpected cell return")
            names = [item.id for item in items]
        for name in names:
            if name in owners:
                raise ValueError(f"{path}: duplicate cell definition {name}")
            owners[name] = len(cells)
        cells.append({"line": node.lineno,
                      "inputs": [item.arg for item in node.args.args],
                      "returns": names})
    dependencies = []
    for cell in cells:
        missing = set(cell["inputs"]) - owners.keys()
        if missing:
            raise ValueError(f"{path}:{cell['line']}: unbound inputs {missing}")
        dependencies.append({owners[name] for name in cell["inputs"]})
    done, visiting = set(), set()

    def visit(index):
        if index in visiting:
            raise ValueError(f"{path}: dependency cycle at cell {index}")
        if index in done:
            return
        visiting.add(index)
        for dependency in dependencies[index]:
            visit(dependency)
        visiting.remove(index)
        done.add(index)

    for index in range(len(cells)):
        visit(index)
    return {"path": str(path.relative_to(ROOT)),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "ast": "parsed", "cell_dependencies": "acyclic", "cells": cells}


def main():
    paths = sorted([
        *(ROOT / "examples" / "notebooks").glob("*.py"),
        *(ROOT / "tests" / "python").glob("test_gallery_*.py"),
        Path(__file__).resolve(),
    ])
    report = {"kind": "source-only-python-ast-review", "status": "passed",
              "executed_notebooks": False, "executed_tests": False,
              "installed_packages": False, "marimo_lint": "not-run-by-this-source-parser",
              "files": [inspect_notebook(path) for path in paths]}
    destination = VALIDATION / "source-ast-review.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "passed", "parsed_files": len(paths),
                      "cells": sum(len(item["cells"]) for item in report["files"]),
                      "notebooks_executed": False,
                      "report": str(destination)}))


if __name__ == "__main__":
    main()
