# Épicos e User Stories — factor_lib

**Data**: 2026-05-16
**Constituição**: [constitution.md](../.specify/memory/constitution.md)

---

## ÉPICO 1 — Scraper do Portal de Transparência

**Objetivo**: Automatizar a extração de dados de projetos do portal Facto, navegando
pelo listing de projetos e coletando detalhes de cada um.

**Entrega de valor**: Transforma dados públicos do portal em estrutura JSON
consultável, eliminando extração manual.

---

### US1-01 — Listar Todos os Projetos (P1 · MVP)

**Como** desenvolvedor,
**Quero** chamar uma função que navegue até o portal e clique em "Consultar",
**Para** obter a lista completa de projetos como estrutura de dados Python.

**Critérios de Aceitação**:
1. **Dado** que o portal está acessível, **Quando** `list_projects()` é chamado, **Então** retorna lista com um ou mais registros de projeto como dicts.
2. **Dado** que o portal está acessível, **Quando** `list_projects()` é chamado, **Então** o botão "Consultar" é clicado automaticamente sem interação manual.
3. **Dado** que o portal retorna zero resultados, **Quando** `list_projects()` é chamado, **Então** retorna lista vazia sem lançar exceção.

**Teste independente**: Chamar `list_projects()` e verificar lista não vazia com campo `id` e `name`.

---

### US1-02 — Scraping de Detalhes de Projetos (P2)

**Como** desenvolvedor,
**Quero** chamar uma função que itere a lista de projetos e clique na lupa de cada um,
**Para** obter todos os campos detalhados de cada projeto em uma estrutura agregada.

**Critérios de Aceitação**:
1. **Dado** N projetos na listagem, **Quando** `scrape_all_projects()` é chamado, **Então** retorna exatamente N registros de detalhe.
2. **Dado** projeto com ícone de lupa, **Quando** processado, **Então** ícone é clicado e view de detalhe é totalmente carregada antes da leitura.
3. **Dado** página de detalhe com campos rotulados, **Quando** scraped, **Então** todos os campos visíveis são capturados como pares chave-valor.
4. **Dado** falha ao clicar lupa em um projeto, **Quando** scraping continua, **Então** projeto é marcado com erro e o processo segue para o próximo.

**Teste independente**: Verificar que cada registro contém mais campos que a listagem sozinha.

---

### US1-03 — Salvar Resultados em JSON (P3)

**Como** desenvolvedor,
**Quero** chamar `save_to_json(records, path)` com os dados extraídos,
**Para** persistir os dados em arquivo JSON reutilizável por outros sistemas.

**Critérios de Aceitação**:
1. **Dado** lista de dicts de detalhe, **Quando** `save_to_json(records, path)` é chamado, **Então** arquivo em `path` é criado contendo array JSON válido.
2. **Dado** arquivo já existe em `path`, **Quando** `save_to_json` é chamado, **Então** arquivo é sobrescrito com novos dados.
3. **Dado** diretório de `path` não existe, **Quando** `save_to_json` é chamado, **Então** diretório é criado automaticamente antes da escrita.

**Teste independente**: Verificar que arquivo JSON gerado tem mesmo número de registros que a lista de entrada.

---

## ÉPICO 2 — Exportação CSV para JSON

**Objetivo**: Na página de detalhes do portal, acionar a exportação CSV, baixar o
arquivo ZIP resultante, processar os CSVs contidos e salvar tudo em JSON.

**Entrega de valor**: Captura dados estruturados em formato tabular exportados
pelo portal, complementando os dados scraped do ÉPICO 1.

---

### US2-01 — Acionar Download do CSV (P1 · MVP)

**Como** desenvolvedor,
**Quero** chamar uma função que localize e clique em "Exportar em CSV" na página de detalhe,
**Para** iniciar o download automático do arquivo ZIP com os dados do projeto.

