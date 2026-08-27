terraform {
  required_version = ">= 1.6.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

###############################################################################
# OWL-GATE REALISTIC LOCAL IaC SECURITY LAB
#
# Purpose:
#   Simulate a production-like multi-tier infrastructure without provisioning
#   any real cloud resources.
#
# This configuration intentionally contains:
#   - Public-facing resources
#   - Internal services
#   - Critical databases
#   - Administrative plane
#   - Backup infrastructure
#   - Multiple dependency/data-flow relationships
#   - Intentionally weak trust boundaries
#   - Strong/isolated resources
#
# The configuration is INPUT to OwlGate.
# OwlGate must infer the normalized InfrastructureModel from this IaC.
###############################################################################


###############################################################################
# GLOBAL CONFIGURATION
###############################################################################

locals {

  environment = "production"

  region = "local-lab"

  organization = "owlgate-lab"

  security_zones = {
    edge        = "public"
    application = "internal"
    data        = "restricted"
    admin       = "administrative"
    backup      = "isolated"
  }

  common_tags = {
    environment = "production"
    managed_by  = "terraform"
    project     = "owlgate-security-lab"
  }
}


###############################################################################
# NETWORK FOUNDATION
###############################################################################

resource "local_file" "network_vpc" {
  filename = "${path.module}/generated/network-vpc.txt"

  content = <<-EOT
    resource_id: network-vpc
    resource_type: network
    name: production-vpc
    provider: local
    environment: production

    cidr: 10.0.0.0/16

    security_zone: network
    exposure: internal
    trust_level: high
    sensitivity: high

    purpose: primary production network
  EOT
}


resource "local_file" "public_subnet" {
  filename = "${path.module}/generated/public-subnet.txt"

  content = <<-EOT
    resource_id: subnet-public
    resource_type: network
    name: public-subnet
    provider: local

    cidr: 10.0.10.0/24

    parent_network: ${local_file.network_vpc.filename}

    security_zone: edge
    exposure: internet
    trust_level: low
    sensitivity: medium

    purpose: internet-facing workloads
  EOT
}


resource "local_file" "application_subnet" {
  filename = "${path.module}/generated/application-subnet.txt"

  content = <<-EOT
    resource_id: subnet-application
    resource_type: network
    name: application-subnet
    provider: local

    cidr: 10.0.20.0/24

    parent_network: ${local_file.network_vpc.filename}

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    purpose: application workloads
  EOT
}


resource "local_file" "database_subnet" {
  filename = "${path.module}/generated/database-subnet.txt"

  content = <<-EOT
    resource_id: subnet-database
    resource_type: network
    name: database-subnet
    provider: local

    cidr: 10.0.30.0/24

    parent_network: ${local_file.network_vpc.filename}

    security_zone: data
    exposure: isolated
    trust_level: high
    sensitivity: critical

    purpose: production databases
  EOT
}


resource "local_file" "admin_subnet" {
  filename = "${path.module}/generated/admin-subnet.txt"

  content = <<-EOT
    resource_id: subnet-admin
    resource_type: network
    name: administrative-subnet
    provider: local

    cidr: 10.0.40.0/24

    parent_network: ${local_file.network_vpc.filename}

    security_zone: admin
    exposure: internal
    trust_level: high
    sensitivity: critical

    purpose: privileged administrative workloads
  EOT
}


resource "local_file" "backup_subnet" {
  filename = "${path.module}/generated/backup-subnet.txt"

  content = <<-EOT
    resource_id: subnet-backup
    resource_type: network
    name: backup-subnet
    provider: local

    cidr: 10.0.50.0/24

    parent_network: ${local_file.network_vpc.filename}

    security_zone: backup
    exposure: isolated
    trust_level: high
    sensitivity: critical

    purpose: immutable backup infrastructure
  EOT
}


###############################################################################
# EDGE / INTERNET-FACING LAYER
###############################################################################

resource "local_file" "waf" {
  filename = "${path.module}/generated/waf.txt"

  content = <<-EOT
    resource_id: waf-01
    resource_type: network
    name: production-waf
    provider: local

    security_zone: edge
    exposure: internet
    trust_level: medium
    sensitivity: high

    inbound:
      source: internet
      protocol: HTTPS
      port: 443

    purpose: web application firewall
  EOT

  depends_on = [
    local_file.public_subnet
  ]
}


resource "local_file" "web" {
  filename = "${path.module}/generated/web.txt"

  content = <<-EOT
    resource_id: web-01
    resource_type: compute
    name: public-web-server
    provider: local

    security_zone: edge
    exposure: internet
    trust_level: low
    sensitivity: medium

    subnet: ${local_file.public_subnet.filename}

    inbound:
      source: internet
      protocol: HTTPS
      port: 443

    outbound:
      target: api-01
      protocol: HTTPS
      port: 8443

    purpose: public customer-facing web application
  EOT

  depends_on = [
    local_file.waf
  ]
}


###############################################################################
# API / APPLICATION LAYER
###############################################################################

resource "local_file" "api_gateway" {
  filename = "${path.module}/generated/api-gateway.txt"

  content = <<-EOT
    resource_id: api-gateway-01
    resource_type: network
    name: internal-api-gateway
    provider: local

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    inbound:
      source: web-01
      protocol: HTTPS
      port: 8443

    outbound:
      target: api-01
      protocol: HTTP
      port: 8080

    purpose: internal API gateway
  EOT

  depends_on = [
    local_file.application_subnet,
    local_file.web
  ]
}


resource "local_file" "api" {
  filename = "${path.module}/generated/api.txt"

  content = <<-EOT
    resource_id: api-01
    resource_type: compute
    name: customer-api
    provider: local

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    inbound:
      source: api-gateway-01
      protocol: HTTP
      port: 8080

    outbound:
      worker: worker-01
      cache: redis-01
      database_proxy: db-proxy-01

    purpose: customer business API
  EOT

  depends_on = [
    local_file.api_gateway
  ]
}


resource "local_file" "worker" {
  filename = "${path.module}/generated/worker.txt"

  content = <<-EOT
    resource_id: worker-01
    resource_type: compute
    name: background-worker
    provider: local

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    inbound:
      source: api-01
      protocol: TCP
      port: 9000

    outbound:
      target: db-proxy-01
      protocol: TCP
      port: 5432

    purpose: asynchronous business processing
  EOT

  depends_on = [
    local_file.api
  ]
}


###############################################################################
# CACHE / MESSAGE LAYER
###############################################################################

resource "local_file" "redis" {
  filename = "${path.module}/generated/redis.txt"

  content = <<-EOT
    resource_id: redis-01
    resource_type: storage
    name: production-redis
    provider: local

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    inbound:
      source: api-01
      protocol: TCP
      port: 6379

    data_classification:
      contains_session_data: true
      contains_cache_data: true

    purpose: session and application cache
  EOT

  depends_on = [
    local_file.application_subnet
  ]
}


resource "local_file" "queue" {
  filename = "${path.module}/generated/queue.txt"

  content = <<-EOT
    resource_id: queue-01
    resource_type: storage
    name: production-message-queue
    provider: local

    security_zone: application
    exposure: internal
    trust_level: medium
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    inbound:
      source: api-01
      protocol: TCP
      port: 5672

    outbound:
      target: worker-01

    purpose: asynchronous message transport
  EOT

  depends_on = [
    local_file.api,
    local_file.worker
  ]
}


###############################################################################
# DATABASE ACCESS LAYER
###############################################################################

resource "local_file" "db_proxy" {
  filename = "${path.module}/generated/db-proxy.txt"

  content = <<-EOT
    resource_id: db-proxy-01
    resource_type: network
    name: production-database-proxy
    provider: local

    security_zone: data
    exposure: internal
    trust_level: high
    sensitivity: critical

    subnet: ${local_file.database_subnet.filename}

    inbound:
      source:
        - api-01
        - worker-01
      protocol: TCP
      port: 5432

    outbound:
      target: db-01
      protocol: TCP
      port: 5432

    purpose: controlled database access layer
  EOT

  depends_on = [
    local_file.database_subnet,
    local_file.api,
    local_file.worker
  ]
}


###############################################################################
# CRITICAL DATABASE
###############################################################################

resource "local_file" "database" {
  filename = "${path.module}/generated/database.txt"

  content = <<-EOT
    resource_id: db-01
    resource_type: database
    name: production-customer-database
    provider: local

    environment: production

    security_zone: data
    exposure: isolated
    trust_level: high
    sensitivity: critical

    subnet: ${local_file.database_subnet.filename}

    protocol: PostgreSQL
    port: 5432

    data_classification:
      customer_records: true
      financial_records: true
      credentials: true
      pii: true

    allowed_sources:
      - db-proxy-01
      - admin-01

    purpose: primary production customer database
  EOT

  depends_on = [
    local_file.db_proxy
  ]
}


###############################################################################
# BACKUP / DISASTER RECOVERY
###############################################################################

resource "local_file" "backup" {
  filename = "${path.module}/generated/backup.txt"

  content = <<-EOT
    resource_id: backup-01
    resource_type: storage
    name: production-database-backup
    provider: local

    security_zone: backup
    exposure: isolated
    trust_level: high
    sensitivity: critical

    subnet: ${local_file.backup_subnet.filename}

    source:
      - db-01

    protection:
      immutable: true
      encryption: true
      retention_days: 90

    purpose: disaster recovery backup
  EOT

  depends_on = [
    local_file.database,
    local_file.backup_subnet
  ]
}


###############################################################################
# ADMINISTRATIVE PLANE
###############################################################################

resource "local_file" "bastion" {
  filename = "${path.module}/generated/bastion.txt"

  content = <<-EOT
    resource_id: bastion-01
    resource_type: compute
    name: administrative-bastion
    provider: local

    security_zone: admin
    exposure: internet
    trust_level: low
    sensitivity: high

    subnet: ${local_file.public_subnet.filename}

    inbound:
      source: internet
      protocol: SSH
      port: 22

    outbound:
      target: admin-01
      protocol: SSH
      port: 22

    security_note:
      intentionally_public: true
      purpose: administrative jump host

    purpose: privileged administrative entry point
  EOT

  depends_on = [
    local_file.public_subnet
  ]
}


resource "local_file" "admin" {
  filename = "${path.module}/generated/admin.txt"

  content = <<-EOT
    resource_id: admin-01
    resource_type: identity
    name: production-admin-service
    provider: local

    security_zone: admin
    exposure: internal
    trust_level: high
    sensitivity: critical

    subnet: ${local_file.admin_subnet.filename}

    inbound:
      source: bastion-01
      protocol: SSH
      port: 22

    privileged_permissions:
      manage_database: true
      read_customer_data: true
      modify_production: true
      manage_backups: true

    outbound:
      target: db-01

    purpose: privileged production administration
  EOT

  depends_on = [
    local_file.bastion,
    local_file.admin_subnet
  ]
}


###############################################################################
# SECURITY / IDENTITY SERVICES
###############################################################################

resource "local_file" "identity" {
  filename = "${path.module}/generated/identity.txt"

  content = <<-EOT
    resource_id: identity-01
    resource_type: identity
    name: production-identity-service
    provider: local

    security_zone: admin
    exposure: internal
    trust_level: high
    sensitivity: critical

    subnet: ${local_file.admin_subnet.filename}

    capabilities:
      authentication: true
      authorization: true
      service_accounts: true
      privileged_access: true

    consumers:
      - api-01
      - admin-01

    purpose: centralized identity and access management
  EOT

  depends_on = [
    local_file.admin_subnet
  ]
}


###############################################################################
# MONITORING / SECURITY OPERATIONS
###############################################################################

resource "local_file" "monitoring" {
  filename = "${path.module}/generated/monitoring.txt"

  content = <<-EOT
    resource_id: monitoring-01
    resource_type: storage
    name: security-monitoring
    provider: local

    security_zone: internal
    exposure: internal
    trust_level: high
    sensitivity: high

    subnet: ${local_file.application_subnet.filename}

    collects:
      - web-01
      - api-01
      - worker-01
      - bastion-01
      - admin-01
      - db-01

    purpose: centralized security telemetry
  EOT

  depends_on = [
    local_file.application_subnet
  ]
}


###############################################################################
# EXPLICIT RELATIONSHIP MANIFEST
#
# These resources intentionally make infrastructure relationships explicit.
# The ingestion layer must normalize them into Relationship objects.
###############################################################################

resource "local_file" "relationship_manifest" {
  filename = "${path.module}/generated/relationships.txt"

  content = <<-EOT
    # EDGE
    web-01 -> api-gateway-01 | network_access | HTTPS | 8443
    waf-01 -> web-01         | network_access | HTTPS | 443

    # APPLICATION
    api-gateway-01 -> api-01 | network_access | HTTP | 8080
    api-01 -> worker-01      | network_access | TCP | 9000
    api-01 -> redis-01       | network_access | TCP | 6379
    api-01 -> queue-01       | data_flow | AMQP | 5672
    queue-01 -> worker-01    | data_flow | AMQP | 5672

    # DATABASE
    worker-01 -> db-proxy-01 | network_access | TCP | 5432
    api-01 -> db-proxy-01    | network_access | TCP | 5432
    db-proxy-01 -> db-01     | network_access | TCP | 5432

    # BACKUP
    db-01 -> backup-01       | data_flow | INTERNAL | 0

    # ADMINISTRATIVE PLANE
    bastion-01 -> admin-01   | administration | SSH | 22
    admin-01 -> db-01        | administration | PostgreSQL | 5432

    # IDENTITY
    identity-01 -> api-01    | administration | HTTPS | 443
    identity-01 -> admin-01  | administration | HTTPS | 443

    # MONITORING
    web-01 -> monitoring-01  | data_flow | HTTPS | 443
    api-01 -> monitoring-01  | data_flow | HTTPS | 443
    db-01 -> monitoring-01   | data_flow | HTTPS | 443
    bastion-01 -> monitoring-01 | data_flow | HTTPS | 443
  EOT

  depends_on = [
    local_file.web,
    local_file.api,
    local_file.worker,
    local_file.database,
    local_file.backup,
    local_file.bastion,
    local_file.admin,
    local_file.identity,
    local_file.monitoring
  ]
}


###############################################################################
# SECURITY POLICY / POSTURE DOCUMENT
#
# This is intentionally infrastructure metadata, not OwlGate logic.
###############################################################################

resource "local_file" "security_posture" {
  filename = "${path.module}/generated/security-posture.txt"

  content = <<-EOT
    OWL-GATE SECURITY LAB
    =====================

    CRITICAL ASSETS
    ---------------
    db-01
    admin-01
    identity-01
    backup-01

    PUBLIC ASSETS
    ------------
    web-01
    waf-01
    bastion-01

    TRUSTED ASSETS
    --------------
    db-proxy-01
    db-01
    admin-01
    identity-01
    backup-01
    monitoring-01

    INTENTIONALLY WEAK BOUNDARIES
    ------------------------------
    Internet -> web-01
    Internet -> bastion-01
    bastion-01 -> admin-01
    admin-01 -> db-01

    EXPECTED SECURITY PATHS
    -----------------------
    web-01 -> api-gateway-01 -> api-01 -> db-proxy-01 -> db-01

    bastion-01 -> admin-01 -> db-01

    PROTECTED PATH
    --------------
    db-01 -> backup-01

    SECURITY OBJECTIVES
    -------------------
    1. Internet-facing resources must not directly reach critical assets.
    2. Administrative access must be tightly controlled.
    3. Critical database access must traverse the database proxy.
    4. Backup infrastructure must remain isolated.
    5. Identity services must remain highly trusted.
    6. Monitoring should observe security-sensitive resources.
  EOT

  depends_on = [
    local_file.relationship_manifest
  ]
}


###############################################################################
# OUTPUTS
###############################################################################

output "lab_environment" {
  value = local.environment
}

output "resource_count" {
  value = 22
}

output "critical_assets" {
  value = [
    "db-01",
    "admin-01",
    "identity-01",
    "backup-01"
  ]
}

output "public_assets" {
  value = [
    "web-01",
    "waf-01",
    "bastion-01"
  ]
}

output "relationship_manifest" {
  value = local_file.relationship_manifest.filename
}

output "security_posture" {
  value = local_file.security_posture.filename
}
