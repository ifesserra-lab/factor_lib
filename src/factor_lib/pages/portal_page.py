"""TransparencyPortalPage: POM for the Facto transparency portal."""
from __future__ import annotations

import re

from playwright.sync_api import Page

from factor_lib.pages.base_page import BasePage

CONSULTAR_SEL = "#ctl00_ContentPlaceHolder1_ProjetosUserControl1_lnkConsultarProjetos"
LUPA_SEL = "[title='Visualizar']"
LISTING_PANEL_SEL = "#ctl00_upgMain2"
DETAIL_READY_JS = (
    "() => { const el = document.getElementById('pnlProjetoInfo');"
    " return el && el.offsetParent !== null; }"
)

_ID_RE = re.compile(r"projeto\s+(\d+)", re.IGNORECASE)


class TransparencyPortalPage(BasePage):
    """Page Object for the Facto transparency portal."""

    def __init__(self, page: Page, *, url: str, default_timeout: int = 30_000) -> None:
        super().__init__(page, default_timeout=default_timeout)
        self.url = url

    def navigate(self) -> None:
        self.page.goto(self.url, wait_until="networkidle", timeout=60_000)

    # ------------------------------------------------------------------ listing

    def click_consultar(self) -> None:
        self.wait_for(CONSULTAR_SEL)
        self.page.click(CONSULTAR_SEL)
        self.wait_for_network_idle()

    def get_listing_rows(self) -> list[dict[str, str]]:
        """Return raw row data from all project listing links."""
        lupas = self.page.locator(LUPA_SEL).all()
        rows = []
        for i, lupa in enumerate(lupas):
            text = lupa.inner_text().strip()
            m = _ID_RE.search(text)
            proj_id = m.group(1) if m else str(i)
            # Strip "Visualizar os detalhes do projeto N - " prefix to get clean name
            if m:
                name = text[m.end():].lstrip(" -").strip()
            else:
                name = text
            rows.append({"id": proj_id, "name": name, "raw": text})
        return rows

    # ------------------------------------------------------------------ detail

    def click_detail_icon(self, row_index: int) -> None:
        """Click the lupa icon at the given row index and wait for detail view."""
        lupas = self.page.locator(LUPA_SEL)
        lupas.nth(row_index).click(timeout=self.default_timeout)
        self.page.wait_for_load_state("networkidle", timeout=60_000)
        # Confirm detail view: listing panel must be hidden
        self.page.wait_for_selector(LISTING_PANEL_SEL, state="hidden", timeout=15_000)
        # Wait for pnlProjetoInfo to be rendered (confirms content is ready).
        # Some project types don't have this panel — silently continue if timeout.
        try:
            self.page.wait_for_function(DETAIL_READY_JS, timeout=10_000)
        except Exception:
            pass

    def get_detail_fields(self) -> dict[str, str]:
        """Extract all label-value pairs from the visible detail panels."""
        fields: dict[str, str] = {}

        # pnlProjetoInfo: label → value pairs (li > label + span/input)
        fields.update(self._extract_label_values("#pnlProjetoInfo"))

        # pnlProjetoHeader may overlap with pnlProjetoInfo; skip duplicates silently

        # Table panels: include row count and section title as metadata
        table_panels = {
            "Recursos por rubrica": "#pnlProjetoRecursoRubrica",
            "Pagamento pessoa jurídica": "#pnlProjetoPagamentoPessoaJuridica",
            "Pagamento pessoa física": "#pnlProjetoPagamentoPessoaFisica",
            "Equipe": "#pnlProjetoEquipe",
            "Plano de trabalho": "#pnlProjetoPlanoTrabalho",
            "Documentos": "#pnlProjetoDocumento",
        }
        for section_name, sel in table_panels.items():
            rows_text = self._extract_table_text(sel)
            if rows_text:
                fields[section_name] = rows_text

        return fields

    def _extract_label_values(self, panel_selector: str) -> dict[str, str]:
        result = self.page.evaluate(
            """(sel) => {
                const panel = document.querySelector(sel);
                if (!panel) return {};
                const out = {};
                panel.querySelectorAll('li').forEach(li => {
                    const label = li.querySelector('label');
                    if (!label) return;
                    const key = label.textContent.trim().replace(/:$/, '');
                    const span = li.querySelector('span');
                    const inp = li.querySelector('input[type=text]');
                    const value = span
                        ? span.textContent.trim()
                        : (inp ? inp.value.trim() : '');
                    if (key) out[key] = value;
                });
                return out;
            }""",
            panel_selector,
        )
        return dict(result)

    def _extract_table_text(self, panel_selector: str) -> str:
        text: str = self.page.evaluate(
            """(sel) => {
                const panel = document.querySelector(sel);
                if (!panel || panel.offsetParent === null) return '';
                return panel.innerText.trim();
            }""",
            panel_selector,
        )
        return text

    def navigate_back_to_listing(self) -> None:
        """Return to the project listing by re-navigating and clicking Consultar."""
        self.navigate()
        self.click_consultar()
