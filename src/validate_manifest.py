#!/usr/bin/env python3
"""
Manifest Validator
Validates artifacts/manifest.yaml against schema requirements.
Checks for required fields, valid enums, and format compliance.
"""

import yaml
import sys
from datetime import datetime
from pathlib import Path

# Schema validation rules
VALID_STATES = {"current", "historical", "proposed", "unknown"}
VALID_CATEGORIES = {"architecture", "process", "data", "communication", "decision"}
VALID_CONFIDENCE = {"verified", "inferred", "assumed"}
VALID_SCAN_RESULTS = {"clean", "quarantined", "pending"}

REQUIRED_FIELDS = {
    "filename": str,
    "source": str,
    "date": str,
    "state": str,
    "owner": str,
    "category": str,
    "confidence": str,
    "scan_result": str,
}

OPTIONAL_FIELDS = {
    "notes": str,
    "extracted_to": (str, type(None)),
    "tags": list,
}


def validate_date(date_str):
    """Check if date is in YYYY-MM-DD format and valid."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_artifact(artifact, artifact_num):
    """Validate a single artifact entry."""
    errors = []

    # Check required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in artifact:
            errors.append(f"  Artifact {artifact_num}: Missing required field '{field}'")
        elif not isinstance(artifact[field], expected_type):
            errors.append(
                f"  Artifact {artifact_num}: Field '{field}' must be {expected_type.__name__}, got {type(artifact[field]).__name__}"
            )

    # Check optional fields
    for field, expected_types in OPTIONAL_FIELDS.items():
        if field in artifact:
            if not isinstance(expected_types, tuple):
                expected_types = (expected_types,)
            if not isinstance(artifact[field], expected_types):
                type_names = " or ".join(t.__name__ for t in expected_types)
                errors.append(
                    f"  Artifact {artifact_num}: Field '{field}' must be {type_names}, got {type(artifact[field]).__name__}"
                )

    # Validate enums
    if "state" in artifact and artifact["state"] not in VALID_STATES:
        errors.append(
            f"  Artifact {artifact_num}: Invalid state '{artifact['state']}'. Must be one of: {', '.join(VALID_STATES)}"
        )

    if "category" in artifact and artifact["category"] not in VALID_CATEGORIES:
        errors.append(
            f"  Artifact {artifact_num}: Invalid category '{artifact['category']}'. Must be one of: {', '.join(VALID_CATEGORIES)}"
        )

    if "confidence" in artifact and artifact["confidence"] not in VALID_CONFIDENCE:
        errors.append(
            f"  Artifact {artifact_num}: Invalid confidence '{artifact['confidence']}'. Must be one of: {', '.join(VALID_CONFIDENCE)}"
        )

    if "scan_result" in artifact and artifact["scan_result"] not in VALID_SCAN_RESULTS:
        errors.append(
            f"  Artifact {artifact_num}: Invalid scan_result '{artifact['scan_result']}'. Must be one of: {', '.join(VALID_SCAN_RESULTS)}"
        )

    # Validate date format
    if "date" in artifact and not validate_date(artifact["date"]):
        errors.append(
            f"  Artifact {artifact_num}: Invalid date format '{artifact['date']}'. Must be YYYY-MM-DD"
        )

    return errors


def validate_manifest(manifest_path):
    """Validate manifest.yaml file."""
    try:
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: Manifest file not found: {manifest_path}")
        return False
    except yaml.YAMLError as e:
        print(f"ERROR: Invalid YAML in manifest: {e}")
        return False

    errors = []

    # Check top-level structure
    if "artifacts" not in manifest:
        errors.append("ERROR: Missing 'artifacts' key in manifest")
        print("\n".join(errors))
        return False

    if not isinstance(manifest["artifacts"], list):
        errors.append("ERROR: 'artifacts' must be a list")
        print("\n".join(errors))
        return False

    # Validate each artifact
    for i, artifact in enumerate(manifest["artifacts"], 1):
        if not isinstance(artifact, dict):
            errors.append(f"ERROR: Artifact {i} must be a dictionary")
            continue
        errors.extend(validate_artifact(artifact, i))

    # Check metadata (optional)
    if "metadata" in manifest and isinstance(manifest["metadata"], dict):
        if "total_artifacts" in manifest["metadata"]:
            expected_count = manifest["metadata"]["total_artifacts"]
            actual_count = len(manifest["artifacts"])
            if expected_count != actual_count:
                errors.append(
                    f"WARNING: metadata.total_artifacts ({expected_count}) != actual artifacts ({actual_count})"
                )

    if errors:
        print("Manifest validation FAILED:\n")
        print("\n".join(errors))
        return False

    print("✓ Manifest validation PASSED")
    print(f"  Total artifacts: {len(manifest['artifacts'])}")
    print(
        f"  State distribution: {sum(1 for a in manifest['artifacts'] if a['state'] == 'current')} current, {sum(1 for a in manifest['artifacts'] if a['state'] == 'historical')} historical"
    )
    print(
        f"  Scan results: {sum(1 for a in manifest['artifacts'] if a['scan_result'] == 'clean')} clean, {sum(1 for a in manifest['artifacts'] if a['scan_result'] == 'pending')} pending, {sum(1 for a in manifest['artifacts'] if a['scan_result'] == 'quarantined')} quarantined"
    )
    return True


if __name__ == "__main__":
    manifest_path = Path(__file__).parent.parent / "artifacts" / "manifest.yaml"
    success = validate_manifest(manifest_path)
    sys.exit(0 if success else 1)
