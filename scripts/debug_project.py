#!/usr/bin/env python3
"""Capture raw HTML of a specific project's detail page for debugging."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from factor_lib.browser import BrowserFactory
from factor_lib.pages.portal_page import TransparencyPortalPage

URL = "https://facto.conveniar.com.br/portaltransparencia/"
# 0-field project index in listing (project 24 = index 1, project 88 = index 2)
ROW_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else 1

print(f"Navigating to listing, clicking lupa[{ROW_INDEX}]...")
with BrowserFactory(headless=True, timeout=30_000) as factory:
    page = factory.new_page()
    portal = TransparencyPortalPage(page, url=URL, default_timeout=30_000)
    portal.navigate()
    portal.click_consultar()

    # Find project ID at this index
    lupas = page.locator("[title='Visualizar']").all()
    print(f"Total lupas: {len(lupas)}")
    if ROW_INDEX < len(lupas):
        print(f"Lupa text: {lupas[ROW_INDEX].inner_text()[:100]}")

    portal.click_detail_icon(ROW_INDEX)

    html = page.content()
    out = Path(f"data/debug_row_{ROW_INDEX}.html")
    out.write_text(html, encoding="utf-8")
    print(f"Saved HTML ({len(html):,} bytes) → {out}")

    # Check which panels exist and their visibility
    panels = [
        "pnlProjetoInfo", "pnlProjetoEquipe", "pnlProjetoRecursoRubrica",
        "pnlProjetoPagamentoPessoaJuridica", "pnlProjetoPagamentoPessoaFisica",
        "pnlProjetoPlanoTrabalho", "pnlProjetoDocumento",
        "ctl00_upgMain2", "pnlProjeto",
    ]
    print("\nPanel visibility:")
    for panel_id in panels:
        result = page.evaluate(f"""() => {{
            const el = document.getElementById('{panel_id}');
            if (!el) return 'NOT FOUND';
            const style = window.getComputedStyle(el);
            return `display=${{style.display}} visibility=${{style.visibility}} offsetParent=${{el.offsetParent !== null}}`;
        }}""")
        print(f"  #{panel_id}: {result}")

    # Dump all visible text in body
    body_text = page.evaluate("() => document.body.innerText")
    print(f"\nBody text preview (first 500 chars):\n{body_text[:500]}")
