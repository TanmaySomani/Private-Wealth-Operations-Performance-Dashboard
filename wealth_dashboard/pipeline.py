"""Validate CSV extracts, quarantine unsafe rows, and rebuild the reporting database."""
from __future__ import annotations
import csv
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
DB = ROOT / 'data' / 'curated' / 'wealth.db'
SNAPSHOT = '2026-09-30'


def read(name):
    with (RAW / f'{name}.csv').open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def valid_date(value):
    try:
        return date.fromisoformat(value).isoformat() == value
    except (ValueError, TypeError):
        return False


def build(db_path=DB, raw_path=RAW):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Build separately so a failed load never replaces a previous successful database.
    temp = db_path.with_suffix('.building')
    temp.unlink(missing_ok=True)
    con = sqlite3.connect(temp)
    con.execute('PRAGMA foreign_keys = ON')
    try:
        con.executescript((ROOT / 'sql' / 'schema.sql').read_text())
        def rows(name):
            with (Path(raw_path) / f'{name}.csv').open(newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        def issue(source, rid, rule, disposition, detail):
            con.execute('INSERT INTO issues(source, record_id, rule, disposition, detail) VALUES (?,?,?,?,?)', (source, rid or '(missing)', rule, disposition, detail))
        # Dimensions are essential for all facts. Invalid or duplicate dimension rows are quarantined.
        ids = {}
        for name, columns, key in [
            ('teams', ['team_id', 'team_name'], 'team_id'),
            ('advisers', ['adviser_id', 'adviser_name', 'team_id'], 'adviser_id'),
            ('clients', ['client_id', 'client_name', 'adviser_id', 'segment', 'status'], 'client_id')]:
            ids[name] = set()
            for r in rows(name):
                rid = r.get(key, '')
                required = [c for c in columns if not (name == 'clients' and c == 'adviser_id')]
                if not rid or rid in ids[name] or any(not r.get(c) for c in required):
                    issue(name, rid, 'Required or unique identifier', 'Quarantined', 'Missing required field or duplicate identifier')
                    continue
                if name == 'advisers' and r['team_id'] not in ids['teams'] or name == 'clients' and r['adviser_id'] and r['adviser_id'] not in ids['advisers']:
                    issue(name, rid, 'Valid relationship', 'Quarantined', 'Unknown parent identifier')
                    continue
                vals = [r[c] or None for c in columns]
                con.execute(f"INSERT INTO {name} VALUES ({','.join('?' for _ in columns)})", vals)
                ids[name].add(rid)
                if name == 'clients' and not r['adviser_id']:
                    issue(name, rid, 'Assigned adviser', 'Retained with exception', 'Client is visible to firm-wide reporting only until assigned')
        for name, columns, key in [
            ('tasks', ['task_id', 'client_id', 'task_type', 'created_date', 'due_date', 'status', 'completed_date', 'stage'], 'task_id'),
            ('fees', ['fee_id', 'client_id', 'fee_date', 'amount_cents'], 'fee_id'),
            ('ledger', ['ledger_id', 'fee_id', 'posting_date', 'amount_cents'], 'ledger_id')]:
            seen = set()
            for r in rows(name):
                rid = r.get(key, '')
                reason = None
                if not rid or rid in seen:
                    reason = 'Missing or duplicate identifier'
                elif name in ('tasks', 'fees') and r.get('client_id') not in ids['clients']:
                    reason = 'Unknown client'
                elif name == 'tasks':
                    if r.get('task_type') not in ('Annual review', 'Onboarding', 'Service request') or r.get('status') not in ('Open', 'Completed', 'Cancelled'):
                        reason = 'Invalid task type or status'
                    elif not valid_date(r.get('created_date')) or not valid_date(r.get('due_date')) or r['created_date'] > r['due_date']:
                        reason = 'Invalid task dates'
                    elif r['status'] == 'Completed' and (not valid_date(r.get('completed_date')) or r['completed_date'] < r['created_date'] or r['completed_date'] > SNAPSHOT):
                        reason = 'Completed task has missing or impossible completion date'
                    elif r['status'] != 'Completed' and r.get('completed_date'):
                        reason = 'Non-completed task has completion date'
                else:
                    d = r.get('fee_date') if name == 'fees' else r.get('posting_date')
                    try:
                        amount_valid = int(r.get('amount_cents', '')) >= 0
                    except ValueError:
                        amount_valid = False
                    if not valid_date(d) or d > SNAPSHOT or not amount_valid or (name == 'ledger' and not r.get('fee_id')):
                        reason = 'Invalid date, amount or fee reference'
                if reason:
                    issue(name, rid, reason, 'Quarantined', str(r))
                    continue
                seen.add(rid)
                vals = [int(r[c]) if c == 'amount_cents' else (r[c] or None) for c in columns]
                con.execute(f"INSERT INTO {name} VALUES ({','.join('?' for _ in columns)})", vals)
        con.execute('INSERT INTO load_log(snapshot_date,completed_at_utc,status) VALUES (?,?,?)', (SNAPSHOT, datetime.now(timezone.utc).isoformat(timespec='seconds'), 'Succeeded'))
        con.executescript((ROOT / 'sql' / 'views.sql').read_text())
        con.commit()
        con.close()
        temp.replace(db_path)
    except Exception:
        con.close()
        temp.unlink(missing_ok=True)
        raise
    return db_path

if __name__ == '__main__':
    print(f'Built {build()}')
