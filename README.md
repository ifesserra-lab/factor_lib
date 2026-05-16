# factor_lib

Biblioteca Python para extração automatizada de dados do
[Portal de Transparência Facto](https://facto.conveniar.com.br/portaltransparencia/).

Usa Playwright para automação de browser — sem APIs privadas, sem scraping frágil
de HTML estático. Navega o portal como um usuário real e salva tudo em JSON.

---

## O que faz

### Épico 1 — Scraper do Portal

```python
from factor_lib import scrape_and_save

result = scrape_and_save("output/projetos.json")
print(f"{result.success_count} projetos extraídos, {result.error_count} erros.")
```

1. Acessa o portal de transparência
2. Clica em **Consultar** → lista todos os projetos
3. Para cada projeto, clica na **lupa** → entra nos detalhes
4. Captura todos os campos visíveis (labels e valores em português)
5. Salva tudo em um arquivo JSON

### Épico 2 — Exportação CSV para JSON

```python
from factor_lib.export import export_project_csv_to_json

# Com a página de detalhe já aberta no Playwright:
export_project_csv_to_json(page, "output/projeto_csv.json")
```

1. Clica em **Exportar em CSV** na página de detalhe
2. Baixa o arquivo ZIP automaticamente (timeout: 60s)
3. Abre o ZIP, parseia todos os CSVs internos
4. Trata encoding (UTF-8 com fallback para Latin-1/ISO-8859-1)
5. Salva todos os registros em JSON
6. Apaga arquivos temporários automaticamente

---

## Instalação

```bash
git clone https://github.com/ifesserra-lab/factor_lib.git
cd factor_lib

pip install -e ".[dev]"
playwright install chromium
```

---

## Uso rápido

### Scraper completo (Épico 1)

```python
from factor_lib import scrape_and_save

# Uma chamada — lista, detalha e salva
result = scrape_and_save("output/projetos.json")
```

### Funções individuais

```python
from factor_lib import list_projects, scrape_all_projects, save_to_json

# Só a listagem
projetos = list_projects()

# Listagem + detalhes
resultado = scrape_all_projects()

# Salvar resultado
save_to_json(resultado.records, "output/projetos.json")
```

### Exportação CSV (Épico 2)

```python
from playwright.sync_api import sync_playwright
from factor_lib.export import export_project_csv_to_json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://facto.conveniar.com.br/portaltransparencia/")
    # ... navegar até a página de detalhe ...
    export_project_csv_to_json(page, "output/projeto.json")
    browser.close()
```

### Saída JSON — Épico 1

```json
[
  {
    "id": "PRJ-001",
    "name": "Projeto Exemplo",
    "Situação": "Em andamento",
    "Valor Total": "R$ 500.000,00",
    "Beneficiário": "Município X",
    "_source_url": "https://facto.conveniar.com.br/portaltransparencia/",
    "_scraped_at": "2026-05-16T14:30:00",
    "_error": null
  }
]
```

### Saída JSON — Épico 2

```json
[
  {
    "Código": "PRJ-001",
    "Descrição": "...",
    "Valor": "500000",
    "_source_file": "projeto_001.csv",
    "_extracted_at": "2026-05-16T14:35:00"
  }
]
```

---

## Estrutura do projeto

```
factor_lib/
├── src/
│   └── factor_lib/
│       ├── api.py                  # API pública de alto nível
│       ├── browser.py              # Gerenciamento do browser Playwright
│       ├── pages/
│       │   ├── base_page.py        # Page Object base
│       │   └── portal_page.py      # Page Object do portal
│       ├── scrapers/
│       │   ├── listing_scraper.py  # Extração da listagem
│       │   └── detail_scraper.py   # Extração dos detalhes
│       ├── export/
│       │   ├── downloader.py       # Download do ZIP via Playwright
│       │   ├── csv_parser.py       # Parsing de CSV dentro do ZIP
│       │   └── exporter.py         # Facade end-to-end
│       ├── models/
│       │   ├── project.py          # ProjectListingRecord, ProjectDetailRecord
│       │   └── result.py           # ScrapeResult, ExportResult
│       └── serializers/
│           └── json_serializer.py  # save_to_json
└── tests/
    ├── unit/                       # Sem I/O externo
    ├── integration/                # Filesystem real
    └── e2e/                        # Playwright com mocks (sem portal ao vivo)
        └── fixtures/               # Snapshots HTML/ZIP gravados
```

---

## Desenvolvimento

```bash
# Rodar todos os testes
pytest

# Só unitários (rápido)
pytest tests/unit

# Type check
mypy src/

# Lint
ruff check src/ tests/
```

### Padrão TDD (obrigatório)

```
1. Escrever teste → confirmar que FALHA (Red)
2. Implementar o mínimo para passar (Green)
3. Refatorar mantendo testes verdes (Refactor)
4. Commit do teste (Red) → commit da implementação (Green)
```

---

## Padrões de design

| Padrão | Onde | Por quê |
|--------|------|---------|
| Page Object Model | `pages/` | Seletores em um lugar; mudanças no HTML afetam só a página |
| Strategy | `scrapers/` | `ListingScraper` e `DetailScraper` intercambiáveis |
| Facade | `api.py`, `exporter.py` | Uma chamada para o fluxo completo |
| Factory | `browser.py` | Criação e configuração do browser centralizada |

---

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/architecture.md](docs/architecture.md) | Arquitetura detalhada, decisões técnicas |
| [docs/backlog.md](docs/backlog.md) | Épicos e status das User Stories |
| [docs/epics-and-user-stories.md](docs/epics-and-user-stories.md) | US completas com Given/When/Then |
| [specs/001-transparency-scraper/](specs/001-transparency-scraper/) | Spec, plano, contratos e quickstart do Épico 1 |
| [specs/002-csv-export-to-json/](specs/002-csv-export-to-json/) | Spec, tasks e clarificações do Épico 2 |
| [.specify/memory/constitution.md](.specify/memory/constitution.md) | Constituição do projeto (princípios e regras) |

---

## Licença

MIT
