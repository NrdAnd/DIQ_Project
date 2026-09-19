# Results

## Data quality

The following measurements refer to the two CSV files included at the repository root.

| Measurement | Original dataset | Cleaned dataset |
| --- | ---: | ---: |
| Records | 2,070 | 1,636 |
| Attributes | 12 | 35 |
| Missing cells | 5,278 | 0 |
| Completeness | 78.7520% | 100% |
| Exact duplicate rows beyond the first occurrence | 22 | 0 |
| Minimum service-area value | 2 | 4 |
| Maximum service-area value | 4,815 | 418 |

Completeness is computed using pandas' default missing-value interpretation. The cleaned data includes explicit defaults and model-based imputations, as described in [METHODOLOGY.md](METHODOLOGY.md).

The final schema consists of 13 descriptive attributes, 20 Boolean sector indicators, `context_type` and `IsAnomaly`. The anomaly rules flag **19 records**, leaving **1,617 non-flagged records**. Flagged records remain available in the cleaned CSV.

| Context | Records |
| --- | ---: |
| Other | 1,330 |
| HoReCa | 121 |
| Company | 78 |
| School | 66 |
| Hospital | 28 |
| Public office | 13 |

## Exploratory predictive experiments

The table below reports the saved outputs of [the v5 notebook](archive/DIQ_Project25_26_v5.original.ipynb), cells 181, 186, 191 and 196 (zero-based indices).

Classification predicts `Forma vendita`; regression predicts `Superficie somministrazione`.

| Model / dataset | Classification accuracy | Macro F1 | Regression RMSE |
| --- | ---: | ---: | ---: |
| KNN / original | 0.57 | 0.33 | 300.2847 |
| KNN / cleaned | 0.69 | 0.42 | 87.7651 |
| KNN / cleaned, non-flagged | 0.70 | 0.42 | 80.9392 |
| XGBoost / cleaned, non-flagged | 0.854938 | 0.564377 | 76.2377 |

KNN classification scores use the saved report's two-decimal precision. Its regression RMSE is the mean over eight ShuffleSplit folds of the outer training subset. XGBoost regression RMSE is measured on the held-out test set. The two regression columns therefore describe their respective evaluation procedures, rather than a shared-test-set model ranking.

The experiments characterize the processed datasets. Cleaning and imputation precede the predictive splits, and some targets are imputed. Model evaluation is interpreted within that exploratory setting. The `al tavolo` class has zero recall in the saved experiments, reflecting the remaining class imbalance.

To generate a new set of outputs with the current notebook and dependency environment, follow [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Each execution writes its results to `generated/`.
