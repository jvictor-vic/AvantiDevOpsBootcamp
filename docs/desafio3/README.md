# 🏗️ Desafio 3 — Infraestrutura como Código (IaC) e Continuous Deployment (CD) com Terraform (Versão Mais Recente)

## 🎯 Objetivo

Evoluir a esteira de CI desenvolvida no **Desafio 2** para uma pipeline completa de **CI/CD (Continuous Integration & Continuous Deployment)** utilizando a **versão mais recente do Terraform (`>= 1.10.0` / `latest`)**.

Neste desafio, você utilizará o **Terraform** para provisionar e gerenciar a infraestrutura das 4 componentes da aplicação **CondoCombat** de forma automatizada, utilizando as **imagens Docker do Backend e do Frontend criadas no Desafio 2**, a **Landing Page criada no Desafio 1** e provedores de nuvem que **não exigem cartão de crédito para cadastro**:

1. 🗄️ **Banco de Dados (PostgreSQL)** — Provisionado via IaC no **Supabase**
2. 🏗️ **Backend (FastAPI)** — Deploy da imagem Docker do backend (`condocombat-backend:latest`) no **Render**
3. 🎨 **Frontend (Next.js)** — Deploy da imagem Docker do frontend (`condocombat-frontend:latest`) no **Render**
4. 🌐 **Landing Page (Astro)** — Deploy e gerenciamento via provider **Netlify** (`netlify/netlify`), substituindo o passo de deploy via Netlify CLI realizado no Desafio 1 pelo deploy automatizado via Terraform a partir do build da Landing Page.

> 💡 **Recomendação Importante aos Alunos**: O passo de deploy da Landing Page que utilizava a **Netlify CLI** (`netlify deploy`) no **Desafio 1** deve ser **removido** do job de CD das pipelines anteriores. No Desafio 3, a etapa de CI deve gerar os arquivos estáticos compilados (`landing/dist`) e o **Terraform** será o responsável por realizar o deploy desses arquivos na Netlify durante o estágio de CD.

---

## 🛠️ Providers Escolhidos (100% Gratuitos & Sem Cartão de Crédito)

| Stack | Serviço | Provider Terraform | Necessita Cartão? | Origem do Deploy | Papel no Projeto |
|-------|---------|---------------------|-------------------|------------------|------------------|
| 🗄️ **Database** | Supabase | `supabase/supabase` | ❌ **Não** | Instância Gerenciada | Banco de Dados PostgreSQL 16 para persistência dos dados do FastAPI. |
| 🏗️ **Backend** | Render | `render-oss/render` | ❌ **Não** | Imagem DockerHub (CI Desafio 2) | Execução da API FastAPI a partir da imagem Docker criada na esteira de CI. |
| 🎨 **Frontend** | Render | `render-oss/render` | ❌ **Não** | Imagem DockerHub (CI Desafio 2) | Execução do Frontend Next.js 14 a partir da imagem Docker criada na esteira de CI. |
| 🌐 **Landing Page** | Netlify | `netlify/netlify` | ❌ **Não** | Build `landing/dist` (CI Desafio 3) | Deploy e gestão de variáveis de ambiente da Landing Page Astro via Terraform. |

---

## 🔑 Como se Cadastrar e Obter Credenciais

