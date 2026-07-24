# 🏗️ Desafio 3 — Terraform + CD do Backend, Frontend, Landing Page e Banco de Dados (GitHub Actions)

## 🎯 Objetivo

Estender a pipeline de **CI** criada no **Desafio 2** para uma pipeline completa de **CD (Continuous Deployment)** usando o **GitHub Actions** e o **Terraform na versão mais recente**.

Neste desafio, você irá reutilizar as **2 imagens Docker** publicadas no DockerHub durante a etapa de CI do Desafio 2 (`condocombat-backend` e `condocombat-frontend`), o build da **Landing Page** do Desafio 1 e fará o provisionamento e deploy via código (IaC):

1. **Banco de Dados PostgreSQL 16** via provider **Supabase** (ou Neon).
2. **Backend FastAPI** via provider **Render** (Web Service a partir da Imagem Docker do DockerHub).
3. **Frontend Next.js** via provider **Render** (Web Service a partir da Imagem Docker do DockerHub), injetando a URL da API gerada no Backend.
4. **Landing Page Astro** via provider **Netlify** (`netlify/netlify`) + recurso Terraform para realizar o deploy dos arquivos gerados pelo CI (`landing/dist`).

> ⚠️ **Atenção — Alteração em relação ao Desafio 1**:
> No **Desafio 1**, o deploy da Landing Page era executado diretamente pelo job de CD via CLI do Netlify (`netlify deploy`). **Neste Desafio 3, você deve remover esse passo de deploy por CLI**. A etapa de CI deve compilar o projeto (`npm run build` na pasta `landing/`, gerando a pasta `landing/dist`) e o **Terraform** será o responsável por realizar o deploy desses arquivos na Netlify durante a execução do `terraform apply`.

---

## 🛠️ Providers Escolhidos (Gratuitos & Sem Cartão de Crédito)

