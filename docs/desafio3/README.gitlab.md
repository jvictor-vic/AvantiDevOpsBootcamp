# 🏗️ Desafio 3 — Terraform + CD do Backend, Frontend, Landing Page e Banco de Dados (GitLab CI/CD)

## 🎯 Objetivo

Estender a pipeline de **CI** criada no **Desafio 2** para uma pipeline completa de **CD (Continuous Deployment)** usando o **GitLab CI/CD** e o **Terraform na versão mais recente**.

Neste desafio você reutilizará as **2 imagens Docker** publicadas no DockerHub durante a etapa de CI do Desafio 2 (`condocombat-backend` e `condocombat-frontend`), o build da **Landing Page** do Desafio 1 e fará o provisionamento e deploy via código (IaC):

1. Armazenar o **Terraform State** no **GitLab Managed Terraform State**.
2. Provisionar o banco **PostgreSQL 16** via provider **Supabase** (ou Neon).
3. Fazer o deploy do **Backend FastAPI** via provider **Render** usando o container Docker do DockerHub.
4. Fazer o deploy do **Frontend Next.js** via provider **Render** usando o container Docker do DockerHub conectado à API.
5. Fazer o deploy da **Landing Page Astro** via provider **Netlify** (`netlify/netlify`) + recurso Terraform para publicar os arquivos gerados pelo CI (`landing/dist`).

> ⚠️ **Atenção — Alteração em relação ao Desafio 1**:
> No **Desafio 1**, o deploy da Landing Page era executado diretamente pela CLI da Netlify no pipeline de CI/CD. **Neste Desafio 3, o aluno deve remover o passo de deploy via Netlify CLI**. O pipeline de CI continuará gerando os arquivos compilados (`landing/dist`) e o **Terraform** será o responsável por realizar o deploy desses arquivos na Netlify durante a execução do `terraform apply`.

---

## 🛠️ Providers Escolhidos (Gratuitos & Sem Cartão de Crédito)

