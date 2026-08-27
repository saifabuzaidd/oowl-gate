from typing import Dict, Any, List
from oowl.core.models.infrastructure import InfrastructureModel, Resource, Relationship, SecurityContext
from oowl.ingestion.errors import TerraformParseError


class TerraformParser:
    """Parses Terraform plan JSON into the canonical InfrastructureModel."""

    def parse(self, tf_json: Dict[str, Any]) -> InfrastructureModel:
        try:
            resources_data = tf_json.get("planned_values", {}).get("root_module", {}).get("resources", [])
            configuration_data = tf_json.get("configuration", {}).get("root_module", {}).get("resources", [])
        except AttributeError:
            raise TerraformParseError("Malformed Terraform JSON structure.")

        resources = self._extract_resources(resources_data)
        relationships = self._extract_relationships(configuration_data)

        # Determinism: Sort outputs strictly
        resources.sort(key=lambda r: r.id)
        relationships.sort(key=lambda r: (r.source, r.target))

        return InfrastructureModel(
            resources=resources,
            relationships=relationships,
            metadata={
                "source_format": "terraform",
                "version": tf_json.get("terraform_version", "unknown")
            }
        )

    def _extract_resources(self, resources_data: List[Dict[str, Any]]) -> List[Resource]:
        resources = []
        for res in resources_data:
            # Strictly avoid hallucinating SecurityContext
            sec_context = SecurityContext(
                exposure="UNKNOWN",
                sensitivity="UNKNOWN"
            )

            resources.append(Resource(
                id=res.get("address"),
                type=res.get("type"),
                name=res.get("name"),
                attributes=res.get("values", {}),
                security_context=sec_context
            ))

        return resources

    def _extract_relationships(self, config_data: List[Dict[str, Any]]) -> List[Relationship]:
        relationships = []

        for res in config_data:
            source = res.get("address")
            expressions = res.get("expressions", {})

            # Extract basic dependencies/references from expressions
            for attr, expr in expressions.items():
                if "references" in expr:
                    for ref in expr["references"]:
                        # 1. Ignore internal Terraform references
                        if ref.startswith(("var.", "local.", "data.", "path.")):
                            continue

                        # 2. Strip attribute access to get the base resource address
                        # e.g., 'local_file.vpc.filename' -> 'local_file.vpc'
                        parts = ref.split(".")
                        if len(parts) >= 2:
                            base_ref = f"{parts[0]}.{parts[1]}"
                        else:
                            base_ref = ref

                        if base_ref != source:
                            relationships.append(Relationship(
                                source=source,
                                target=base_ref,
                                relationship_type="REFERENCES"
                            ))

        # Remove duplicates while preserving order for determinism
        unique_rels = list({
            (r.source, r.target, r.relationship_type): r
            for r in relationships
        }.values())

        return unique_rels
