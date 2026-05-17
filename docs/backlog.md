# Backlog — factor_lib

**Última atualização**: 2026-05-16 | **Constituição**: v1.1.0

---

## Épicos

| Épico | Branch | Spec | Plan | Tasks | Status |
|-------|--------|------|------|-------|--------|
| Scraper do Portal de Transparência | `001-transparency-scraper` | [spec.md](../specs/001-transparency-scraper/spec.md) | [plan.md](../specs/001-transparency-scraper/plan.md) | [tasks.md](../specs/001-transparency-scraper/tasks.md) | Pendente ⏳ |
| Exportação CSV para JSON | `002-csv-export-to-json` | [spec.md](../specs/002-csv-export-to-json/spec.md) | [plan.md](../specs/002-csv-export-to-json/plan.md) | [tasks.md](../specs/002-csv-export-to-json/tasks.md) | Concluído ✅ |
| Modelo de Domínio do Projeto | `003-project-domain-model` | [spec.md](../specs/003-project-domain-model/spec.md) | [plan.md](../specs/003-project-domain-model/plan.md) | [tasks.md](../specs/003-project-domain-model/tasks.md) | Concluído ✅ |

---

## User Stories

### ÉPICO 1 — [spec.md](../specs/001-transparency-scraper/spec.md) · [tasks.md](../specs/001-transparency-scraper/tasks.md)

| ID | P | Título | Tasks | Status |
|----|---|--------|-------|--------|
| US1-01 | P1 | Listar todos os projetos | T021–T029 | Pendente ⏳ |
| US1-02 | P2 | Scraping de detalhes (lupa) | T030–T037 | Pendente ⏳ |
| US1-03 | P3 | Salvar resultados em JSON | T038–T043 | Pendente ⏳ |

### ÉPICO 2 — [spec.md](../specs/002-csv-export-to-json/spec.md) · [tasks.md](../specs/002-csv-export-to-json/tasks.md)

| ID | P | Título | Tasks | Status |
|----|---|--------|-------|--------|
| US2-01 | P1 | Acionar download CSV | T010–T014 | Concluído ✅ |
| US2-02 | P2 | Extrair e parsear CSV do ZIP | T015–T021 | Concluído ✅ |
| US2-03 | P3 | Salvar registros em JSON | T022–T025 | Concluído ✅ |
| US2-04 | P4 | Fluxo end-to-end | T026–T031 | Concluído ✅ |

### ÉPICO 3 — [spec.md](../specs/003-project-domain-model/spec.md) · [tasks.md](../specs/003-project-domain-model/tasks.md)

| ID | P | Título | Tasks | Status |
|----|---|--------|-------|--------|
| US3-01 | P1 | Parsear informações do projeto | T007–T013 | Concluído ✅ |
| US3-02 | P2 | Parsear entidades de projeto (equipe, pagamentos, plano, recursos, documentos, prestações) | T014–T027 | Concluído ✅ |
| US3-03 | P3 | Construir modelo completo via Facade `build_projeto()` | T028–T032 | Concluído ✅ |

---

## Legenda de Status

| Status | Significado |
|--------|-------------|
| Pendente | Não iniciado |
| Em andamento 🔄 | Em desenvolvimento |
| Bloqueado | Aguardando dependência |
| Concluído ✅ | Implementado e testado |
| Cancelado ❌ | Removido do escopo |
