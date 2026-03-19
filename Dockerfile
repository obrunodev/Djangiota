FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (necessárias para o Postgres/Psycopg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependência primeiro (aproveita o cache do Docker)
COPY pyproject.toml uv.lock ./

# Instala as dependências sem instalar o projeto em si
RUN uv sync --frozen --no-cache

# Copia o restante do código
COPY . .

# Comando padrão
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]