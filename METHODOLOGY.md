# Methodology

The analysis is implemented in `DIQ_Project25_26_v5.ipynb`. References below use the numeric suffix of cell IDs, for example `v5-cell-159`; these correspond to zero-based cell indices in the archived v5 notebook.

## 1. Profiling and quality assessment — cells 10–44

The input CSV contains 2,070 rows and 12 attributes, with UTF-16 encoding and a semicolon separator. Profiling covers schema, data types, cardinality, categorical frequencies, missingness, exact duplicate rows, numeric ranges and Pearson correlations.

The quality measures are:

- **Completeness:** non-null cells divided by all cells.
- **Syntactic accuracy:** domain and structural checks for ZD and street codes.
- **Consistency:** indicators comparing surface and structured address fields with the location text.
- **Uniqueness:** distinct non-null values divided by all rows, using the notebook's definition.
- **Distinctness:** distinct non-null values divided by non-null rows.
- **Constancy:** the largest observed frequency divided by non-null rows.

Ground-truth semantic accuracy and record-level timeliness are outside the measured dimensions because the input lacks an independent reference and individual update timestamps.

## 2. Text normalization and activity features — cells 48–65

Explicit replacements correct recurring encoding artefacts and malformed accented words. These rules target the supplied dataset.

`Settore storico pe` is split on semicolons and commas, stripped of extra whitespace and expanded with `TransactionEncoder`. Labels with **Jaro–Winkler similarity > 0.8 and matching custom Soundex codes** are combined using Boolean OR, retaining the more frequent label. Manual mappings handle additional aliases, and labels below 1% prevalence are removed.

The saved v5 sequence has 52 initial activity features, 47 after automatic consolidation, 39 after manual mappings and 20 after frequency filtering. The resulting Boolean features replace the original compound activity column.

## 3. Address and commercial-form processing — cells 68–107

One malformed record is reconstructed from a pair of source rows, after which the auxiliary row is removed. Regex extraction recovers missing civic numbers. Structured street type, street name and civic values are checked against `Ubicazione`; conflicting rows are filtered. `codvia` location strings are set to missing before these checks.

Street abbreviations are expanded and numeric codes normalized. `Accesso`, `Isolato` and `Presso` are extracted from the location text. Mentions of `ingresso` are counted during exploration. ZD is renamed `Municipio`, and the original location string is removed once its structured attributes have been extracted.

For ZD reconciliation, the notebook reads five cached Nominatim responses. It extracts `Municipio N` when available and otherwise uses the existing ZD. A matching existing ZD is kept; a matching value extracted from `Ubicazione` replaces it; otherwise the record is removed. For Via Goldoni, the cached result lacks a municipality token and the existing-ZD fallback applies. The query uses street name and type without a civic number.

Commercial forms are split into primary and secondary activities. For a mixed activity with missing primary form, the rule assigns `somministrazione` as primary. These domain assumptions are retained in the transformed dataset.

## 4. Association rules — cells 112–123

| Procedure | Input | Minimum support | Minimum confidence | Application |
| --- | --- | ---: | ---: | --- |
| FP-Growth with mlxtend | Sector matrix | 0.05 | 0.90 | Explore associations and apply two explicit `Bar caffè` updates |
| efficient-apriori | Primary form, secondary form and sales form | 0.01 | 0.50 | Fill missing business categories |

Apriori uses a temporary mode-filled copy of the three fields. Rules containing `Assente` are excluded; the rest are ordered by confidence and support. A rule is applied when its antecedents match and the target is still missing. The saved v5 output records two primary-form and 21 sales-form imputations.

FP-Growth operates on the sector matrix built before subsequent address-based row filtering. Its mining population therefore follows that earlier processing stage.

## 5. Imputation and outlier treatment — cells 129–156

Explicit defaults represent unresolved fields: `S.N.C.` for civic number, `Non specificata` for name, `Non specificato` for host context, `0` for block identifier and `Assente` for secondary business form.

Random Forest estimates remaining surface, primary-form, sales-form and access values. Temporary copies receive median/mode initialization. Selected identifiers and original target fields are excluded from predictors; categorical predictors are one-hot encoded and categorical targets label-encoded.

