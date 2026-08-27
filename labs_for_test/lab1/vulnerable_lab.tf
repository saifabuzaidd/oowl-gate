###############################################################################
# VULNERABLE ENVIRONMENT (HIGH RISK)
###############################################################################
resource "local_file" "vuln_web" {
  filename = "${path.module}/generated/vulnerable/web.txt"
  content  = <<-EOT
    resource_id: vuln-web-01
    resource_type: compute
    exposure: internet
    trust_level: low
    inbound: { source: internet, port: 80 }
    outbound: { target: vuln-db-01 }
  EOT
}

resource "local_file" "vuln_db" {
  filename = "${path.module}/generated/vulnerable/database.txt"
  content  = <<-EOT
    resource_id: vuln-db-01
    resource_type: database
    exposure: internet
    trust_level: low
    sensitivity: critical
    data_classification: { pii: true, credentials: true }
    inbound: { source: internet, port: 5432 }
  EOT
}

resource "local_file" "vuln_bastion" {
  filename = "${path.module}/generated/vulnerable/bastion.txt"
  content  = <<-EOT
    resource_id: vuln-bastion-01
    resource_type: compute
    exposure: internet
    trust_level: low
    inbound: { source: internet, port: 22 }
    outbound: { target: vuln-bucket-01 }
  EOT
}

resource "local_file" "vuln_bucket" {
  filename = "${path.module}/generated/vulnerable/bucket.txt"
  content  = <<-EOT
    resource_id: vuln-bucket-01
    resource_type: storage
    exposure: internet
    trust_level: low
    sensitivity: high
    inbound: { source: internet, port: 443 }
  EOT
}

resource "local_file" "vuln_relationships" {
  filename = "${path.module}/generated/vulnerable/relationships.txt"
  content  = <<-EOT
    internet -> vuln-web-01 | network_access | HTTP | 80
    internet -> vuln-db-01 | network_access | TCP | 5432
    vuln-web-01 -> vuln-db-01 | data_flow | TCP | 5432
    internet -> vuln-bastion-01 | administration | SSH | 22
    vuln-bastion-01 -> vuln-bucket-01 | administration | HTTPS | 443
    internet -> vuln-bucket-01 | data_flow | HTTPS | 443
  EOT
  depends_on = [local_file.vuln_web, local_file.vuln_db, local_file.vuln_bastion, local_file.vuln_bucket]
}
