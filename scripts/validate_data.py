#!/usr/bin/env python
import _bootstrap

from paper_radar.validation import validate_public_outputs


def main() -> None:
    errors, warnings = validate_public_outputs()
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        raise SystemExit(1)
    print("Validation passed")


if __name__ == "__main__":
    main()
