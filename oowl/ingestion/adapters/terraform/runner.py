import subprocess
import json
import os
from oowl.ingestion.errors import TerraformExecutionError

class TerraformRunner:
    """Executes the Terraform lifecycle to produce the normalized JSON plan."""
    
    def __init__(self, source_dir: str):
        if not os.path.isdir(source_dir):
            raise TerraformExecutionError(f"Source directory does not exist: {source_dir}")
        self.source_dir = source_dir

    def _run_cmd(self, cmd: list[str]) -> subprocess.CompletedProcess:
        try:
            result = subprocess.run(
                cmd,
                cwd=self.source_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            raise TerraformExecutionError(f"Command '{' '.join(cmd)}' failed:\n{e.stderr}")
        except FileNotFoundError:
            raise TerraformExecutionError("Terraform executable not found in PATH.")

    def generate_plan_json(self) -> dict:
        """Runs init, plan, and show to extract the infrastructure state."""
        self._run_cmd(["terraform", "init", "-no-color"])
        self._run_cmd(["terraform", "validate", "-no-color"])
        self._run_cmd(["terraform", "plan", "-out=tfplan", "-no-color"])
        
        show_result = self._run_cmd(["terraform", "show", "-json", "tfplan"])
        
        try:
            return json.loads(show_result.stdout)
        except json.JSONDecodeError as e:
            raise TerraformExecutionError(f"Failed to parse Terraform JSON output: {e}")

