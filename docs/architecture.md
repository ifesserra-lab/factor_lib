# Arquitetura de Software — factor_lib

**Versão**: 1.1.0
**Atualizado**: 2026-05-16
**Constituição**: [constitution.md](../.specify/memory/constitution.md) v1.1.0

---

## Visão Geral

`factor_lib` é uma biblioteca Python para extração automatizada de dados do
[Portal de Transparência Facto](https://facto.conveniar.com.br/portaltransparencia/).
Utiliza Playwright para automação de browser e expõe uma API pública simples para
listagem de projetos, scraping de detalhes e exportação de dados em JSON.

---

## Princípios Arquiteturais

| Princípio | Aplicação |
|-----------|-----------|
| TDD (Test-First) — NON-NEGOTIABLE | Commit Red (teste falho) ANTES do commit Green (impl); `pytest` obrigatório |
| Pirâmide de testes | `tests/unit/` → `tests/integration/` → `tests/e2e/`; todos obrigatórios |
| OO + Design Patterns | POM, Strategy, Facade, Factory, Value Object — tabela de patterns obrigatórios |
| Zero Anti-Patterns | Sem God Objects, singletons, spaghetti, duplicação |
| Playwright E2E | `pytest-playwright`; POM obrigatório; `page.route()` para mocking |
| Python idiomático | Python 3.11+, PEP 8, type hints, dataclasses, `pyproject.toml` |

---

## Estrutura de Pacotes

```
factor_lib/                          # raiz do repositório
├── pyproject.toml                   # metadados e dependências
├── src/
│   └── factor_lib/
│       ├── __init__.py              # re-exports públicos
│       ├── api.py                   # Facade — API de alto nível (feature 001)
│       ├── browser.py               # BrowserFactory + ciclo de vida do contexto
│       ├── pages/
│       │   ├── base_page.py         # BasePage — helpers de espera (POM base)
│       │   └── portal_page.py       # TransparencyPortalPage (POM concreto)
│       ├── scrapers/
│       │   ├── base_scraper.py      # AbstractScraper (interface Strategy)
│       │   ├── listing_scraper.py   # ListingScraper (Strategy — listagem)
│       │   └── detail_scraper.py    # DetailScraper  (Strategy — detalhes)
│       ├── export/
│       │   ├── __init__.py
│       │   └── csv_export.py        # Módulo de exportação CSV→JSON (feature 002)
│       ├── models/
│       │   ├── project.py           # ProjectListingRecord, ProjectDetailRecord
│       │   └── result.py            # ScrapeResult, ExportResult
│       └── serializers/
│           └── json_serializer.py   # save_to_json
└── tests/
    ├── conftest.py                  # fixtures compartilhadas
    ├── unit/                        # sem I/O externo
    ├── integration/                 # filesystem real
    └── e2e/
        ├── conftest.py              # fixtures Playwright + snapshots gravados
        └── test_portal.py           # testes E2E com mocking via page.route()
```

---

## Padrões de Design Aplicados

### Page Object Model (POM)
Cada página do portal é encapsulada em uma classe. Seletores ficam em um único lugar;
mudanças no HTML só afetam a classe da página (OCP).

```
BasePage
  └── TransparencyPortalPage
        ├── click_consultar()
        ├── get_project_rows() → list[ProjectListingRecord]
        ├── click_lupa(record)
        ├── get_detail_fields() → dict[str, str]
        └── click_export_csv() → Path  (feature 002)
```

### Strategy (Scraper)
`AbstractScraper` define o contrato; `ListingScraper` e `DetailScraper` são
implementações intercambiáveis. `PortalScraper` (Facade) os compõe.

```
AbstractScraper
  ├── ListingScraper.scrape(page) → list[ProjectListingRecord]
  └── DetailScraper.scrape(page, record) → ProjectDetailRecord
```

### Facade (API pública)
`api.py` e `export/csv_export.py` escondem a complexidade do browser, POM e
scrapers. O caller invoca uma função e recebe dados prontos.

```python
from factor_lib import scrape_and_save
from factor_lib.export import export_project_csv_to_json
```

### Factory (Browser)
`BrowserFactory` centraliza a criação e configuração do browser Playwright
(headless, timeout, tipo de browser). Injeção de dependência nos scrapers.

---

## Fluxo de Dados — Feature 001 (Scraper)

```
Portal URL
    │
    ▼ click "Consultar"
ProjectListingRecord[]
    │
    ├─ para cada registro:
    │   │
    │   ▼ click lupa
    │  ProjectDetailRecord { fields, _source_url, _scraped_at }
    │
    ▼
ScrapeResult { records[], total, success_count, error_count }
    │
    ▼ save_to_json()
output.json
```

## Fluxo de Dados — Feature 002 (CSV Export)

```
Detail Page (Playwright Page object)
    │
    ▼ click "Exportar em CSV" (segue redirect se necessário)
ZIP download → temp dir (gerenciado pela lib)
    │
    ▼ extrai CSV(s)
CSV rows → list[dict]  (linhas vazias ignoradas; encoding fallback Latin-1)
    │
    ▼ save_to_json()
output.json          (temp dir deletado automaticamente)
```

---

## Decisões Arquiteturais Relevantes

| Decisão | Escolha | Alternativa Rejeitada |
|---------|---------|----------------------|
| API Playwright | Síncrona (`sync_api`) | Assíncrona — overhead sem benefício em scraping sequencial |
| POM | `BasePage` + `TransparencyPortalPage` | Páginas separadas Listing/Detail — over-engineering para portal único |
| Serialização | `dataclasses` + `json.dumps` | `pydantic` — pesado; `dataclasses-json` — desnecessário |
| Wait strategy | `networkidle` + `wait_for_selector` | `sleep()` fixo — frágil e lento |
| Test isolation | `page.route()` mocking com snapshots gravados | Portal ao vivo em CI — viola constituição §V |
| Temp files | Lib cria e deleta temp dir automaticamente | Caller gerencia — leak em CI |
| Packaging | Módulo `factor_lib.export` no mesmo pacote | Pacote separado — overhead de dependência desnecessário |

---

## Dependências

| Pacote | Versão | Finalidade |
|--------|--------|-----------|
| `playwright` | pinada | Automação de browser |
| `pytest` | pinada | Framework de testes |
| `pytest-playwright` | pinada | Fixtures Playwright para pytest |
| `mypy` | pinada | Verificação de tipos |
| `ruff` | pinada | Linting e formatação |

---

## Quality Gates (por Pull Request)

1. `pytest` — todos os testes verde (unit + integration + E2E)
2. `mypy --strict src/` — zero erros de tipo
3. `ruff check src/ tests/` — zero warnings
4. Revisão: nenhum anti-padrão da lista da constituição §IV
5. TDD evidenciado: commit de teste falha antes do commit de implementação
