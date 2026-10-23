"""Inspect real marimo static output without a browser or native extension."""

from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPORT = ROOT / "target/gallery/benchmarks-posthoc.html"


class AssetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "link", "img"):
            for name, value in attrs:
                if name in ("src", "href") and value.startswith(("https://", "http://")):
                    self.urls.add(value)


def main():
    payload = EXPORT.read_bytes()
    text = payload.decode()
    for line in text.splitlines():
        if line.lstrip().startswith('"session": '):
            session = json.loads(line.strip()[len('"session": '):].rstrip(","))
            break
    else:
        raise ValueError("Export has no embedded marimo session.")
    outputs = [output for cell in session["cells"] for output in cell.get("outputs", [])]
    assert all(output["type"] == "data" for output in outputs), "Export contains a failed cell."
    markup = [output.get("data", {}).get("text/html", "") for output in outputs]
    grid = next(item for item in markup if '<table class="tirust-table">' in item)
    assert grid.count("<tr>") == 9
    assert grid.count("inconclusive-short-block") == 1
    assert grid.count("regression") == 7
    assert "TIRust (selected) / COLLIER" in grid
    assert "TIRust (selected) divided by COLLIER" in grid
    assert grid.count("<circle") == 8
    assert grid.count("99% CI") == 8
    assets = AssetLinks()
    assets.feed(text)
    report = {
        "status": "PASS", "html_sha256": sha256(payload).hexdigest(), "bytes": len(payload),
        "cells": len(session["cells"]), "failed_output_cells": 0, "default_rows": 8,
        "timing_gates": {"regression": 7, "inconclusive-short-block": 1},
        "uncertainty_chart_points": 8, "displayed_99_percent_intervals": 8,
        "external_asset_urls": sorted(assets.urls),
        "offline_self_contained": not bool(assets.urls), "browser_visual_review": "pending",
        "limitation": "Static HTML embeds successful default outputs; frontend assets use marimo0.24.0 jsDelivr CDN. No browser or interactive frontend rendering is qualified.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
