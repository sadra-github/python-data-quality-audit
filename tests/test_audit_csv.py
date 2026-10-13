import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.audit_csv import audit_dataframe, run_audit


class TestAuditDataFrame(unittest.TestCase):
    def test_reports_missing_values_duplicates_and_constant_columns(self):
        df = pd.DataFrame({
            "sensor": [1.0, 1.0, 2.0],
            "temperature": [20.0, None, 22.0],
            "site": ["A", "A", "A"],
        })
        report = audit_dataframe(df)
        self.assertEqual(report["n_rows"], 3)
        self.assertEqual(report["n_columns"], 3)
        self.assertEqual(report["columns_with_missing_values"]["temperature"], 1)
        self.assertEqual(report["constant_columns"], ["site"])
        self.assertEqual(report["duplicate_rows"], 0)

    def test_run_audit_writes_both_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            csv_path = folder / "example.csv"
            outdir = folder / "reports"
            pd.DataFrame({"x": [1, 2], "y": [3, 3]}).to_csv(csv_path, index=False)
            report = run_audit(csv_path, outdir)
            self.assertEqual(report["n_rows"], 2)
            self.assertTrue((outdir / "audit_report.json").is_file())
            self.assertTrue((outdir / "audit_summary.txt").is_file())


if __name__ == "__main__":
    unittest.main()