**Critérios de Aceitação**:
1. **Dado** página de detalhe carregada com botão "Exportar em CSV" visível, **Quando** `download_csv_export(page)` é chamado, **Então** botão é clicado e ZIP é baixado para diretório temporário gerenciado pela lib.
2. **Dado** download concluído, **Quando** completo, **Então** arquivo ZIP existe e tem tamanho > 0.
3. **Dado** botão "Exportar em CSV" ausente na página, **Quando** chamado, **Então** erro informativo é lançado sem crash.
4. **Dado** botão aciona redirect, **Quando** clicado, **Então** redirect é seguido e download é tentado na URL final.

**Timeout**: 60 segundos máximo para conclusão do download.

**Teste independente**: Verificar ZIP não vazio retornado no path temporário.

---

### US2-02 — Extrair e Parsear CSV do ZIP (P2)

**Como** desenvolvedor,
**Quero** passar o caminho do ZIP para uma função de parsing,
**Para** obter todos os registros CSV como lista de dicts com os cabeçalhos como chaves.

**Critérios de Aceitação**:
1. **Dado** ZIP válido com um ou mais CSVs, **Quando** `parse_zip_csv(zip_path)` é chamado, **Então** retorna lista de dicts, um por linha, com cabeçalhos como chaves.
2. **Dado** ZIP com múltiplos CSVs, **Quando** parseado, **Então** linhas de todos os arquivos são mescladas em lista única, cada registro com `_source_file`.
3. **Dado** ZIP sem CSVs, **Quando** `parse_zip_csv` é chamado, **Então** retorna lista vazia e loga aviso.
4. **Dado** CSV com encoding não-UTF-8, **Quando** parseado, **Então** fallback para Latin-1/ISO-8859-1 antes de lançar erro.
5. **Dado** CSV com linhas vazias, **Quando** parseado, **Então** linhas vazias são ignoradas silenciosamente; contagem é logada em nível debug.

**Teste independente**: Verificar que resultado tem chaves iguais aos cabeçalhos do CSV.

---

### US2-03 — Salvar Registros CSV em JSON (P3)

**Como** desenvolvedor,
**Quero** chamar `save_to_json(records, path)` com os registros CSV parseados,
**Para** persistir os dados em arquivo JSON para consumo downstream.

**Critérios de Aceitação**:
1. **Dado** lista de dicts derivados do CSV, **Quando** `save_to_json(records, path)` é chamado, **Então** arquivo em `path` é criado com array JSON válido.
2. **Dado** arquivo já existe, **Quando** chamado, **Então** é sobrescrito.
3. **Dado** diretório pai não existe, **Quando** chamado, **Então** diretórios são criados automaticamente.

**Nota**: Reutiliza `save_to_json` do núcleo de `factor_lib` (compartilhado com ÉPICO 1).

---

### US2-04 — Fluxo End-to-End em Chamada Única (P4)

**Como** desenvolvedor,
**Quero** chamar `export_project_csv_to_json(page, output_path)` com a página de detalhe aberta,
**Para** executar todo o fluxo de exportação (clique → download → parse → salvar) em uma linha.

**Critérios de Aceitação**:
1. **Dado** página de detalhe aberta, **Quando** `export_project_csv_to_json(page, output_path)` é chamado, **Então** arquivo JSON em `output_path` contém todos os registros CSV do projeto.
2. **Dado** falha em qualquer etapa, **Quando** chamado, **Então** erro é lançado com mensagem indicando qual etapa falhou.

**Teste independente**: Verificar JSON gerado tem registros esperados do projeto.

---

## ÉPICO 3 — Modelo de Domínio Estruturado

**Objetivo**: Converter os registros CSV brutos exportados do portal em um modelo de
domínio tipado e validado, pronto para análise financeira e relatórios.

**Entrega de valor**: Transforma dicts genéricos em dataclasses Python fortemente
tipadas com `Decimal` para valores monetários, `datetime.date` para datas e `None`
para campos ausentes — eliminando parsing ad-hoc no código downstream.

**Status**: Concluído ✅ — `factor_lib.domain` implementado e testado (146/146 testes passando).

---

### US3-01 — Parsear Informações do Projeto (P1 · MVP)

