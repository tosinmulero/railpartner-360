from pathlib import Path
import sys
import importlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_DIRECTORIES = [
    "data/raw",
    "data/external",
    "data/interim",
    "data/processed",
    "data/synthetic",
    "data/exports",
    "src/data_generation",
    "src/validation",
    "sql",
    "dbt",
    "powerbi",
    "reports",
    "docs",
    "tests",
]

REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "pyarrow",
    "polars",
    "sqlalchemy",
    "sklearn",
    "matplotlib",
    "yaml",
]

def main():
    print("=" * 60)
    print("RAILPARTNER 360 - ENVIRONMENT VALIDATION")
    print("=" * 60)

    print(f"\nProject root:\n{PROJECT_ROOT}")
    print(f"\nPython executable:\n{sys.executable}")
    print(f"\nPython version:\n{sys.version.split()[0]}")

    problems = []

    print("\nDIRECTORY CHECK")
    print("-" * 60)

    for directory in REQUIRED_DIRECTORIES:
        path = PROJECT_ROOT / directory

        if path.exists():
            print(f"[OK] {directory}")
        else:
            print(f"[MISSING] {directory}")
            problems.append(f"Missing directory: {directory}")

    print("\nPACKAGE CHECK")
    print("-" * 60)

    for package in REQUIRED_PACKAGES:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "installed")
            print(f"[OK] {package}: {version}")
        except Exception as exc:
            print(f"[FAILED] {package}: {exc}")
            problems.append(f"Package failure: {package}")

    print("\nCONFIGURATION CHECK")
    print("-" * 60)

    config_file = PROJECT_ROOT / "config.yaml"

    if config_file.exists():
        print("[OK] config.yaml")
    else:
        print("[MISSING] config.yaml")
        problems.append("Missing config.yaml")

    if problems:
        print("\nVALIDATION FAILED")
        print("-" * 60)

        for problem in problems:
            print(problem)

        raise SystemExit(1)

    print("\n" + "=" * 60)
    print("ENVIRONMENT VALIDATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
