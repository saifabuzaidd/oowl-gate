from oowl.core.models.infrastructure import InfrastructureModel
from oowl.ingestion.adapters.terraform.runner import TerraformRunner
from oowl.ingestion.adapters.terraform.parser import TerraformParser
from oowl.ingestion.errors import UnsupportedIaCFormatError

def ingest(source: str, format: str = "terraform") -> InfrastructureModel:
    """
    Main entry point for the Ingestion Engine.
    Transforms an IaC directory into a normalized InfrastructureModel.
    """
    if format.lower() != "terraform":
        raise UnsupportedIaCFormatError(f"Format '{format}' is not currently supported.")
    
    # 1. Run IaC Execution
    runner = TerraformRunner(source_dir=source)
    tf_json = runner.generate_plan_json()
    
    # 2. Parse and Normalize
    parser = TerraformParser()
    model = parser.parse(tf_json)
    
    return model
