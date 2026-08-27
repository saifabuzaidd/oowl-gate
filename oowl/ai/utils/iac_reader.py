"""Utility module for recursively reading and aggregating raw IaC source code and fixture files."""

import os
from typing import Set

# Allowed file extensions capturing Terraform, CloudFormation/Ansible YAML, JSON, HCL, tfvars, and test fixtures
ALLOWED_EXTENSIONS: Set[str] = {
    ".tf",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".hcl",
    ".tfvars",
}


def read_raw_iac(directory_path: str) -> str:
    """Recursively scan and concatenate valid IaC definition files within a target directory.

    Args:
        directory_path: Absolute or relative filesystem path to the target source directory.

    Returns:
        A unified string payload containing aggregated file contents prefixed with file paths,
        or a system status message if the path is missing or yields no matching files.
    """
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return f"[SYSTEM MESSAGE] Warning: Directory '{directory_path}' not found or inaccessible."

    raw_text_parts = []

    # Deterministic recursive directory traversal to preserve prompt sequence across runs
    for root, _, files in sorted(os.walk(directory_path)):
        for file in sorted(files):
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                file_path = os.path.join(root, file)
                try:
                    # UTF-8 decoding with replacement prevents binary or invalid character crashes
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                        raw_text_parts.append(f"--- FILE: {file_path} ---\n{content}\n")
                except Exception as exc:
                    raw_text_parts.append(
                        f"--- FILE: {file_path} (ERROR READING: {str(exc)}) ---\n"
                    )

    if not raw_text_parts:
        return "[SYSTEM MESSAGE] No valid IaC files found."

    return "\n".join(raw_text_parts)
