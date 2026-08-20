"""Build the static dashboard site from the scraped project data.

Reads output/projetos.json and scripts/site_template.html, embeds the data
into the template and writes a self-contained site/index.html ready for
GitHub Pages (https://ifesserra-lab.github.io/factor/).
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "output" / "projetos.json"
TEMPLATE_PATH = ROOT / "scripts" / "site_template.html"
OUT_PATH = ROOT / "site" / "index.html"

HTML_SKELETON = (
    "<!doctype html>\n"
    '<html lang="pt-BR">\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
)


def build() -> pathlib.Path:
    data = json.loads(DATA_PATH.read_text())
    for record in data:
        record.pop("_source_url", None)
        record.pop("_error", None)
        record.pop("name", None)

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    html = HTML_SKELETON + TEMPLATE_PATH.read_text().replace("__DATA__", payload)
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(html)
    return OUT_PATH


if __name__ == "__main__":
    out = build()
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB)")