**Como** desenvolvedor,
**Quero** chamar `parse_project_info(records)` com os registros CSV brutos,
**Para** obter um objeto `ProjetoInfo` com campos tipados (datas, Decimal, strings normalizadas).

**Critérios de Aceitação**:
1. `ProjetoInfo.referencia` extrai apenas o número antes do " — " (ex.: "372 - Estudos" → "372").
2. Campos de data são `datetime.date`; campos monetários são `Decimal` sem separador de milhar.
3. Campos opcionais (`data_encerramento`, `departamento`, `processo`) retornam `None` quando valor é `\xa0` ou vazio.
4. Lança `DomainParseError` se nenhum registro do arquivo "informações do projeto" for encontrado.
5. Matching do arquivo de origem é por substring ("informa") para tolerar encoding CP437/Latin-1 nos ZIPs.

**Teste independente**: `parse_project_info([record_with_full_fields])` retorna `ProjetoInfo` com `referencia == "372"` e `valor_aprovado == Decimal("3722800.00")`.

---

### US3-02 — Parsear Entidades de Projeto (P2)

**Como** desenvolvedor,
**Quero** chamar parsers específicos para cada CSV exportado (equipe, pagamentos, plano de trabalho, recursos, documentos, prestações de contas),
**Para** obter listas de dataclasses tipadas para cada entidade do projeto.

**Entidades e parsers**:

| Parser | Entidade | Arquivo fonte (keyword) |
|--------|----------|------------------------|
| `parse_equipe` | `MembroEquipe` | "equipe" |
| `parse_pagamentos` | `Pagamento` | "pagamento" |
| `parse_plano_trabalho` | `ItemPlanoTrabalho` | "plano" |
| `parse_recursos` | `RecursoRubrica` | "recurso" |
| `parse_documentos` | `Documento` | "documento" |
| `parse_prestacoes_contas` | `PrestacaoContas` | "presta" |

**Critérios de Aceitação**:
1. Cada parser filtra por keyword no nome do arquivo fonte (`source_file`).
2. Campos monetários são `Decimal`; datas são `datetime.date`; valores `\xa0` → `None`.
3. Registros sem correspondência de arquivo retornam lista vazia (sem erro).
4. `Pagamento.tipo_favorecido` é derivado do nome do arquivo ("pessoa" → `"pessoa_fisica"`, default → `"servidor"`).

**Teste independente**: `parse_recursos([matching_record, non_matching_record])` retorna exatamente 1 `RecursoRubrica`.

---

### US3-03 — Construir Modelo Completo via Facade (P3)

**Como** desenvolvedor,
**Quero** chamar `build_projeto(records)` com todos os registros CSV de um projeto,
**Para** obter um único `ProjetoCompleto` com todas as entidades já parseadas e tipadas.

**Critérios de Aceitação**:
1. `ProjetoCompleto` agrega `ProjetoInfo` + 6 tuples de entidades via chamada única.
2. Todos os campos são imutáveis (`frozen=True` em todos os dataclasses).
3. `ProjetoCompleto` é serializável via `dataclasses.asdict()` para JSON.
4. Lança `DomainParseError` apenas se `ProjetoInfo` não puder ser extraído.

**Teste independente**: `build_projeto(real_records_from_projeto_372)` retorna `ProjetoCompleto.info.referencia == "372"` com equipe e pagamentos populados.

---

## Mapa de Dependências

```
US1-01 (Listar projetos)
    └─► US1-02 (Scraping detalhes)
            └─► US1-03 (Salvar JSON)  ◄── compartilhado
                                              ▲
US2-01 (Download CSV)                         │
    └─► US2-02 (Parsear CSV)                  │
            └─► US2-03 (Salvar JSON) ─────────┘
                    └─► US2-04 (End-to-end)
                              │
                              ▼ (records brutos)
                        US3-01 (parse_project_info)
                        US3-02 (parsers por entidade) [P]
                              └─► US3-03 (build_projeto Facade) ✅ CONCLUÍDO
```
