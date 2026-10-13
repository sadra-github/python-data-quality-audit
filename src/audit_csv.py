"""Lightweight structural quality audit for CSV files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def audit_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Return a JSON-serializable structural audit for a DataFrame."""
    missing = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())
    duplicate_columns = [str(c) for c in df.columns[df.columns.duplicated()].tolist()]
    constant_columns = [
        str(c) for c in df.columns
        if df[c].nunique(dropna=False) <= 1
    ]
    mixed_type_columns = []
    for col in df.columns:
        observed_types = {type(v).__name__ for v in df[col].dropna().tolist()}
        if len(observed_types) > 1:
            mixed_type_columns.append(str(col))

    return {
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "duplicate_rows": duplicate_rows,
        "duplicate_columns": duplicate_columns,
        "missing_by_column": {str(k): int(v) for k, v in missing.items()},
        "columns_with_missing_values": {
            str(k): int(v) for k, v in missing.items() if int(v) > 0
        },
        "constant_columns": constant_columns,
        "mixed_type_columns": mixed_type_columns,
        "column_dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
    }


def format_summary(report: dict[str, Any], source: str) -> str:
    missing_cols = report["columns_with_missing_values"]
    lines = [
        "CSV DATA QUALITY AUDIT",
        "=" * 24,
        f"Source: {source}",
        f"Rows: {report['n_rows']}",
        f"Columns: {report['n_columns']}",
        f"Duplicate rows: {report['duplicate_rows']}",
        f"Duplicate column names: {len(report['duplicate_columns'])}",
        f"Columns containing missing values: {len(missing_cols)}",
        f"Constant columns: {len(report['constant_columns'])}",
        f"Mixed-type columns: {len(report['mixed_type_columns'])}",
        "",
        "Missing values by column:",
    ]
    if missing_cols:
        lines.extend(f"  - {name}: {count}" for name, count in missing_cols.items())
    else:
        lines.append("  None")
    lines.extend(["", "Constant columns:"])
    lines.extend(f"  - {name}" for name in report["constant_columns"]) if report["constant_columns"] else lines.append("  None")
    lines.extend(["", "Interpretation:"])
    if report["duplicate_rows"] or missing_cols or report["duplicate_columns"]:
        lines.append("  Review the flagged structural issues before downstream analysis.")
    else:
        lines.append("  No missing values, duplicate rows, or duplicate column names were detected.")
    lines.append("  Constant columns may be valid, but often add little value to predictive models.")
    return "\n".join(lines) + "\n"


def run_audit(csv_path: str | Path, outdir: str | Path) -> dict[str, Any]:
    source = Path(csv_path)
    output_dir = Path(outdir)
    if not source.is_file():
        raise FileNotFoundError(f"CSV file not found: {source}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Keep duplicate column names visible when reading a CSV.
    df = pd.read_csv(source)
    report = audit_dataframe(df)
    report["source_file"] = str(source)
    (output_dir / "audit_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "audit_summary.txt").write_text(
        format_summary(report, str(source)),
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the structure and basic quality of a CSV file.")
    parser.add_argument("csv_path", help="Path to the CSV file to audit")
    parser.add_argument("--outdir", default="outputs", help="Directory for report files (default: outputs)")
    args = parser.parse_args()
    try:
        report = run_audit(args.csv_path, args.outdir)
    except (FileNotFoundError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        parser.error(str(exc))
    print(format_summary(report, args.csv_path))


if __name__ == "__main__":
    main()
