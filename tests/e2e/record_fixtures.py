"""One-time script to record portal HTML snapshots for E2E test fixtures.

Run: .venv/bin/python tests/e2e/record_fixtures.py

Portal uses ASP.NET WebForms full postbacks. After clicking "Visualizar":
- upgMain2 (listing panel) becomes hidden
- pnlProjetoInfo and other pnl* panels become visible with project detail
"""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

PORTAL_URL = "https://facto.conveniar.com.br/portaltransparencia/"
FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONSULTAR_SEL = "#ctl00_ContentPlaceHolder1_ProjetosUserControl1_lnkConsultarProjetos"
LUPA_SEL = "[title='Visualizar']"


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Navigating to {PORTAL_URL} ...")
        page.goto(PORTAL_URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_selector(CONSULTAR_SEL, timeout=30_000)
        page.click(CONSULTAR_SEL)
        page.wait_for_load_state("networkidle", timeout=60_000)
        page.wait_for_selector(LUPA_SEL, timeout=30_000)

        listing_html = page.content()
        out = FIXTURES_DIR / "portal_listing.html"
        out.write_text(listing_html, encoding="utf-8")
        print(f"Saved listing snapshot → {out} ({len(listing_html):,} bytes)")

        first_lupa = page.locator(LUPA_SEL).first
        first_lupa.click(timeout=30_000)
        page.wait_for_load_state("networkidle", timeout=60_000)
        # Wait for listing panel to hide — signals detail view is active
        page.wait_for_selector("#ctl00_upgMain2", state="hidden", timeout=30_000)
        # pnlProjetoInfo becomes visible once JavaScript finishes rendering
        page.wait_for_function(
            "() => { const el = document.getElementById('pnlProjetoInfo');"
            " return el && el.offsetParent !== null; }",
            timeout=30_000,
        )

        detail_html = page.content()
        out2 = FIXTURES_DIR / "portal_detail.html"
        out2.write_text(detail_html, encoding="utf-8")
        print(f"Saved detail snapshot  → {out2} ({len(detail_html):,} bytes)")

        browser.close()
    print("Done.")


if __name__ == "__main__":
    main()
