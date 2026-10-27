import csv
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from wealth_dashboard.generate import generate, RAW
from wealth_dashboard.pipeline import build

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / 'test.db'
        build(cls.db)
        cls.con = sqlite3.connect(cls.db)
    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        cls.tmp.cleanup()
    def scalar(self, query):
        return self.con.execute(query).fetchone()[0]
    def test_dimensions_and_quarantine(self):
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM clients'), 500)
        self.assertEqual(self.scalar('SELECT COUNT(*) FROM fees'), 9000)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM issues WHERE disposition='Quarantined'"), 2)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM issues WHERE rule='Assigned adviser'"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM task_reporting WHERE status='Completed' AND completed_date IS NULL"), 0)
    def test_reconciliation_conserves_both_ledgers(self):
        self.assertEqual(self.scalar('SELECT SUM(operational_cents) FROM fee_reconciliation'), self.scalar('SELECT SUM(amount_cents) FROM fees'))
        self.assertEqual(self.scalar('SELECT SUM(ledger_cents) FROM fee_reconciliation'), self.scalar('SELECT SUM(amount_cents) FROM ledger'))
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM fee_reconciliation WHERE match_status='Amount mismatch'"), 1)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM fee_reconciliation WHERE match_status='Missing in operations'"), 1)
        self.assertEqual(self.scalar('SELECT SUM(difference_cents) FROM fee_reconciliation'), 42500)
    def test_snapshot_and_on_time_rules(self):
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM task_reporting WHERE overdue_at_snapshot=1 AND (status <> 'Open' OR due_date >= '2026-09-30')"), 0)
        self.assertEqual(self.scalar("SELECT COUNT(*) FROM task_reporting WHERE completed_on_time=1 AND (status <> 'Completed' OR completed_date > due_date)"), 0)
    def test_failed_build_preserves_previous_database(self):
        with tempfile.TemporaryDirectory() as folder:
            raw_copy = Path(folder) / 'raw'
            shutil.copytree(RAW, raw_copy)
            (raw_copy / 'tasks.csv').unlink()
            before = self.db.read_bytes()
            with self.assertRaises(FileNotFoundError): build(self.db, raw_copy)
            self.assertEqual(before, self.db.read_bytes())

if __name__ == '__main__':
    unittest.main()
