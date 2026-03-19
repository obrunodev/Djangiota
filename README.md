# 💰 Djangiota

Sistema financeiro para controle de empréstimos e gestão de crédito.

## 🛠️ Stack

- **Linguagem**: Python 3.12+
- **Framework**: Django 6
- **Banco**: PostgreSQL (Produção/Docker) | SQLite (Local)
- **Gerenciador**: uv
- **Configuração**: Pydantic Settings (.env)
- **Infra**: Docker & Docker Compose

## 📌 Requisitos

- uv (Gerenciador de pacotes)
- Docker & Docker Compose (Opcional para rodar localmente)
- Python 3.12

## 🚀 Como Rodar

### Opção 1: Com Docker (Recomendado)

O projeto já conta com um Makefile para facilitar os comandos:

```bash
make up        # Sobe os containers
make migrate   # Roda as migrações
make superuser # Cria o admin
```

### Opção 2: Sem Docker (Local)

Certifique-se de ter o arquivo .env configurado (se usar SQLite, deixe as variáveis de DB vazias ou comente-as no core/config.py).

**Instalar dependências:**

```bash
uv sync
```

**Rodar migrações:**

```bash
uv run python manage.py migrate
```

**Criar Admin:**

```bash
uv run python manage.py createsuperuser
```

**Iniciar servidor:**

```bash
uv run python manage.py runserver
```

## 🏗️ Estrutura

- **apps/**: Regras de negócio e apps Django.
- **core/**: Configurações globais e variáveis de ambiente.
- **Makefile**: Atalhos para produtividade.
