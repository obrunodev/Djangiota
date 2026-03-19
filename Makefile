# Variáveis para facilitar a manutenção
COMPOSE = docker compose
EXEC_WEB = $(COMPOSE) exec web
PYTHON = uv run python
MANAGE = $(PYTHON) manage.py

.PHONY: help up down restart logs migrate migrations shell superuser test clean

help: ## Mostra os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Sobe os containers em background
	$(COMPOSE) up -d

down: ## Derruba os containers
	$(COMPOSE) down

restart: down up ## Reinicia os containers

logs: ## Mostra os logs do container web em tempo real
	$(COMPOSE) logs -f web

migrations: ## Cria novas migrações baseadas nos models
	$(EXEC_WEB) $(MANAGE) makemigrations

migrate: ## Aplica as migrações no banco de dados
	$(EXEC_WEB) $(MANAGE) migrate

shell: ## Abre o shell interativo do Django
	$(EXEC_WEB) $(MANAGE) shell

superuser: ## Cria um superusuário (o Agiota Master)
	$(EXEC_WEB) $(MANAGE) createsuperuser

test: ## Executa os testes automatizados
	$(EXEC_WEB) $(PYTHON) pytest

clean: ## Limpa arquivos temporários do Python e cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete