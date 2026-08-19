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