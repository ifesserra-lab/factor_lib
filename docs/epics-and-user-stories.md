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
```
