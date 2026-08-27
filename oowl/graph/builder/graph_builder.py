import networkx as nx
from typing import Set

class GraphBuilder:
    @staticmethod
    def build(model: 'InfrastructureModel') -> nx.MultiDiGraph:
        """
        Builds a deterministic directed multigraph from the InfrastructureModel.
        Input model is read-only. No shared data is mutated.
        """
        graph = nx.MultiDiGraph()
        
        # 1. Deterministic Node Addition
        # Sorting guarantees identical inputs yield identical internal graph node ordering
        sorted_resources = sorted(model.resources, key=lambda r: r.id)
        valid_node_ids: Set[str] = set()
        
        for resource in sorted_resources:
            graph.add_node(
                resource.id, 
                type=resource.type, 
                name=resource.name, 
                **resource.attributes
            )
            valid_node_ids.add(resource.id)
            
        # 2. Deterministic Edge Addition
        # Sorting by source, then target, then relationship type
        sorted_relationships = sorted(
            model.relationships, 
            key=lambda r: (r.source, r.target, r.relationship_type)
        )
        
        for rel in sorted_relationships:
            # Integrity check: Do not hallucinate relationships to non-existent nodes
            if rel.source in valid_node_ids and rel.target in valid_node_ids:
                graph.add_edge(
                    rel.source, 
                    rel.target, 
                    key=rel.relationship_type, 
                    relationship_type=rel.relationship_type
                )
                
        return graph

