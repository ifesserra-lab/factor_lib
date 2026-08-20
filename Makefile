.PHONY: help install test test-unit test-integration test-e2e lint typecheck scrape listing site deploy clean

PYTHON := .venv/bin/python
PIP := .venv/bin/pip
OUTPUT ?= output/projetos.json

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.venv: ## Cria o virtualenv
	python3 -m venv .venv

install: .venv ## Instala a lib em modo editável + browser Chromium
	$(PIP) install -e ".[dev]"
	$(PYTHON) -m playwright install chromium

test: ## Roda todos os testes
	$(PYTHON) -m pytest

test-unit: ## Roda só os testes unitários (rápido)
	$(PYTHON) -m pytest tests/unit -q

test-integration: ## Roda os testes de integração
	$(PYTHON) -m pytest tests/integration -q

test-e2e: ## Roda os testes E2E (Playwright com mocks)
	$(PYTHON) -m pytest tests/e2e -q

lint: ## Lint com ruff
	$(PYTHON) -m ruff check src/ tests/

typecheck: ## Type check com mypy
	$(PYTHON) -m mypy src/

listing: ## Lista os projetos do portal (sem detalhes)
	$(PYTHON) -c "from factor_lib import list_projects; \
projs = list_projects(); \
print(f'{len(projs)} projetos'); \
[print(f'  {p.id}: {p.name}') for p in projs]"

scrape: ## Scrape completo (listagem + detalhes) -> $(OUTPUT)
	$(PYTHON) -c "from factor_lib import scrape_and_save; \
r = scrape_and_save('$(OUTPUT)'); \
print(f'total={r.total} ok={r.success_count} erros={r.error_count}')"

site: ## Gera site/index.html a partir de output/projetos.json
	$(PYTHON) scripts/build_site.py

deploy: site ## Publica o dashboard em https://ifesserra-lab.github.io/factor/
	rm -rf .deploy
	git clone -q --depth 1 https://github.com/ifesserra-lab/factor.git .deploy
	cp site/index.html .deploy/index.html
	touch .deploy/.nojekyll
	cd .deploy && git add -A && \
		(git diff --cached --quiet && echo "Nada a publicar — site já atualizado." || \
		(git commit -m "Atualiza dashboard com dados de $$(date +%d/%m/%Y)" && git push))
	rm -rf .deploy

clean: ## Remove artefatos gerados
	rm -rf output/ site/ .deploy/ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
