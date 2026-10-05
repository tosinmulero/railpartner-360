from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXTENSIONS = {
    ".json",
    ".tmdl",
    ".pbip",
    ".pbir",
    ".pbism",
    ".py",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
}

fixed = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if path.suffix.lower() not in EXTENSIONS:
        continue

    if any(part in SKIP_DIRS for part in path.parts):
        continue

    try:
        raw = path.read_bytes()

        if raw.startswith(b"\xef\xbb\xbf"):

            path.write_bytes(
                raw[3:]
            )

            fixed.append(path)

            print(
                f"[FIXED] {path.relative_to(ROOT)}"
            )

    except OSError as exc:

        print(
            f"[SKIPPED] {path}: {exc}"
        )


print()
print("=" * 72)
print("UTF-8 BOM CLEANUP COMPLETE")
print("=" * 72)
print(f"Files cleaned: {len(fixed)}")