###############################################################################
# MODERATE ENVIRONMENT (MEDIUM RISK)
###############################################################################
resource "local_file" "mod_waf" {
  filename = "${path.module}/generated/moderate/waf.txt"
  content  = "resource_id: mod-waf-01\nresource_type: network\nexposure: internet\ntrust_level: medium\n"
}

resource "local_file" "mod_web" {
  filename = "${path.module}/generated/moderate/web.txt"
  content  = "resource_id: mod-web-01\nresource_type: compute\nexposure: internal\ntrust_level: medium\n"
}

resource "local_file" "mod_queue" {
  filename = "${path.module}/generated/moderate/queue.txt"
  content  = "resource_id: mod-queue-01\nresource_type: storage\nexposure: internal\ntrust_level: medium\n"
}

resource "local_file" "mod_worker" {
  filename = "${path.module}/generated/moderate/worker.txt"
  content  = "resource_id: mod-worker-01\nresource_type: compute\nexposure: internal\ntrust_level: medium\n"
}

resource "local_file" "mod_db" {
  filename = "${path.module}/generated/moderate/database.txt"
  content  = "resource_id: mod-db-01\nresource_type: database\nexposure: isolated\ntrust_level: high\nsensitivity: critical\n"
}

resource "local_file" "mod_bastion" {
  filename = "${path.module}/generated/moderate/bastion.txt"
  content  = "resource_id: mod-bastion-01\nresource_type: compute\nexposure: internet\ntrust_level: low\n"
}

resource "local_file" "mod_relationships" {
  filename = "${path.module}/generated/moderate/relationships.txt"
  content  = <<-EOT
    internet -> mod-waf-01 | network_access | HTTPS | 443
    mod-waf-01 -> mod-web-01 | network_access | HTTP | 8080
    mod-web-01 -> mod-db-01 | data_flow | TCP | 5432
    mod-web-01 -> mod-queue-01 | data_flow | TCP | 5672
    mod-queue-01 -> mod-worker-01 | data_flow | TCP | 5672
    mod-worker-01 -> mod-db-01 | data_flow | TCP | 5432
    internet -> mod-bastion-01 | administration | SSH | 22
    mod-bastion-01 -> mod-db-01 | administration | TCP | 5432
  EOT
  depends_on = [local_file.mod_waf, local_file.mod_web, local_file.mod_queue, local_file.mod_worker, local_file.mod_db, local_file.mod_bastion]
}
