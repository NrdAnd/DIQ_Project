"""Validate immutable artefacts, the portable notebook and documented data contracts."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import warnings

from IPython.core.inputtransformer2 import TransformerManager
import nbformat
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEANED = "Cleaned_Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_links(text, base):
    # Check inline Markdown links without optional titles.
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip("<>")
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        path = base / unquote(parts.path)
        require(path.exists(), f"Broken local link: {target}")


def check_cleaned(frame, expected_columns):
    require(list(frame.columns) == expected_columns, "Unexpected cleaned column names/order")
    require(frame.shape == (1636, 35), f"Unexpected cleaned shape: {frame.shape}")
    require(not frame.isna().any().any(), "Cleaned CSV has missing values")
    require(not frame.duplicated().any(), "Cleaned CSV has exact duplicate rows")
    require(frame["Municipio"].isin(range(1, 10)).all(), "Municipio outside 1–9")
    require((frame["Superficie somministrazione"] > 0).all(), "Non-positive surface")
    for col in expected_columns[13:33] + ["IsAnomaly"]:
        require(pd.api.types.is_bool_dtype(frame[col]), f"Non-Boolean field: {col}")
    require(int(frame["IsAnomaly"].sum()) == 19, "Unexpected anomaly count")
    require(set(frame["Forma vendita"]) == {"al banco", "al tavolo", "misto", "self service"},
            "Unexpected sales-form domain")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated", action="store_true", help="Also validate a completed local rerun")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "provenance/artifacts.json").read_text())
    expected_columns = None
    for item in manifest["artifacts"]:
        path = ROOT / item["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == item["sha256"], f"Historical artefact changed: {item['path']}")
        if path.suffix == ".csv":
            frame = pd.read_csv(path, encoding=item["encoding"], sep=item["delimiter"])
            require(list(frame.columns) == item["columns"], f"Schema changed: {path.name}")
            require(len(frame) == item["rows"], f"Row count changed: {path.name}")
            require(int(frame.isna().sum().sum()) == item["pandas_missing_cells"], f"Missingness changed: {path.name}")
            require(int(frame.duplicated().sum()) == item["duplicate_rows"], f"Duplicate count changed: {path.name}")
            if path.name == CLEANED:
                expected_columns = item["columns"]
                check_cleaned(frame, expected_columns)

    transform = TransformerManager()
    paths = [ROOT / "DIQ_Project25_26_v5.ipynb", *sorted((ROOT / "archive").glob("*.ipynb"))]
    for path in paths:
        with warnings.catch_warnings():
            # Old notebooks predate mandatory cell IDs; preserve their original bytes.
            warnings.simplefilter("ignore", nbformat.warnings.MissingIDFieldWarning)
            notebook = nbformat.read(path, as_version=4)
            nbformat.validate(notebook)
        require(not any(o.get("output_type") == "error" for c in notebook.cells
                        for o in c.get("outputs", [])), f"Saved error output in {path.name}")
        if path.parent == ROOT:
            ids = [c.id for c in notebook.cells]
            require(len(ids) == len(set(ids)), "Duplicate notebook cell IDs")
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    require(not cell.outputs and cell.execution_count is None, "Portable source has stale outputs")
                    require(not re.search(r"(?m)^\s*!", cell.source), "Shell installation in portable notebook")
                    require("/content/drive/" not in cell.source, "Colab-specific path in portable notebook")
                    ast.parse(transform.transform_cell(cell.source))
                elif cell.cell_type == "markdown":
                    check_links(cell.source, ROOT)
    for path in ROOT.glob("*.md"):
        check_links(path.read_text(), ROOT)

    cache = json.loads((ROOT / "provenance/geocoding.json").read_text())
    original = json.loads((ROOT / cache["source"]).read_text())
    cell = original["cells"][cache["original_cell_index"]]
    saved = "".join("".join(o.get("text", [])) for o in cell["outputs"])
    extracted = dict(re.findall(r"Location found by Nominatim for '([^']+)' string: ([^\n]+)", saved))
    require(cache["responses"] == extracted and len(extracted) == 5, "Geocoder cache differs from evidence")

    if args.generated:
        require(expected_columns is not None, "Missing historical schema")
        frame = pd.read_csv(ROOT / "generated" / CLEANED)
        check_cleaned(frame, expected_columns)
        executed = nbformat.read(ROOT / "generated/DIQ_Project25_26_v5.executed.ipynb", as_version=4)
        source = nbformat.read(ROOT / "DIQ_Project25_26_v5.ipynb", as_version=4)
        require([(c.id, c.source) for c in executed.cells] == [(c.id, c.source) for c in source.cells],
                "Executed notebook does not match current source")
        code = [c for c in executed.cells if c.cell_type == "code"]
        require(all(c.execution_count is not None for c in code), "Incomplete notebook execution")
        require(not any(o.get("output_type") == "error" for c in code for o in c.outputs), "Execution contains errors")
        print(f"Regenerated data and all {len(code)} executed code cells validated.")
    print("Historical checksums, data contracts, notebooks, cache evidence and local links validated.")


if __name__ == "__main__":
    main()
