resource "render_web_service" "frontend" {
  name   = "condocombat-frontend-web"
  region = "oregon"
  plan   = "free"


  runtime_source = {
    image = {
      image_url = "docker.io/${var.dockerhub_username}/condocombat-frontend"

      tag = "latest"
    }
  }

  env_vars = {
    "NEXT_PUBLIC_API_URL" = {
      value = render_web_service.backend.url
    }
    "PORT" = {
      value = "3000"
    }
  }
}
