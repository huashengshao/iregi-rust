"""Inspect offscreen benchmark cells in the same static export qualification."""

from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import time

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent / "attempt002"
loader = json.loads((OUT / "loader-environment.json").read_text())
os.environ["LD_LIBRARY_PATH"] = loader["library_path"]
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(ROOT / ".local/playwright-browsers")

from playwright.sync_api import sync_playwright
from smoke_browser import QuietHandler


def main():
    requests, failures, page_errors, views = [], [], [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "target/gallery")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    start = time.monotonic()
    try:
        with sync_playwright() as driver:
            browser = driver.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
            for name, width, height, color in [("desktop", 1440, 1100, "light"), ("mobile", 390, 1400, "dark")]:
                context = browser.new_context(viewport={"width": width, "height": height}, color_scheme=color)
                page = context.new_page()
                page.on("request", lambda request: requests.append({"url": request.url, "type": request.resource_type}))
                page.on("requestfailed", lambda request: failures.append({"url": request.url, "failure": request.failure}))
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/benchmarks-posthoc.html", timeout=30000)
                grid = page.locator(".tirust-overflow").first
                grid.wait_for(state="visible", timeout=30000)
                grid.scroll_into_view_if_needed()
                page.evaluate("document.fonts.ready")
                grid.screenshot(path=str(OUT / f"{name}-grid-left.png"), timeout=15000)
                dimensions = grid.evaluate("e=>({visible:e.clientWidth,content:e.scrollWidth})")
                grid.evaluate("e=>e.scrollLeft=e.scrollWidth-e.clientWidth")
                grid.screenshot(path=str(OUT / f"{name}-grid-right.png"), timeout=15000)
                chart = page.locator("svg.tirust-chart")
                chart.screenshot(path=str(OUT / f"{name}-chart.png"), timeout=15000)
                views.append({"name": name, "viewport": {"width": width, "height": height},
                              "grid": dimensions, "ratio_cells": page.locator(".tirust-ratio").count(),
                              "hero_font": page.locator(".tirust-hero h1").evaluate("e=>getComputedStyle(e).fontFamily"),
                              "grid_font": grid.evaluate("e=>getComputedStyle(e).fontFamily")})
                context.close()
            browser.close()
        result = {"status": "PASS" if not failures and not page_errors else "FAIL",
                  "seconds": time.monotonic() - start, "views": views,
                  "frontend_requests": len(requests), "failed_requests": failures,
                  "page_errors": page_errors, "changed_source_or_HTML": False,
                  "scope": "Targeted existing grid/chart crops; horizontal scrolling inspected, static backend remains absent."}
        (OUT / "grid-result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if result["status"] != "PASS":
            raise RuntimeError("Grid inspection frontend failure.")
    finally:
        (OUT / "grid-requests.json").write_text(json.dumps(requests, indent=2) + "\n")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
