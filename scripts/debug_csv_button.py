#!/usr/bin/env python3
"""Find the export button on project 12's detail page."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from factor_lib.browser import BrowserFactory
from factor_lib.pages.portal_page import TransparencyPortalPage

URL = "https://facto.conveniar.com.br/portaltransparencia/"

with BrowserFactory(headless=True, timeout=30_000) as factory:
    page = factory.new_page()
    portal = TransparencyPortalPage(page, url=URL, default_timeout=30_000)
    portal.navigate()
    portal.click_consultar()
    portal.click_detail_icon(0)  # project 12

    # Find all links and buttons
    print("=== All links containing 'xport' or 'csv' (case insensitive) ===")
    links = page.evaluate("""() => {
        const result = [];
        document.querySelectorAll('a, button, input[type=button], input[type=submit]').forEach(el => {
            const text = el.textContent.trim() || el.value || el.title || '';
            const href = el.href || '';
            if (text.toLowerCase().includes('xport') || text.toLowerCase().includes('csv')
                || href.toLowerCase().includes('csv')) {
                result.push({tag: el.tagName, text, href, id: el.id, className: el.className});
            }
        });
        return result;
    }""")
    for item in links:
        print(f"  {item}")

    print("\n=== All links/buttons on page ===")
    all_links = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a[href], button')).map(el => ({
            tag: el.tagName,
            text: el.textContent.trim().slice(0, 80),
            href: el.href || '',
            id: el.id
        })).filter(x => x.text);
    }""")
    for item in all_links:
        print(f"  {item}")
