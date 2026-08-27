###############################################################################
# SECURE ENVIRONMENT (ZERO-TRUST / LOW RISK)
###############################################################################
resource "local_file" "sec_waf" {
  filename = "${path.module}/generated/secure/waf.txt"
  content  = "resource_id: sec-waf-01\nresource_type: network\nexposure: internet\ntrust_level: high\n"
}

resource "local_file" "sec_gateway" {
  filename = "${path.module}/generated/secure/gateway.txt"
  content  = "resource_id: sec-gateway-01\nresource_type: network\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_app" {
  filename = "${path.module}/generated/secure/app.txt"
  content  = "resource_id: sec-app-01\nresource_type: compute\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_queue" {
  filename = "${path.module}/generated/secure/queue.txt"
  content  = "resource_id: sec-queue-01\nresource_type: storage\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_worker" {
  filename = "${path.module}/generated/secure/worker.txt"
  content  = "resource_id: sec-worker-01\nresource_type: compute\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_db_proxy" {
  filename = "${path.module}/generated/secure/db-proxy.txt"
  content  = "resource_id: sec-db-proxy-01\nresource_type: network\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_db" {
  filename = "${path.module}/generated/secure/database.txt"
  content  = "resource_id: sec-db-01\nresource_type: database\nexposure: isolated\ntrust_level: high\nsensitivity: critical\n"
}

resource "local_file" "sec_ztna" {
  filename = "${path.module}/generated/secure/ztna-gateway.txt"
  content  = "resource_id: sec-ztna-01\nresource_type: identity\nexposure: internet\ntrust_level: high\n"
}

resource "local_file" "sec_admin" {
  filename = "${path.module}/generated/secure/admin-service.txt"
  content  = "resource_id: sec-admin-01\nresource_type: compute\nexposure: internal\ntrust_level: high\n"
}

resource "local_file" "sec_relationships" {
  filename = "${path.module}/generated/secure/relationships.txt"
  content  = <<-EOT
    internet -> sec-waf-01 | network_access | HTTPS | 443
    sec-waf-01 -> sec-gateway-01 | network_access | HTTPS | 8443
    sec-gateway-01 -> sec-app-01 | network_access | HTTP | 8080
    sec-app-01 -> sec-db-proxy-01 | network_access | TCP | 5432
    sec-app-01 -> sec-queue-01 | data_flow | TCP | 5672
    sec-queue-01 -> sec-worker-01 | data_flow | TCP | 5672
    sec-worker-01 -> sec-db-proxy-01 | data_flow | TCP | 5432
    sec-db-proxy-01 -> sec-db-01 | network_access | TCP | 5432
    internet -> sec-ztna-01 | administration | HTTPS | 443
    sec-ztna-01 -> sec-admin-01 | administration | HTTPS | 8443
    sec-admin-01 -> sec-db-proxy-01 | administration | TCP | 5432
  EOT
  depends_on = [
    local_file.sec_waf, local_file.sec_gateway, local_file.sec_app,
    local_file.sec_queue, local_file.sec_worker, local_file.sec_db_proxy,
    local_file.sec_db, local_file.sec_ztna, local_file.sec_admin
  ]
}
