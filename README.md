# Python Data Quality Audit

A small, reproducible Python tool for auditing CSV files before analysis or machine-learning workflows.

## Features
- Reports row/column counts, duplicate rows, missing values, and duplicate column names.
- Identifies constant columns and columns with mixed data types.
- Saves machine-readable JSON and a concise text report.
- Includes a tiny example dataset and automated tests.

## Quick start

Python 3.10+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.audit_csv data/sample_messy.csv --outdir outputs
```

The sample intentionally contains a missing value, a duplicate row, and a constant column so the audit has something to report.

## Audit your own file

```bash
python -m src.audit_csv path/to/your_file.csv --outdir outputs
```

Outputs:
- `outputs/audit_report.json`
- `outputs/audit_summary.txt`

## Tests

```bash
python -m unittest discover -s tests -v
```

## Limitations
This is a lightweight structural audit, not a domain-specific validator. It does not decide whether a value is scientifically plausible or whether a target has leaked into model inputs. Review the report in the context of your data.

## License
MIT
