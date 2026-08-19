resource "supabase_project" "db" {
  organization_id   = "bbivqgjybwkwiaerukui"
  name              = "condocombat-db"
  database_password = var.supabase_db_password
  region            = "sa-east-1"
}