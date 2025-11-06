import os
import re
import numpy as np
import pandas as pd

# ===== Colors =====
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(SCRIPT_DIR, "Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv")

# ---------- Helpers ----------
def _banner(title: str, color=RED):
    print(color + "=" * 100)
    print("=" + " " * 98 + "=")
    print("=" + title.center(98) + "=")
    print("=" + " " * 98 + "=")
    print("=" * 100 + RESET)

def _sub(title: str):
    print(CYAN + "-" * 100 + RESET)
    print(title)
    print(CYAN + "-" * 100 + RESET)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Carica il CSV del Comune di Milano in modo robusto.
    """
    for enc, sep in [("utf-16", ";"), ("latin1", ";"), ("utf-8", ";"), ("utf-8", ",")]:
        try:
            df = pd.read_csv(file_path, encoding=enc, sep=sep)
            return df
        except Exception:
            continue
    raise RuntimeError("Impossibile leggere il CSV: controlla encoding o separatore.")

# ---------- DATA EXPLORATION ----------
def data_exploration(df: pd.DataFrame) -> None:
    _banner("DATA EXPLORATION")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns):,}")
    print(f"Column names ({len(df.columns)}): {list(df.columns)}\n")

    _sub("Sample rows (head)")
    print(df.head(10).to_string(index=False))
    print()

    _sub("Sample rows (tail)")
    print(df.tail(10).to_string(index=False))
    print()

    _sub("Random sample (n=10)")
    n = min(10, len(df))
    print(df.sample(n, random_state=42).to_string(index=False))
    print()

    _sub("Memory usage (MB)")
    mem = (df.memory_usage(index=True, deep=True).sum() / 1024**2)
    print(f"{mem:.2f} MB")
    print()

# ---------- DATA PROFILING ----------
def data_profiling_extended(df: pd.DataFrame) -> None:
    _banner("DATA PROFILING (Extended)")

    dtypes_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.values,
        "Distinct Count": df.nunique(dropna=True).values,
        "Non-Null Count": df.notna().sum().values,
        "Null Count": df.isna().sum().values,
        "Missing %": (df.isna().sum() / len(df) * 100).round(2).values
    })
    print(dtypes_df.to_string(index=False)); print()

    # Numeric statistics
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:

        #This part has been commented since must be some reasonings made on it all together
        """
        _sub("Numeric columns – describe()")
        print(df[num_cols].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).T.to_string())
        print()

        _sub("Correlation (Pearson) – absolute values")
        corr = df[num_cols].corr(numeric_only=True).abs()
        print(corr.to_string())
        print()

        _sub("Potential outliers (IQR method) – count per column")
        outlier_counts = {}
        for c in num_cols:
            s = df[c].dropna().astype(float)
            if s.empty:
                outlier_counts[c] = 0
                continue
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                outlier_counts[c] = 0
                continue
            lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
            outlier_counts[c] = int(((s < lower) | (s > upper)).sum())
        print(pd.Series(outlier_counts, name="outliers").to_string())
        print()
        """

    # String / categorical profiling
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if obj_cols:
        _sub("Categorical/string columns – cardinality & length stats")
        rows = []
        for c in obj_cols:
            s = df[c].astype(str)
            lens = s.str.len()
            rows.append({
                "Column": c,
                "Cardinality": df[c].nunique(dropna=True),
                "MinLen": int(lens.min() if len(lens) else 0),
                "MeanLen": round(lens.mean(),2) if len(lens) else 0,
                "MaxLen": int(lens.max() if len(lens) else 0)
            })
        print(pd.DataFrame(rows).to_string(index=False))
        print()

        _sub("Top-10 most frequent values per column")
        for c in obj_cols:
            print(f"\nColumn: {c}")
            vc = df[c].value_counts(dropna=True).head(10)
            tot = len(df[c])
            freq_df = pd.DataFrame({
                "Value": vc.index.astype(str),
                "Count": vc.values,
                "Pct(%)": (vc.values / tot * 100).round(2)
            })
            print(freq_df.to_string(index=False))

# ---------- DATA QUALITY ASSESSMENT ----------
def data_quality_assessment(df: pd.DataFrame) -> None:
    _banner("DATA QUALITY ASSESSMENT")

    _sub("Missing values summary")
    miss = pd.DataFrame({
        "Column": df.columns,
        "Missing": df.isna().sum().values,
        "Missing %": (df.isna().sum() / len(df) * 100).round(2).values
    }).sort_values("Missing %", ascending=False)
    print(miss.to_string(index=False)); print()

    print(f"Rows completely empty: {(df.isna().all(axis=1)).sum()}")
    print(f"Rows with any missing: {(df.isna().any(axis=1)).sum()}")
    print()

    _sub("Duplicate rows")
    dup_count = df.duplicated().sum()
    print(f"Duplicated rows: {dup_count}")
    if dup_count:
        print("Example duplicates (first 5):")
        print(df[df.duplicated()].head().to_string(index=False))
    print()

    _sub("Suspicious placeholder values that should maybe be NULL")
    placeholders = {"", "na", "n/a", "nd", "null", "none", "-", "--", "sconosciuto"}
    sus_counts = {}
    for c in df.columns:
        if df[c].dtype == "object":
            s = df[c].astype(str).str.strip().str.lower()
            sus_counts[c] = int(s.isin(placeholders).sum())
    print(pd.Series(sus_counts, name="placeholder_count").sort_values(ascending=False).to_string())
    print()

    _sub("Leading/trailing/multiple spaces (string columns)")
    anomalies = {}
    for c in df.select_dtypes(include=["object"]).columns:
        s = df[c].astype(str)
        #it's used to count leading spaces
        leading = s.str.match(r"^\s+").sum()
        #it's used to count trailing spaces
        trailing = s.str.match(r".*\s+$").sum()
        #it's used to count multiple spaces
        multi = s.str.contains(r"\s{2,}", regex=True).sum()
        anomalies[c] = {"leading": int(leading), "trailing": int(trailing), "multi": int(multi)}
    if anomalies:
        print(pd.DataFrame(anomalies).transpose().to_string())
    print()

    _sub("Validity checks (simple rules)")
    checks = []

    if "Codice via" in df.columns:
        checks.append(("Codice via positive", int((df["Codice via"] > 0).sum()), len(df)))
    if "Civico" in df.columns:
        civ = pd.to_numeric(df["Civico"], errors="coerce")
        checks.append(("Civico numeric (coercible)", int(civ.notna().sum()), len(df)))
    if "ZD" in df.columns:
        z = pd.to_numeric(df["ZD"], errors="coerce")
        in_range = z.between(1, 9, inclusive="both")
        checks.append(("ZD in [1..9]", int(in_range.fillna(False).sum()), len(df)))
    if "Tipo via" in df.columns:
        common = set(df["Tipo via"].value_counts(normalize=True).cumsum().index[:int(max(1, round(0.95*df["Tipo via"].nunique())))] )
        out_pct = (~df["Tipo via"].isin(common)).mean() * 100
        checks.append(("Tipo via unusual labels (%)", round(out_pct, 2), 100))

    if checks:
        for name, ok, tot in checks:
            if tot == 100:
                print(f"{name}: {ok}%")
            else:
                print(f"{name}: {ok}/{tot} ({ok/tot*100:.2f}%)")
    print()

def main():
    df = load_data(FILE_PATH)
    data_exploration(df)
    data_profiling_extended(df)
    data_quality_assessment(df)

if __name__ == "__main__":
    main()