| Stack | Serviço | Link de Cadastro | Provider Terraform | Vantagem do Provider |
|-------|---------|------------------|---------------------|----------------------|
| 🗄️ **Database** | Supabase | [supabase.com](https://supabase.com/dashboard/sign-in) | `supabase/supabase` | Instância isolada de PostgreSQL 16 com SSL sem cartão. |
| 🏗️ **Backend** | Render | [render.com](https://dashboard.render.com/register) | `render-oss/render` | Deploy direto do container Docker da API vindo do DockerHub sem cartão. |
| 🎨 **Frontend** | Render | [render.com](https://dashboard.render.com/register) | `render-oss/render` | Deploy direto do container Docker do Frontend vindo do DockerHub sem cartão. |
| 🌐 **Landing Page** | Netlify | [netlify.com](https://app.netlify.com/signup) | `netlify/netlify` | Gestão de variáveis de ambiente e deploy da Landing Page via Terraform. |

---

## 🔑 Passo a Passo para Obtenção de Credenciais e Tokens

### 🗄️ Supabase
1. **Cadastro/Login**: Acesse [Supabase Dashboard](https://supabase.com/dashboard/sign-in) e faça login via GitHub.
2. **Access Token**: Acesse [Account Settings > Access Tokens](https://supabase.com/dashboard/account/tokens), clique em **Generate new token** e salve para cadastrar na variável `SUPABASE_ACCESS_TOKEN`.
3. **Organization ID**: Obtenha o ID da sua organização em [Supabase Organizations](https://supabase.com/dashboard/organizations) (usado em `database.tf`).

### 🚀 Render
1. **Cadastro/Login**: Acesse [Render Register](https://dashboard.render.com/register) e cadastre-se via GitHub.
2. **API Key**: Acesse [Account Settings > API Keys](https://dashboard.render.com/u/settings#api-keys), clique em **Create API Key** e salve para cadastrar na variável `RENDER_API_KEY`.
3. **Owner ID**: Localize o seu ID em **Account Settings** ou no endereço da URL do Dashboard (salve para cadastrar na variável `RENDER_OWNER_ID`).

### 🌐 Netlify
1. **Cadastro/Login**: Acesse [Netlify Sign Up](https://app.netlify.com/signup) e faça login via GitHub.
2. **Personal Access Token**: Acesse [User Settings > Applications > Personal Access Tokens](https://app.netlify.com/user/applications/personal-access-tokens), clique em **New access token** e salve para cadastrar na variável `NETLIFY_AUTH_TOKEN`.
3. **Site Name**: Nome do site da Landing Page na Netlify para cadastrar na variável `NETLIFY_SITE_NAME`.

---

## 📁 Estrutura de Arquivos Recomendada

```
.
├── .gitlab-ci.yml            # Pipeline Principal (Integra CI do Desafio 2 + CD do Desafio 3)
├── .gitlab-ci/
│   ├── backend.yml           # (CI do Backend)
│   ├── frontend.yml          # (CI do Frontend)
│   └── deploy.yml            # (NOVO — CD com Terraform Latest)
└── terraform/
    ├── providers.tf          # Provedores e Backend HTTP do GitLab State (Terraform Latest)
    ├── variables.tf          # Variáveis
    ├── database.tf           # Supabase Postgres
    ├── backend.tf            # Container Docker Backend no Render
    ├── frontend.tf           # Container Docker Frontend no Render
    ├── landing.tf            # Landing Page no Netlify
    └── outputs.tf            # URLs expostas
```

---

## ⚙️ Configuração do State Nativo do GitLab (`terraform/providers.tf`)

```hcl
terraform {
  # Requer a versão mais recente do Terraform (1.10.x ou superior)
  required_version = ">= 1.10.0"

  backend "http" {}

  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
    render = {
      source  = "render-oss/render"
      version = "~> 1.3"
    }
    netlify = {
      source  = "netlify/netlify"
      version = "~> 0.4"
    }
  }
}

provider "supabase" {
  access_token = var.supabase_access_token
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

provider "netlify" {
  token = var.netlify_api_token
}
```

---

## ⚙️ Pipeline GitLab CI/CD com Imagem Oficial Latest (`.gitlab-ci/deploy.yml`)

```yaml
stages:
  - lint
  - test
  - build
  - deploy

deploy:terraform:
  stage: deploy
  image:
    name: hashicorp/terraform:latest
    entrypoint: [""]
  before_script:
    - apk add --no-search --no-cache nodejs npm
    - cd landing && npm ci && npm run build && cd ..
  script:
    - cd terraform
    - terraform init -backend-config="address=${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production" -backend-config="lock_address=${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production/lock" -backend-config="unlock_address=${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/terraform/state/production/lock" -backend-config="username=gitlab-ci-token" -backend-config="password=${CI_JOB_TOKEN}" -backend-config="lock_method=POST" -backend-config="unlock_method=DELETE" -backend-config="retry_wait_min=5"
    - terraform plan -out=tfplan
    - terraform apply -auto-approve tfplan
  variables:
    TF_VAR_dockerhub_username: "${DOCKERHUB_USERNAME}"
    TF_VAR_supabase_access_token: "${SUPABASE_ACCESS_TOKEN}"
    TF_VAR_supabase_db_password: "${SUPABASE_DB_PASSWORD}"
    TF_VAR_render_api_key: "${RENDER_API_KEY}"
    TF_VAR_render_owner_id: "${RENDER_OWNER_ID}"
    TF_VAR_backend_secret_key: "${BACKEND_SECRET_KEY}"
    TF_VAR_netlify_api_token: "${NETLIFY_AUTH_TOKEN}"
    TF_VAR_netlify_site_name: "${NETLIFY_SITE_NAME}"
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
```

---

## 🔐 Variáveis de Ambiente no GitLab (CI/CD Variables)

Cadastre em **Settings > CI/CD > Variables**:
- `DOCKERHUB_USERNAME`
- `SUPABASE_ACCESS_TOKEN` (Masked)
- `SUPABASE_DB_PASSWORD` (Masked)
- `RENDER_API_KEY` (Masked)
- `RENDER_OWNER_ID` (Masked)
- `BACKEND_SECRET_KEY` (Masked)
- `NETLIFY_AUTH_TOKEN` (Masked)
- `NETLIFY_SITE_NAME`

---

## ✅ Entregáveis do Desafio 3

1. **Diretório `/terraform`** contendo os arquivos `.tf` funcionais compatíveis com a versão mais recente do Terraform (`>= 1.10.0`).
2. **Remoção do deploy por Netlify CLI**: Retirar o deploy do Desafio 1 da pipeline e migrar para o Terraform.
3. **Variáveis de CI/CD no GitLab**: `DOCKERHUB_USERNAME`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `RENDER_API_KEY`, `RENDER_OWNER_ID`, `BACKEND_SECRET_KEY`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_NAME`.
4. **GitLab Managed Terraform State** funcionando via backend HTTP nativo do GitLab.
5. **Pipeline de CD `.gitlab-ci/deploy.yml`** usando a imagem oficial `hashicorp/terraform:latest`.
6. **URLs no ar**: Links públicos do Backend e Frontend rodando no Render conectados ao Supabase e Landing Page no Netlify via Terraform.
