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