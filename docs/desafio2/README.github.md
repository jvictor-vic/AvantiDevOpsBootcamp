# 🏗️ Desafio 2 — Docker + CI/CD do Backend e Frontend (CondoCombat)

## 🎯 Objetivo

Criar **Dockerfiles** e um **docker-compose.yml** para o backend (FastAPI) e frontend (Next.js) do CondoCombat, e configurar uma pipeline de **Integração Contínua (CI)** no GitHub Actions que executa lint, testes, build e push das imagens para o **DockerHub**.

A pipeline deve:

1. **Executar lint** no backend (Ruff) e frontend (ESLint)
2. **Executar testes automatizados** (pytest + vitest)
3. **Fazer o build das imagens Docker** e **publicar no DockerHub**

Pipeline configurada para **GitHub Actions**.

---

## 📦 Sobre o Projeto

### Backend (FastAPI)

| Item | Detalhe |
|------|---------|
| Framework | FastAPI + Python 3.12 |
| Porta | 8000 |
| Testes | pytest-asyncio (216 testes) |
| Lint | Ruff |
| Comando teste | `pytest` |
| Comando lint | `ruff check app/` |
| Pasta do Dockerfile | `backend/` |

### Frontend (Next.js)

| Item | Detalhe |
|------|---------|
| Framework | Next.js 14 + TypeScript strict |
| Porta | 3000 |
| Testes | Vitest + Testing Library (79 testes) |
| Lint | ESLint (next lint) |
| Comando teste | `npm run test` |
| Comando lint | `npm run lint` |
| Pasta do Dockerfile | `frontend/` |

---

## 📋 Pré-requisitos

