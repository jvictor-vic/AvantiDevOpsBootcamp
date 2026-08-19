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