### 1. 🗄️ Supabase (Banco de Dados PostgreSQL)
- **Cadastro Gratuito**: Acesse [Supabase Dashboard](https://supabase.com/dashboard/sign-in) e faça login via **GitHub** (não exige cartão de crédito).
- **Access Token**: Gere em [Account Settings > Access Tokens](https://supabase.com/dashboard/account/tokens) clicando em **Generate new token** (utilizado como `SUPABASE_ACCESS_TOKEN`).
- **Organization ID**: Obtenha em [Supabase Organizations](https://supabase.com/dashboard/organizations) copiando o ID da sua organização (utilizado em `database.tf`).

### 2. 🚀 Render (Backend e Frontend)
- **Cadastro Gratuito**: Acesse [Render Register](https://dashboard.render.com/register) e cadastre-se via **GitHub** (não exige cartão de crédito no plano gratuito).
- **API Key**: Gere em [Account Settings > API Keys](https://dashboard.render.com/u/settings#api-keys) clicando em **Create API Key** (utilizado como `RENDER_API_KEY`).
- **Owner ID**: Localize na tela de **Account Settings** ou na URL do Dashboard (`usr-xxxxxxxxxxxx` / `tea-xxxxxxxxxxxx`), utilizado como `RENDER_OWNER_ID`.

### 3. 🌐 Netlify (Landing Page)
- **Cadastro Gratuito**: Acesse [Netlify Sign Up](https://app.netlify.com/signup) e cadastre-se via **GitHub**.
- **Personal Access Token**: Acesse **User Settings > Applications > Personal access tokens**, clique em **New access token** (utilizado como `NETLIFY_AUTH_TOKEN` / `NETLIFY_API_TOKEN`).
- **Site Name / ID**: Obtenha o nome ou ID do site configurado na Netlify (utilizado em `landing.tf`).

---

## ⚙️ Versão do Terraform

A pipeline de CD está configurada para utilizar a **versão mais recente do Terraform**:

- **No código HCL (`terraform/providers.tf`)**: `required_version = ">= 1.10.0"`
- **No GitHub Actions**: `terraform_version: "latest"` na action `hashicorp/setup-terraform@v3`
- **No GitLab CI/CD**: Imagem de container oficial `hashicorp/terraform:latest`

---

## 🔄 Fluxo da Esteira CI/CD Completa

```
[ Git Push / PR na branch main ]
               │
               ▼
┌────────────────────────────────────────────────────────┐
│ 1. Etapa de CI                                         │
│    ├── Lint (Ruff / ESLint)                            │
│    ├── Testes (pytest / Vitest)                        │
│    ├── Build das imagens Docker (Backend e Frontend)   │
│    ├── Build da Landing Page (gera landing/dist)       │
│    └── Push das 2 imagens para o DockerHub             │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (Disparo do CD após sucesso no CI)
┌────────────────────────────────────────────────────────┐
│ 2. Etapa de CD com Terraform                           │
│    ├── terraform init (Terraform Latest)               │
│    ├── terraform plan                                  │
│    └── terraform apply (Deploy Backend, Frontend, DB  │
│        e Deploy do landing/dist na Netlify)            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Aplicação CondoCombat no Ar 🚀                      │
│    ├── Database: Supabase PostgreSQL (URL segura SSL)  │
│    ├── Backend: Render Web Service (https://api...)    │
│    ├── Frontend: Render Web Service (https://web...)   │
│    └── Landing Page: Netlify Site (https://landing...) │
└──────────────────────────┘
```

---

## ⚠️ Guia da Plataforma de CI/CD

Escolha o guia de acordo com a plataforma que você utilizou no Desafio 2:

| Plataforma | Guia de Implementação |
|-----------|------------------------|
| 🐙 **GitHub Actions** | [`README.github.md`](./README.github.md) |
| 🦊 **GitLab CI/CD** | [`README.gitlab.md`](./README.gitlab.md) |

---

## ✅ Entregáveis do Desafio 3

1. **Diretório `/terraform`**: Arquivos `.tf` funcionais compatíveis com a versão mais recente do Terraform (`>= 1.10.0`) contendo o provisionamento do Supabase, Render e Netlify.
2. **Remoção do Deploy por CLI**: Remoção do passo de deploy da Landing Page via CLI do Netlify no Desafio 1 e migração do deploy dos arquivos compilados (`landing/dist`) para a infraestrutura via Terraform.
3. **Configuração de Secrets e Variáveis de Ambiente**: Cadastro de credenciais e tokens da nuvem (`SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `RENDER_API_KEY`, `RENDER_OWNER_ID`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_NAME`, `DOCKERHUB_USERNAME`, `BACKEND_SECRET_KEY`) na plataforma de CI/CD escolhida.
4. **Pipeline de CD Integrada**: Pipeline de Continuous Deployment configurada para executar `terraform init`, `terraform plan` e `terraform apply -auto-approve` utilizando a versão mais recente do Terraform (`latest`).
5. **Aplicação Completa e Funcional**: URLs públicas no ar do Backend (API FastAPI) e Frontend (Next.js) rodando no Render conectados ao Banco de Dados PostgreSQL no Supabase, e a Landing Page no Netlify gerenciada via Terraform.

---

## 📚 Referências

- [Terraform Latest Documentation](https://developer.hashicorp.com/terraform/docs)
- [Terraform Registry — Render Provider](https://registry.terraform.io/providers/render-oss/render/latest/docs)
- [Terraform Registry — Supabase Provider](https://registry.terraform.io/providers/supabase/supabase/latest/docs)
- [Terraform Registry — Netlify Provider](https://registry.terraform.io/providers/netlify/netlify/latest/docs)
- [Render — Deploying Public Docker Images](https://render.com/docs/docker-images)