- [ ] Conta no [DockerHub](https://hub.docker.com/)
- [ ] Repositório no [GitHub](https://github.com)
- [ ] Docker instalado localmente (opcional, para testes)

---

## 🔐 Variáveis de Ambiente (Secrets)

Configure as seguintes variáveis como **secrets** no repositório (Settings → Secrets and variables → Actions):

| Variável | Descrição | Onde conseguir |
|----------|-----------|---------------|
| `DOCKERHUB_USERNAME` | Nome de usuário do DockerHub | DockerHub → Account Settings |
| `DOCKERHUB_TOKEN` | Token de acesso ao DockerHub | DockerHub → Account Settings → Security → New Access Token |
| `SECRET_KEY` | Chave secreta para JWT do backend | Gerar com `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |

### Como gerar o `DOCKERHUB_TOKEN`

1. Acesse [hub.docker.com](https://hub.docker.com) e faça login
2. Vá em **Account Settings** (foto do canto superior direito) → **Security**
3. Em **Access Tokens**, clique em **New Access Token**
4. Dê um nome (ex: `github-actions-condocombat`), selecione permissão **Read & Write**
5. Copie o token gerado (você não poderá vê-lo novamente)
6. Adicione como secret no repositório com o nome `DOCKERHUB_TOKEN`

### Como gerar a `SECRET_KEY`

O backend do CondoCombat usa uma chave secreta para assinar tokens JWT. Gere uma com Python:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Copie o resultado e adicione como secret no repositório com o nome `SECRET_KEY`.

> ⚠️ A `SECRET_KEY` é **obrigatória**. O backend valida na inicialização e **crasha** se não for definida.

---

## 🏗️ Criando o Dockerfile do Backend

Crie o arquivo `backend/Dockerfile` com **multi-stage build**:

### Etapas

1. **Stage 1 (builder)**: Instala as dependências Python do `requirements.txt`
2. **Stage 2 (runtime)**: Cópia mínima dos artefatos, configura entrada com migrations + uvicorn

### `backend/Dockerfile`

```dockerfile
# =============================================================================
# Stage 1: Builder — instala dependências
# =============================================================================
FROM python:3.12-slim AS builder

# Define diretório de trabalho
WORKDIR /app

# Copia apenas o requirements.txt primeiro (aproveita cache do Docker)
COPY requirements.txt .

# Instala dependências em um diretório global
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime — imagem final enxuta
# =============================================================================
FROM python:3.12-slim AS runtime

# Cria usuário não-root para segurança
RUN addgroup --system app && adduser --system --ingroup app app

# Define diretório de trabalho
WORKDIR /app

# Copia as dependências instaladas do stage builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia o código da aplicação
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Copia o entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expõe a porta da aplicação
EXPOSE 8000

# Health check: verifica se a API responde
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Muda para usuário não-root
USER app

# Entrypoint: roda migrations antes de iniciar o servidor
ENTRYPOINT ["./entrypoint.sh"]
```

### `backend/entrypoint.sh`

Crie também o arquivo `backend/entrypoint.sh`:

```bash
#!/bin/bash
# =============================================================================
# entrypoint.sh — Executa migrations e inicia o servidor
# =============================================================================
set -e

echo ">>> Executando migrations do banco de dados..."
alembic upgrade head

echo ">>> Iniciando servidor FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> ⚠️ Dê permissão de execução: `chmod +x backend/entrypoint.sh`

### Explicação linha a linha

| Linha | O que faz |
|-------|-----------|
| `FROM python:3.12-slim AS builder` | Imagem base leve para instalar dependências |
| `WORKDIR /app` | Define o diretório de trabalho |
| `COPY requirements.txt .` | Copia apenas o arquivo de dependências |
| `RUN pip install ...` | Instala todas as dependências |
| `FROM python:3.12-slim AS runtime` | Segunda etapa — imagem final |
| `addgroup / adduser` | Cria usuário não-root (`app`) |
| `COPY --from=builder ...` | Copia pacotes Python do builder |
| `COPY app/ app/` | Copia o código da aplicação |
| `COPY entrypoint.sh .` | Copia o script de entrada |
| `EXPOSE 8000` | Documenta a porta |
| `HEALTHCHECK` | Verifica periodicamente se a API está saudável |
| `USER app` | Muda para usuário não-root |
| `ENTRYPOINT ["./entrypoint.sh"]` | Executa o entrypoint |

---

## 🏗️ Criando o Dockerfile do Frontend

Crie o arquivo `frontend/Dockerfile` com **multi-stage build** em 3 estágios:

### Etapas

1. **Stage 1 (deps)**: Instala dependências com `npm ci`
2. **Stage 2 (builder)**: Compila o Next.js com `npm run build`
3. **Stage 3 (runner)**: Imagem final apenas com o necessário para produção

### `frontend/Dockerfile`

```dockerfile
# =============================================================================
# Stage 1: Dependencies — instala node_modules
# =============================================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copia apenas os arquivos de dependências (aproveita cache)
COPY package.json package-lock.json ./

# Instala dependências exatas do lockfile
RUN npm ci

# =============================================================================
# Stage 2: Builder — compila a aplicação
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copia node_modules do stage deps
COPY --from=deps /app/node_modules ./node_modules

# Copia o código fonte
COPY . .

# Compila o Next.js (gera .next/)
RUN npm run build

# =============================================================================
# Stage 3: Runner — imagem final de produção
# =============================================================================
FROM node:20-alpine AS runner

# Cria usuário não-root para segurança
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copia os artefatos do build
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Instala apenas dependências de produção (sem devDependencies)
RUN npm ci --omit=dev

# Expõe a porta da aplicação
EXPOSE 3000

# Health check: verifica se o servidor responde
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Muda para usuário não-root
USER app

# Inicia o servidor Next.js em modo produção
CMD ["npm", "start"]
```

### Explicação de cada stage

| Stage | O que faz |
|-------|-----------|
| **deps** | Instala `node_modules` com `npm ci` (instalação exata do lockfile, mais rápida e determinística que `npm install`) |
| **builder** | Copia node_modules do deps + código fonte, executa `npm run build` para gerar a pasta `.next/` |
| **runner** | Copia apenas `.next/`, `public/`, `package.json` e instala só deps de produção. Imagem final leve (~200MB vs ~1.5GB com devDeps) |

---

## 🐳 Criando o docker-compose.yml

Crie o arquivo `docker-compose.yml` na **raiz do projeto** (`condocombat/docker-compose.yml`).

### `docker-compose.yml`

```yaml
# =============================================================================
# CondoCombat — Stack completa (PostgreSQL + API + Frontend)
# =============================================================================
services:

  # ---------------------------------------------------------------------------
  # Banco de Dados — PostgreSQL 16
  # ---------------------------------------------------------------------------
  db:
    image: postgres:16-alpine
    container_name: condocombat-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-condocombat}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-condocombat}
      POSTGRES_DB: ${POSTGRES_DB:-condocombat}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-condocombat} -d ${POSTGRES_DB:-condocombat}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ---------------------------------------------------------------------------
  # API — FastAPI (backend)
  # ---------------------------------------------------------------------------
  api:
    build:
      context: ./backend
    container_name: condocombat-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-condocombat}:${POSTGRES_PASSWORD:-condocombat}@db:5432/${POSTGRES_DB:-condocombat}
      CORS_ORIGINS: ${CORS_ORIGINS:-http://localhost:3000}
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

  # ---------------------------------------------------------------------------
  # Frontend — Next.js (web)
  # ---------------------------------------------------------------------------
  web:
    build:
      context: ./frontend
    container_name: condocombat-web
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://localhost:8000}
    depends_on:
      api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

# ---------------------------------------------------------------------------
# Volumes
# ---------------------------------------------------------------------------
volumes:
  pgdata:
```

### Explicação de cada serviço

| Serviço | Função | Depende de | Porta |
|---------|--------|------------|-------|
| **db** | PostgreSQL 16 Alpine — banco de dados relacional | — | 5432 |
| **api** | FastAPI — backend com migrations automáticas | db (saudável) | 8000 |
| **web** | Next.js — frontend SPA | api (saudável) | 3000 |

### Variáveis de ambiente

O `docker-compose.yml` usa o padrão `${VAR:-default}`. Isso permite:

1. Criar um arquivo `.env` na raiz com os valores reais
2. Usar os defaults para desenvolvimento local rápido

```bash
# Crie o .env a partir do exemplo
cp .env.example .env

# Edite com sua SECRET_KEY
# O resto já tem defaults funcionais para Docker Compose
```

---

## 📝 Pipeline CI/CD

Crie o arquivo `.github/workflows/ci-cd.yml` no repositório:

```yaml
name: CI/CD - Backend & Frontend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'frontend/**'
      - '.github/workflows/ci-cd.yml'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'
      - 'frontend/**'
      - '.github/workflows/ci-cd.yml'

jobs:
  # ---------------------------------------------------------------------------
  # Lint do Backend (Ruff)
  # ---------------------------------------------------------------------------
  lint-backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar Ruff
        run: pip install ruff

      - name: Executar lint
        run: ruff check app/

  # ---------------------------------------------------------------------------
  # Lint do Frontend (ESLint)
  # ---------------------------------------------------------------------------
  lint-frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: ./frontend/package-lock.json

      - name: Instalar dependências
        run: npm ci

      - name: Executar lint
        run: npm run lint

  # ---------------------------------------------------------------------------
  # Testes do Backend (pytest)
  # ---------------------------------------------------------------------------
  test-backend:
    needs: [lint-backend]
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependências
        run: pip install -r requirements.txt

      - name: Executar testes
        run: pytest
        env:
          SECRET_KEY: ${{ secrets.SECRET_KEY }}

  # ---------------------------------------------------------------------------
  # Testes do Frontend (Vitest)
  # ---------------------------------------------------------------------------
  test-frontend:
    needs: [lint-frontend]
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: ./frontend/package-lock.json

      - name: Instalar dependências
        run: npm ci

      - name: Executar testes
        run: npm run test

  # ---------------------------------------------------------------------------
  # Build e Push da imagem do Backend para o DockerHub
  # ---------------------------------------------------------------------------
  build-and-push-backend:
    needs: [test-backend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login no DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build e Push
        uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/condocombat-api:latest

  # ---------------------------------------------------------------------------
  # Build e Push da imagem do Frontend para o DockerHub
  # ---------------------------------------------------------------------------
  build-and-push-frontend:
    needs: [test-frontend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login no DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build e Push
        uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/condocombat-web:latest
```

### Explicação dos jobs

| Job | Responsabilidade | Depende de |
|-----|-----------------|------------|
| `lint-backend` | Verifica estilo do código Python com Ruff | — |
| `lint-frontend` | Verifica estilo do código TypeScript/React com ESLint | — |
| `test-backend` | Executa 216 testes do backend com pytest | `lint-backend` |
| `test-frontend` | Executa 79 testes do frontend com Vitest | `lint-frontend` |
| `build-and-push-backend` | Build da imagem Docker do backend e push para DockerHub | `test-backend` |
| `build-and-push-frontend` | Build da imagem Docker do frontend e push para DockerHub | `test-frontend` |

### Fluxo da pipeline

```
lint-backend ──► test-backend ──► build-and-push-backend
                                                      │
lint-frontend ─► test-frontend ──► build-and-push-frontend
```

Os jobs de lint rodam em paralelo. Cada um alimenta seu respectivo job de teste. Só após os testes passarem, o build e push são executados.

### Gatilhos (`on.push.paths`)

A pipeline é acionada apenas quando há mudanças em:

- `backend/**` — qualquer arquivo do backend
- `frontend/**` — qualquer arquivo do frontend
- `.github/workflows/ci-cd.yml` — o próprio workflow

Isso evita rodar a pipeline quando a landing page (`landing/`) é alterada.

---

## 🐳 Rodando o Stack Local com Docker Compose

Depois que a pipeline publicar as imagens (ou durante o desenvolvimento), você pode rodar o stack completo localmente:

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd condocombat

# 2. Crie o arquivo .env a partir do exemplo
cp .env.example .env

# 3. Edite o .env com sua SECRET_KEY
#    Gere uma com: python -c 'import secrets; print(secrets.token_urlsafe(32))'
#    E cole no campo SECRET_KEY=

# 4. Inicie todos os serviços
docker compose up -d

# 5. Verifique se está tudo funcionando
curl http://localhost:8000/health
# Deve retornar: {"status":"ok"}

curl http://localhost:3000
# Deve retornar a página inicial do CondoCombat

# 6. Acompanhe os logs
docker compose logs -f

# 7. Para parar e remover os containers
docker compose down -v
```

### Comandos úteis

```bash
# Ver status dos serviços
docker compose ps

# Rebuild de um serviço específico
docker compose build api

# Executar um comando dentro de um container
docker compose exec api alembic upgrade head

# Ver logs de um serviço específico
docker compose logs api -f

# Parar sem remover volumes (dados persistem)
docker compose down
```

---

## ✅ Critérios de Avaliação

| Critério | Peso | Descrição |
|----------|------|-----------|
| Dockerfile do Backend | 15% | Multi-stage, entrypoint com migrations, HEALTHCHECK, não-root |
| Dockerfile do Frontend | 15% | Multi-stage, otimizado (sem dev deps), não-root |
| docker-compose.yml | 15% | 3 serviços, health checks, volumes, variáveis de ambiente |
| Pipeline CI/CD | 25% | 6 jobs, dependências corretas, lint → test → build → push |
| Testes e Lint passando | 20% | Pipeline verde em todas as etapas |
| Organização e clareza | 10% | Código limpo, boas práticas, secrets configurados |

---

## 📚 Referências

- [DockerHub — Repositórios](https://hub.docker.com/)
- [Docker — Boas práticas para Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Login Action](https://github.com/marketplace/actions/docker-login)
- [Docker Build and Push Action](https://github.com/marketplace/actions/build-and-push-docker-images)
- [GitHub Actions — Documentação](https://docs.github.com/en/actions)
- [act — Execute GitHub Actions localmente](https://github.com/nektos/act)
- [FastAPI — Deploy com Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js — Docker Image](https://nextjs.org/docs/pages/building-your-application/deploying#docker-image)
- [CondoCombat — Backend](../../backend/)
- [CondoCombat — Frontend](../../frontend/)

---

## 💡 Dicas

1. **Monorepo**: Use `paths` no GitHub Actions para evitar execuções desnecessárias quando só a landing page mudar. A pipeline já está configurada com isso.
2. **Teste local com act**: Use [act](https://github.com/nektos/act) para testar a pipeline localmente antes de fazer push:
   ```bash
   act --job lint-backend --container-architecture linux/amd64
   ```
3. **DockerHub Token**: Prefira tokens de acesso em vez de senha. Crie em DockerHub → Account Settings → Security. Tokens são mais seguros e podem ser revogados individualmente.
4. **Tags**: Use tags semânticas (`v1.0.0`, `v1.1.0`) em vez de `latest` para produção. O `latest` é suficiente para este desafio, mas em projetos reais prefira versionamento.
5. **entrypoint.sh**: Não esqueça de dar permissão de execução: `chmod +x backend/entrypoint.sh`. Sem isso o container vai falhar ao iniciar.
6. **SECRET_KEY**: O backend valida a SECRET_KEY na inicialização. Se não for definida, o container vai crashar com um `ValueError`. Sempre defina essa variável.
7. **Cache do Docker**: A ordem das instruções no Dockerfile importa. Coloque `COPY requirements.txt` antes do código fonte para aproveitar o cache de camadas do Docker.
8. **Volumes do PostgreSQL**: O volume `pgdata` garante que os dados do banco persistem entre reinicializações. Use `docker compose down -v` com cuidado — isso apaga o volume.
