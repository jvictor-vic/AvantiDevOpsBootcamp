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