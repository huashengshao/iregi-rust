"""One real browser smoke of the static benchmark export, without a backend."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import time

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent / "browser"
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(ROOT / ".local/playwright-browsers")

from playwright.sync_api import sync_playwright


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    OUT.mkdir(exist_ok=True)
    requests, responses, failures, console_errors, page_errors, views = [], [], [], [], [], []
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "target/gallery")))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    began = time.monotonic()
    try:
        with sync_playwright() as driver:
            browser = driver.chromium.launch(headless=True, args=["--no-sandbox"], timeout=20000)
            version = browser.version
            for name, width, height, color in [("desktop-light", 1440, 1100, "light"),
                                               ("mobile-dark", 390, 844, "dark")]:
                context = browser.new_context(viewport={"width": width, "height": height}, color_scheme=color)
                page = context.new_page()
                page.on("request", lambda r: requests.append({"url": r.url, "method": r.method,
                                                             "type": r.resource_type}))
                page.on("response", lambda r: responses.append({"url": r.url, "status": r.status}))
                page.on("requestfailed", lambda r: failures.append({"url": r.url, "failure": r.failure}))
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.on("console", lambda message: console_errors.append(message.text)
                        if message.type == "error" else None)
                page.goto(f"http://127.0.0.1:{server.server_port}/benchmarks-readable.html",
                          wait_until="domcontentloaded", timeout=30000)
                page.locator(".tirust-hero h1").wait_for(state="visible", timeout=30000)
                page.locator("table.tirust-table tbody tr").first.wait_for(state="visible", timeout=15000)
                page.evaluate("document.fonts.ready")
                assert page.locator("table.tirust-table tbody tr").count() == 8
                assert page.locator(".tirust-ratio").count() == 8
                assert "TIRust (selected) / COLLIER" in page.locator("table.tirust-table").inner_text()
                assert "inconclusive-short-block" in page.locator("table.tirust-table").inner_text()
                dimensions = page.evaluate("({viewport:innerWidth,document:document.documentElement.scrollWidth})")
                page.screenshot(path=str(OUT / f"{name}.png"), full_page=True, timeout=15000)
                views.append({"name": name, "viewport": {"width": width, "height": height},
                              "color_scheme": color, "dimensions": dimensions,
                              "rows": 8, "ratio_cells": 8,
                              "hero": page.locator(".tirust-hero h1").inner_text(),
                              "katex_elements": page.locator(".katex").count(),
                              "mathjax_elements": page.locator("mjx-container").count()})
                context.close()
            browser.close()
        result = {"status": "PASS", "browser": version, "views": views,
                  "seconds": time.monotonic() - began, "frontend_requests": len(requests),
                  "failed_requests": len(failures), "console_errors": console_errors,
                  "page_errors": page_errors, "native_backend": False,
                  "scope": "Two real Chromium views of the static benchmark export only; no reactive numerical backend."}
        if failures or page_errors:
            result["status"] = "FAIL"
        (OUT / "browser-result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if result["status"] != "PASS":
            raise RuntimeError("Browser smoke recorded frontend failures.")
    finally:
        for filename, data in [("requests.json", requests), ("responses.json", responses),
                               ("failed-requests.json", failures), ("console-errors.json", console_errors),
                               ("page-errors.json", page_errors)]:
            (OUT / filename).write_text(json.dumps(data, indent=2) + "\n")
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
