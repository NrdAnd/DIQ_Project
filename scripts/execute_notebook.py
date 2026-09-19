"""Execute the portable v5 in a fresh kernel, without touching historical outputs."""

import json
import os
from pathlib import Path
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "generated"
    output.mkdir(exist_ok=True)
    for key, value in {
        "MPLCONFIGDIR": str(output / ".matplotlib"),
        "IPYTHONDIR": str(output / ".ipython"),
        "JUPYTER_RUNTIME_DIR": str(output / ".jupyter-runtime"),
        "PYTHONHASHSEED": "0",
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
    }.items():
        os.environ[key] = value
    notebook = nbformat.read(root / "DIQ_Project25_26_v5.ipynb", as_version=4)
    nbformat.validate(notebook)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="diq-kernel-", dir=output) as tmp:
        kernels = Path(tmp) / "kernels" / "diq"
        kernels.mkdir(parents=True)
        (kernels / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "DIQ verification", "language": "python",
        }))
        previous = os.environ.get("JUPYTER_PATH")
        os.environ["JUPYTER_PATH"] = tmp + (os.pathsep + previous if previous else "")
        try:
            client = NotebookClient(notebook, timeout=1200, kernel_name="diq",
                                    resources={"metadata": {"path": str(root)}})
            client.execute()
        finally:
            nbformat.write(notebook, output / "DIQ_Project25_26_v5.executed.ipynb")
            if previous is None:
                os.environ.pop("JUPYTER_PATH", None)
            else:
                os.environ["JUPYTER_PATH"] = previous
    executed = sum(c.cell_type == "code" and c.execution_count is not None for c in notebook.cells)
    print(f"Executed {executed} code cells in {time.monotonic() - started:.1f} seconds.")
    print("Results: generated/DIQ_Project25_26_v5.executed.ipynb")


if __name__ == "__main__":
    main()