### 1. Banco de Dados: Supabase (`supabase/supabase`)
- **Plano**: Free Tier (500MB de banco PostgreSQL, 2 projetos).
- **Cadastro**: Via [Supabase Sign Up](https://supabase.com/dashboard/sign-in) com conta do GitHub (sem cartão de crédito).
- **Recurso Terraform**: `supabase_project` (cria a instância PostgreSQL e gera a String de Conexão).

### 2. Backend: Render (`render-oss/render`)
- **Plano**: Free Tier (Web Services gratuitos para containers).
- **Cadastro**: Via [Render Register](https://dashboard.render.com/register) com conta do GitHub/E-mail (sem cartão de crédito).
- **Recurso Terraform**: `render_service` com `runtime = "image"` apontando para `${DOCKERHUB_USERNAME}/condocombat-backend:latest` na porta 8000.

### 3. Frontend: Render (`render-oss/render`)
- **Plano**: Free Tier (Web Services gratuitos para containers).
- **Cadastro**: Mesmo cadastro do Render via [dashboard.render.com](https://dashboard.render.com).
- **Recurso Terraform**: `render_service` com `runtime = "image"` apontando para `${DOCKERHUB_USERNAME}/condocombat-frontend:latest` na porta 3000, recebendo a variável `NEXT_PUBLIC_API_URL`.

### 4. Landing Page: Netlify (`netlify/netlify`)
- **Plano**: Free Tier (Hospedagem gratuita de sites estáticos).
- **Cadastro**: Via [Netlify Sign Up](https://app.netlify.com/signup) com conta do GitHub.
- **Recurso Terraform**: `data "netlify_site"`, `netlify_environment_variable` e `terraform_data` (para orquestrar o deploy do `landing/dist` gerado pelo CI).

---

## 🔑 Passo a Passo para Obtenção de Credenciais e Tokens

### 🗄️ Supabase
1. **Cadastro/Login**: Acesse [Supabase Dashboard](https://supabase.com/dashboard/sign-in) e faça login via GitHub.
2. **Access Token**: Acesse [Account Settings > Access Tokens](https://supabase.com/dashboard/account/tokens), clique em **Generate new token** e salve para usar em `SUPABASE_ACCESS_TOKEN`.
3. **Organization ID**: Obtenha o ID da sua organização em [Supabase Organizations](https://supabase.com/dashboard/organizations) (usado em `database.tf`).

### 🚀 Render
1. **Cadastro/Login**: Acesse [Render Register](https://dashboard.render.com/register) e cadastre-se via GitHub.
2. **API Key**: Acesse [Account Settings > API Keys](https://dashboard.render.com/u/settings#api-keys), clique em **Create API Key** e salve para usar em `RENDER_API_KEY`.
3. **Owner ID**: Localize o seu ID em **Account Settings** ou no endereço da URL do Dashboard (salve para usar em `RENDER_OWNER_ID`).

### 🌐 Netlify
1. **Cadastro/Login**: Acesse [Netlify Sign Up](https://app.netlify.com/signup) e faça login via GitHub.
2. **Personal Access Token**: Acesse [User Settings > Applications > Personal Access Tokens](https://app.netlify.com/user/applications/personal-access-tokens), clique em **New access token** e salve para usar em `NETLIFY_AUTH_TOKEN`.
3. **Site Name**: Nome do site da Landing Page na Netlify para usar em `NETLIFY_SITE_NAME`.

---

## 📁 Estrutura de Arquivos Recomendada

No seu repositório, crie a seguinte estrutura dentro do diretório `terraform/`:

```
.
├── .github/
│   └── workflows/
│       ├── backend.yml       # (Do Desafio 2 — CI)
│       ├── frontend.yml      # (Do Desafio 2 — CI)
│       └── deploy.yml        # (NOVO — Pipeline CD com Terraform)
└── terraform/
    ├── providers.tf          # Configuração dos provedores (Terraform Latest)
    ├── variables.tf          # Variáveis de ambiente e secrets
    ├── database.tf           # Provisionamento do PostgreSQL (Supabase)
    ├── backend.tf            # Deploy do Container Backend (Render)
    ├── frontend.tf           # Deploy do Container Frontend (Render)
    ├── landing.tf            # Configuração e Deploy da Landing Page (Netlify)
    └── outputs.tf            # URLs geradas
```

---

## 📝 Código de Exemplo do Terraform (Utilizando Versão Mais Recente)

### 1. `terraform/providers.tf`

```hcl
terraform {
  # Requer a versão mais recente do Terraform (1.10.x ou superior)
  required_version = ">= 1.10.0"

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

### 2. `terraform/variables.tf`

```hcl
variable "dockerhub_username" {
  type        = string
  description = "Usuário do DockerHub onde as imagens foram publicadas no CI"
}

variable "supabase_access_token" {
  type        = string
  sensitive   = true
}

variable "supabase_db_password" {
  type        = string
  sensitive   = true
}

variable "render_api_key" {
  type        = string
  sensitive   = true
}

variable "render_owner_id" {
  type        = string
  sensitive   = true
}

variable "backend_secret_key" {
  type        = string
  sensitive   = true
}

variable "netlify_api_token" {
  type        = string
  sensitive   = true
  description = "Token de Acesso Pessoal da Netlify"
}

variable "netlify_site_name" {
  type        = string
  description = "Nome do site da Landing Page na Netlify"
  default     = "condocombat-landing"
}
```

### 3. `terraform/database.tf`

```hcl
resource "supabase_project" "db" {
  organization_id   = "sua-org-id-supabase"
  name              = "condocombat-db"
  database_password = var.supabase_db_password
  region            = "us-east-1"
}
```

### 4. `terraform/backend.tf`

```hcl
resource "render_service" "backend" {
  name    = "condocombat-backend-api"
  type    = "web_service"
  env     = "image"
  region  = "oregon"
  plan    = "free"

  image = {
    image_url = "docker.io/${var.dockerhub_username}/condocombat-backend:latest"
  }

  env_vars = {
    "DATABASE_URL" = {
      value = "postgresql://postgres:${var.supabase_db_password}@db.${supabase_project.db.id}.supabase.co:5432/postgres"
    }
    "SECRET_KEY" = {
      value = var.backend_secret_key
    }
    "CORS_ORIGINS" = {
      value = "*"
    }
    "PORT" = {
      value = "8000"
    }
  }
}
```

### 5. `terraform/frontend.tf`

```hcl
resource "render_service" "frontend" {
  name    = "condocombat-frontend-web"
  type    = "web_service"
  env     = "image"
  region  = "oregon"
  plan    = "free"

  image = {
    image_url = "docker.io/${var.dockerhub_username}/condocombat-frontend:latest"
  }

  env_vars = {
    "NEXT_PUBLIC_API_URL" = {
      value = render_service.backend.url
    }
    "PORT" = {
      value = "3000"
    }
  }
}
```

### 6. `terraform/landing.tf`

```hcl
# Busca a referência do site da Landing Page na Netlify
data "netlify_site" "landing" {
  name = var.netlify_site_name
}

# Configura a variável de ambiente PUBLIC_APP_URL com a URL gerada para o Frontend (Render)
resource "netlify_environment_variable" "landing_public_url" {
  site_id = data.netlify_site.landing.id
  key     = "PUBLIC_APP_URL"
  values = [
    {
      value   = render_service.frontend.url
      context = "all"
    }
  ]
}

# Fazer o deploy dos arquivos compilados (landing/dist) gerados no CI via Terraform
resource "terraform_data" "landing_deploy" {
  triggers_replace = [
    data.netlify_site.landing.id,
    render_service.frontend.url
  ]

  provisioner "local-exec" {
    command = "npx netlify-cli deploy --dir=${path.module}/../landing/dist --prod --auth=${var.netlify_api_token} --site=${data.netlify_site.landing.id}"
  }

  depends_on = [
    netlify_environment_variable.landing_public_url
  ]
}
```

### 7. `terraform/outputs.tf`

```hcl
output "backend_url" {
  value = render_service.backend.url
}

output "frontend_url" {
  value = render_service.frontend.url
}

output "landing_url" {
  value = "https://${data.netlify_site.landing.name}.netlify.app"
}
```

---

## ⚙️ Passo a Passo da Pipeline no GitHub Actions (Terraform Latest)

Crie o arquivo `.github/workflows/deploy.yml` configurado para baixar a **versão mais recente do Terraform**.

> 💡 Note que a pipeline realiza o build da Landing Page no estagio de preparação antes do Terraform executar, permitindo que a pasta `landing/dist` esteja disponível para o deploy feito pelo Terraform.

```yaml
name: 🚀 Continuous Deployment (CD) — Terraform (Latest)

on:
  workflow_run:
    workflows: ["Backend CI", "Frontend CI", "Deploy Landing Page"]
    types:
      - completed
    branches:
      - main

jobs:
  terraform-deploy:
    name: 🏗️ Provisionar e Fazer Deploy da Infraestrutura
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout do código
        uses: actions/checkout@v4

      - name: ⚙️ Setup Node.js (para build da Landing Page)
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: 📦 Build da Landing Page
        run: |
          cd landing
          npm ci
          npm run build

      - name: ⚙️ Configurar a Versão Mais Recente do Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "latest"

      - name: 🔍 Terraform Init
        run: terraform init
        working-directory: ./terraform

      - name: 📋 Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: ./terraform
        env:
          TF_VAR_dockerhub_username: ${{ secrets.DOCKERHUB_USERNAME }}
          TF_VAR_supabase_access_token: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          TF_VAR_supabase_db_password: ${{ secrets.SUPABASE_DB_PASSWORD }}
          TF_VAR_render_api_key: ${{ secrets.RENDER_API_KEY }}
          TF_VAR_render_owner_id: ${{ secrets.RENDER_OWNER_ID }}
          TF_VAR_backend_secret_key: ${{ secrets.BACKEND_SECRET_KEY }}
          TF_VAR_netlify_api_token: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          TF_VAR_netlify_site_name: ${{ secrets.NETLIFY_SITE_NAME }}

      - name: 🚀 Terraform Apply
        run: terraform apply -auto-approve tfplan
        working-directory: ./terraform
        env:
          TF_VAR_dockerhub_username: ${{ secrets.DOCKERHUB_USERNAME }}
          TF_VAR_supabase_access_token: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          TF_VAR_supabase_db_password: ${{ secrets.SUPABASE_DB_PASSWORD }}
          TF_VAR_render_api_key: ${{ secrets.RENDER_API_KEY }}
          TF_VAR_render_owner_id: ${{ secrets.RENDER_OWNER_ID }}
          TF_VAR_backend_secret_key: ${{ secrets.BACKEND_SECRET_KEY }}
          TF_VAR_netlify_api_token: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          TF_VAR_netlify_site_name: ${{ secrets.NETLIFY_SITE_NAME }}
```

---

## ✅ Entregáveis do Desafio 3

1. **Diretório `/terraform`** contendo os arquivos `.tf` funcionais compatíveis com a versão mais recente do Terraform (`>= 1.10.0`).
2. **Remoção do deploy manual por CLI**: Retirar o job `cd` com Netlify CLI das pipelines do Desafio 1.
3. **Secrets no GitHub**: `DOCKERHUB_USERNAME`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `RENDER_API_KEY`, `RENDER_OWNER_ID`, `BACKEND_SECRET_KEY`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_NAME`.
4. **Pipeline de CD `.github/workflows/deploy.yml`** usando `terraform_version: "latest"`.
5. **URLs no ar**: Links públicos do Backend e Frontend rodando no Render conectados ao Supabase e Landing Page no Netlify via Terraform.