The execution configuration is **200 trees, seed 42, two CPU jobs**, with predictors following DataFrame column order. Initial numeric estimates are cast to the target type. `Codice via` and `Isolato` are treated as categorical identifiers.

Surface outliers are values outside `[Q1 − 1.5 × IQR, Q3 + 1.5 × IQR]`. Flagged surface values are set to missing and re-estimated by Random Forest, rounding predictions upward. Rows remain in the dataset. This step produces a processed surface measure rather than preserving every observed extreme value.

## 6. Duplicate detection — cells 159–162

After exact duplicates are removed, the notebook normalizes names and street strings and extracts civic digits and parity. Candidate pairs combine sorted neighbourhood on normalized street (`window=9`) and blocking on name initial plus municipality. Pairs with both names missing must come from the address-based candidate set.

For pairs with both names present, the address pre-filter requires equal street strings or, for strings longer than three characters, `SequenceMatcher` similarity of at least 0.90. Available civic numbers must have equal parity and differ by at most two.

Recordlinkage computes exact matches for normalized street, civic and municipality, and thresholded Jaro–Winkler comparisons for name and street. The latter use threshold 0.85 and produce **binary match features**.

| Case | Weighted score | Acceptance threshold |
| --- | --- | ---: |
| At least one name missing | 0.70 × exact street + 0.20 × exact civic + 0.10 × exact municipality | 0.95 |
| Both names present | 0.35 × binary name match + 0.35 × binary street match + 0.15 × exact civic + 0.15 × exact municipality | 0.85 |

The missing-name score is zero when street or civic differs. Both-named pairs also use conditional street/name rejection rules; exact civic equality is not an unconditional requirement in that branch. `NAME_VERY_SIMILAR` is applied to the binary name feature. Scores express the implemented matching rules rather than calibrated probabilities of entity identity.

## 7. Data fusion — cells 164–170

An undirected graph represents records as nodes and accepted duplicate pairs as edges. Connected components define merge groups, including singletons. Aggregation uses:

- Longest informative establishment name.
- Median surface, rounded upward.
- Modal street and civic number.
- First non-null municipality and remaining attributes, including sector flags.

A consensus indicator summarizes within-group agreement on street, civic and municipality. It is reported as a diagnostic. Intermediate group IDs, source-index lists, merge counts and consensus scores are removed from the final exported schema.

## 8. Context and anomaly flags — cells 173–174

Patterns in `Insegna` and `Presso` assign context in order: hospital, school, public office, company, horeca and other, with an unknown fallback for empty text. Explicit hospital and school sector combinations set `IsAnomaly=True`.

These are rule-based diagnostic flags. All records remain in the cleaned CSV, allowing analysis of the complete data or of the subset not flagged by the rules.

## 9. Exploratory analysis — cells 177–196

Categorical associations are examined with Cramér's V. The predictive targets are `Forma vendita` for classification and `Superficie somministrazione` for regression.

KNN uses five neighbours, distance weights, an 80/20 train/test split with seed 42 and stratification for classification. Numeric missing predictors receive means, categorical missing predictors a placeholder, and categorical variables are one-hot encoded. StandardScaler is fitted on the outer training subset. Regression reports mean RMSE across eight ShuffleSplit folds of that subset, with a 30% validation fraction.

XGBoost uses the cleaned, non-flagged subset. Classification uses 300 trees, maximum depth 6 and learning rate 0.1; regression uses 400 trees, depth 6 and learning rate 0.05. Both use row and column subsampling of 0.8, histogram trees and seed 42. Regression is evaluated on the held-out 20% test set.

### Evaluation scope

These experiments characterize the processed data. Cleaning and target imputation precede predictive splitting; predictor imputation and category discovery precede the outer split, and KNN scaling precedes its inner cross-validation. Raw and cleaned experiments also use different populations and target distributions. Scores are consequently interpreted as exploratory results for those datasets, not as estimates from a shared, untouched test population. KNN cross-validation RMSE and XGBoost test RMSE retain their separate evaluation definitions.
