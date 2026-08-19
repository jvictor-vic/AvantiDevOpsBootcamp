output "backend_url" {
  value = render_web_service.backend.url
}

output "frontend_url" {
  value = render_web_service.frontend.url
}

output "landing_url" {
  value = "https://${data.netlify_site.landing.name}.netlify.app"
}