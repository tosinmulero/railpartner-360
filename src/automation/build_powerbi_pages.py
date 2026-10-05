from __future__ import annotations

from pathlib import Path
import copy
import hashlib
import json
import shutil


# ============================================================
# RAILPARTNER 360
# STAGE 8E — FIVE PBIR REPORT PAGES
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

REPORT_DEFINITION = (
    ROOT
    / "powerbi"
    / "RailPartner_360.Report"
    / "definition"
)

PAGES_DIR = REPORT_DEFINITION / "pages"

PAGES_JSON = PAGES_DIR / "pages.json"

BACKUP_DIR = (
    ROOT
    / "powerbi"
    / "backups"
    / "stage8e_native_report"
)


PAGE_NAMES = [
    "Executive Overview",
    "Partner Performance",
    "Customer & Conversion",
    "Routes & Operations",
    "Refund & Commercial Risk",
]


def write_json(path: Path, data: dict):

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def make_page_id(display_name: str):

    return hashlib.sha1(
        (
            "railpartner360::"
            + display_name
        ).encode("utf-8")
    ).hexdigest()[:20]


print("=" * 72)
print("RAILPARTNER 360 — STAGE 8E")
print("BUILD FIVE PBIR REPORT PAGES")
print("=" * 72)


# ============================================================
# VERIFY EXISTING NATIVE PAGE
# ============================================================

native_pages = [
    folder
    for folder in PAGES_DIR.iterdir()
    if folder.is_dir()
    and (folder / "page.json").exists()
]

if not native_pages:

    raise RuntimeError(
        "No native Power BI page found."
    )

native_page = native_pages[0]

native_page_json = (
    native_page
    / "page.json"
)

template = json.loads(
    native_page_json.read_text(
        encoding="utf-8-sig"
    )
)

print()
print(
    "[OK] Native template page:"
    f" {native_page.name}"
)

print(
    "[OK] Native page schema:"
    f" {template.get('$schema')}"
)

print(
    "[OK] Canvas:"
    f" {template.get('width')}"
    f" x {template.get('height')}"
)


# ============================================================
# BACKUP REPORT DEFINITION
# ============================================================

if not BACKUP_DIR.exists():

    shutil.copytree(
        REPORT_DEFINITION,
        BACKUP_DIR,
    )

    print(
        "[OK] Native report backup created"
    )

else:

    print(
        "[OK] Native report backup already exists"
    )


# ============================================================
# READ NATIVE pages.json
# ============================================================

pages_metadata = json.loads(
    PAGES_JSON.read_text(
        encoding="utf-8-sig"
    )
)


# ============================================================
# KEEP ORIGINAL PAGE AS EXECUTIVE OVERVIEW
# ============================================================

page_ids = []

first_name = PAGE_NAMES[0]
first_id = native_page.name

page_ids.append(first_id)

first_definition = copy.deepcopy(
    template
)

first_definition["name"] = (
    first_id
)

first_definition["displayName"] = (
    first_name
)

first_definition["displayOption"] = (
    "FitToPage"
)

first_definition["width"] = 1920
first_definition["height"] = 1080

write_json(
    native_page_json,
    first_definition,
)

(native_page / "visuals").mkdir(
    exist_ok=True
)

print(
    f"[PAGE] {first_name}"
)


# ============================================================
# CREATE REMAINING FOUR PAGES
# ============================================================

for display_name in PAGE_NAMES[1:]:

    page_id = make_page_id(
        display_name
    )

    page_ids.append(
        page_id
    )

    page_folder = (
        PAGES_DIR
        / page_id
    )

    if page_folder.exists():

        shutil.rmtree(
            page_folder
        )

    shutil.copytree(
        native_page,
        page_folder,
    )

    definition = copy.deepcopy(
        template
    )

    definition["name"] = (
        page_id
    )

    definition["displayName"] = (
        display_name
    )

    definition["displayOption"] = (
        "FitToPage"
    )

    definition["width"] = 1920
    definition["height"] = 1080

    write_json(
        page_folder
        / "page.json",
        definition,
    )

    visuals_dir = (
        page_folder
        / "visuals"
    )

    visuals_dir.mkdir(
        exist_ok=True
    )

    # Remove any copied native visuals.
    for child in visuals_dir.iterdir():

        if child.is_dir():

            shutil.rmtree(
                child
            )

        else:

            child.unlink()

    print(
        f"[PAGE] {display_name}"
    )


# ============================================================
# UPDATE PAGE ORDER
# ============================================================

pages_metadata["pageOrder"] = (
    page_ids
)

pages_metadata["activePageName"] = (
    page_ids[0]
)

write_json(
    PAGES_JSON,
    pages_metadata,
)


# ============================================================
# VALIDATE
# ============================================================

errors = []

for page_id, display_name in zip(
    page_ids,
    PAGE_NAMES,
):

    page_file = (
        PAGES_DIR
        / page_id
        / "page.json"
    )

    if not page_file.exists():

        errors.append(
            f"Missing page: {display_name}"
        )

        continue

    data = json.loads(
        page_file.read_text(
            encoding="utf-8"
        )
    )

    if data.get("name") != page_id:

        errors.append(
            f"Page ID mismatch: {display_name}"
        )

    if (
        data.get("displayName")
        != display_name
    ):

        errors.append(
            f"Display name mismatch: {display_name}"
        )

    if data.get("width") != 1920:

        errors.append(
            f"Wrong width: {display_name}"
        )

    if data.get("height") != 1080:

        errors.append(
            f"Wrong height: {display_name}"
        )


if (
    pages_metadata.get(
        "pageOrder"
    )
    != page_ids
):

    errors.append(
        "pages.json pageOrder mismatch"
    )


if errors:

    print()

    for error in errors:

        print(
            f"[ERROR] {error}"
        )

    raise SystemExit(1)


print()
print("=" * 72)
print("STAGE 8E VALIDATION")
print("=" * 72)

print(
    "[OK] Five report pages"
)

print(
    "[OK] Native PBIR 2.1 page schema preserved"
)

print(
    "[OK] 1920 x 1080 canvas preserved"
)

print(
    "[OK] Page order configured"
)

print(
    "[OK] Executive Overview set as active page"
)

print(
    "[OK] Blank visual directories ready"
)

print()
print("=" * 72)
print("STAGE 8E PAGE BUILD COMPLETE")
print("=" * 72)