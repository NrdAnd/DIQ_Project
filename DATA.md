# Data dictionary and sources

## Dataset files

| File | Role | Encoding / separator | Shape |
| --- | --- | --- | --- |
| `Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv` | Original input supplied with the project | UTF-16 / `;` | 2,070 × 12 |
| `Cleaned_Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv` | Cleaned dataset | UTF-8 / `,` | 1,636 × 35 |

File checksums, schemas and sizes are recorded in [provenance/artifacts.json](provenance/artifacts.json). The notebook exports new results under `generated/`.

CSV has no persisted pandas type metadata. Load identifiers as strings when their textual representation matters, especially civic numbers such as `000` or `S.N.C.`:

```python
import pandas as pd

raw = pd.read_csv(
    "Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv",
    sep=";", encoding="utf-16",
)
cleaned = pd.read_csv(
    "Cleaned_Comune-di-Milano-Pubblici-esercizi-fuori-piano.csv",
    encoding="utf-8",
    dtype={"Civico": "string", "Codice via": "string", "Isolato": "string"},
)
```

## Source and time coverage

**Source:** Comune di Milano, *Pubblici esercizi fuori piano*. The [municipal catalogue entry DS59](https://dati.comune.milano.it/dataset/ds59-economia-pubblici-esercizi-fuori-piano) describes establishments where food and beverage service takes place within another primary activity. Administrative attributes can reflect different last-update times.

The analysis uses a fixed historical snapshot. The notebook refers to 2012; the CSV has no record-level dates or accompanying acquisition timestamp. Use the included file for execution because the processing rules are specific to this snapshot.

## Source fields

Counts below use pandas' default missing-value interpretation on the supplied raw CSV.

| Field | Meaning / handling | Missing rows |
| --- | --- | ---: |
| `Settore storico pe` | Multi-valued historical activity labels; split and normalized into sectors | 193 |
| `Insegna` | Establishment name/sign | 1,477 |
| `Ubicazione` | Free-text address and contextual details | 2 |
| `Tipo via` | Street type abbreviation | 2 |
| `Via` | Street name | 1 |
| `Civico` | Civic identifier; not a numeric measure | 154 |
| `Codice via` | Street identifier; not a numeric measure | 2 |
| `ZD` | Historical zone identifier | 2 |
| `Forma commercio` | Commercial activity form | 1,021 |
| `Forma commercio prev` | Prevailing commercial form; includes malformed values | 1,025 |
| `Forma vendita` | Sales/service mode | 1,030 |
| `Superficie somministrazione` | Reported service area, treated as a numeric surface measure | 369 |

The project treats surface as area; the original snapshot has no machine-readable unit metadata. The repository does not independently certify units or individual values.

## Cleaned fields

The exported schema has **13 descriptive fields, 20 Boolean sectors and 2 diagnostic fields**. It contains no explicit primary key. Field order is recorded in the manifest.

| Field | Semantic type | Transformation / interpretation |
| --- | --- | --- |
| `Insegna` | Text | Informative name selected during fusion; default `Non specificata` |
| `Tipo via` | Category | Expanded street type |
| `Via` | Text | Street name, with modal selection during fusion |
| `Civico` | Identifier | Extracted/reconciled civic value; default `S.N.C.` |
| `Codice via` | Identifier | Street code; categorical during analysis |
| `Municipio` | Category, 1–9 | Renamed ZD, after the historical reconciliation rule |
| `Accesso` | Category | Extracted access description; remaining gaps predicted |
| `Isolato` | Identifier | Extracted block code; `0` is an unknown/default sentinel |
| `Presso` | Text | Host context extracted from `c/o`; default `Non specificato` |
| `Forma commercio prevalente` | Category | Primary activity; normalized and imputed |
| `Forma commercio secondaria` | Category | Secondary activity; `Assente` includes defaulted missing values |
| `Forma vendita` | Category | Service mode; some values are imputed |
| `Superficie somministrazione` | Numeric measure | Missing/outlier imputation and fusion; supplied export ranges 4–418 |
| `context_type` | Category | Regex-derived context, not an authoritative establishment class |
| `IsAnomaly` | Boolean | Match against heuristic forbidden sector/context combinations |

All 20 sector fields are Boolean (`True` / `False` in CSV), in this order:

```text
Bar caffè
Bar gastronomici e simili
Biliardo
Bocce
Carte
Cibi cotti preconfezionati
Discoteche
Genere merceol.autorizz.sanit.
Giochi legge 388/2000
Mensa
Pizzeria
Prodotti di gastronomia
Ristorante
Spaccio bevande analcoliche
Tavola calda
Tavola fredda
Fast food
Osteria
Self service
Trattoria
```

A false sector flag is the result of the transformation, not proof of confirmed absence. Rare sectors were removed. The original `Settore storico pe`, `Ubicazione`, intermediate imputation columns and fusion provenance fields are not exported.

The supplied cleaned data contains 1,330 `other`, 121 `horeca`, 78 `company`, 66 `school`, 28 `hospital` and 13 `public_office` records. There are 19 flags and 1,617 non-flagged records. Zero missing cells includes placeholders and model estimates; see [METHODOLOGY.md](METHODOLOGY.md).

## Licensing and attribution

The authors' original code and documentation are covered by the [MIT License](LICENSE). Copyright and permission notices must be retained in copies or substantial portions. Authors: Andrea Nardi, Christian Giovanni Pesaturo and Andrea Pinessi.

Municipal source attribution: **Comune di Milano — Unità Analytics e Open Data, “Attività commerciali: pubblici esercizi fuori piano”.** The cleaned dataset is a project derivative.

The [national catalogue](https://www.dati.gov.it/node/view-dataset/dataset?id=de623b2a-647f-4c07-8440-491550118463) lists CC BY 4.0 terms for its distributions. The source licence notice for the specific historical CSV is not included in the repository; its applicable terms require confirmation before redistribution. The repository's MIT licence does not apply to municipal data.

Geographic responses in `provenance/geocoding.json` are sourced from the saved Nominatim results in v5 cell 93. Attribution: **© OpenStreetMap contributors**, under the [Open Database License](https://www.openstreetmap.org/copyright). The lookup date is not recorded. The notebook reads this cache locally; future live requests should follow the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/).

University marks and third-party illustrations in the report remain subject to their respective rights.

## Previous dataset version

[The November 2025 cleaned dataset](archive/Cleaned_Comune-di-Milano-Pubblici-esercizi-fuori-piano.2025-11-29.csv) is retained in `archive/` alongside previous notebooks. It contains 1,635 records and 35 fields. Its checksum and source revision are listed in `provenance/artifacts.json`. The notebook's input and output paths are described in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
