# Environment and execution

## Requirements

Use **Python 3.11**. The reference environment uses CPython 3.11.9 on macOS arm64 with CPU execution. The continuous integration workflow uses Ubuntu and Python 3.11.

```bash
git clone https://github.com/NrdAnd/DIQ_Project.git
cd DIQ_Project
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

On Windows, activate with `.venv\Scripts\Activate.ps1`.

`requirements.txt` pins direct dependencies. `requirements-lock.txt` records the resolved reference environment, including a platform marker for the macOS-only `appnope` package. Install it with `python -m pip install -r requirements-lock.txt` when reproducing that dependency set. Platform-specific dependencies may vary.

The workflow uses scikit-learn Random Forest and CPU XGBoost. If XGBoost reports a missing `libomp.dylib` on macOS, install OpenMP with `brew install libomp`. Windows may require the Visual C++ Redistributable; see the [XGBoost installation guide](https://xgboost.readthedocs.io/en/stable/install.html).

The optional schema illustration uses Graphviz. The Python package is installed by pip; the `dot` executable is a separate system dependency. Install it with `brew install graphviz` on macOS or your operating system's package manager. Without `dot`, the notebook skips the illustration.

## Run the analysis

From the repository root:

```bash
python scripts/validate_repository.py
python scripts/execute_notebook.py
python scripts/validate_repository.py --generated
```

The runner executes all notebook cells in a fresh kernel using the active environment's Python interpreter. It uses a temporary kernel definition, sets `PYTHONHASHSEED=0` and limits selected native thread pools to two threads. Random Forest and XGBoost also use two jobs.

For interactive use, run `python -m jupyterlab`, select a kernel from the installed environment and execute `DIQ_Project25_26_v5.ipynb` from top to bottom. The notebook's working directory must be the repository root.

## Inputs and outputs

The input is the original CSV in the repository root. Its SHA-256 is checked because the analysis contains repairs specific to that dataset. Geographic responses are read from `provenance/geocoding.json`; execution does not require a live geocoding service.

Outputs are written to:

```text
generated/DIQ_Project25_26_v5.executed.ipynb
generated/Cleaned_Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv
```

`generated/` also contains runtime caches and is ignored by Git. Each run replaces the generated files; copy them to a separate run directory when retaining multiple experiments. The dataset stored at the repository root is not overwritten.

If a cell fails, the runner saves the partial notebook for diagnosis and exits with an error. A new dataset is written only when the final export cell completes; consult the exit status before using generated files after a failed run.

## Repository checks

The validator checks file hashes, CSV schemas and counts, missingness, exact duplicates, selected value domains, notebook structure, Python syntax, cached geographic responses and local documentation links. With `--generated`, it also checks that the executed notebook matches the current source, that every code cell completed and that the generated data satisfies the output contract.

GitHub Actions runs dependency installation, `pip check`, repository validation, full notebook execution and output validation. Checks do not impose exact floating-point model scores across operating systems.

Dependency versions, hardware and execution settings can affect numerical results. Preserve the environment and source revision when retaining an experiment. The notebooks in `archive/` retain the execution setup of their respective versions; use the root notebook with the installation instructions above.
