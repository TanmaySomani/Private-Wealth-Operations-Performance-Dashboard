"""Generate deterministic, fictional source extracts using only the Python standard library."""
from __future__ import annotations
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
AS_OF = date(2026, 9, 30)


def write(name, rows):
    with (RAW / f'{name}.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate():
    RAW.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    teams = [{'team_id': f'T{i}', 'team_name': n} for i, n in enumerate(['North', 'Central', 'South'], 1)]
    advisers = [{'adviser_id': f'A{i:02}', 'adviser_name': f'Adviser {i:02}', 'team_id': f'T{(i-1)//4+1}'} for i in range(1, 13)]
    clients = [{'client_id': f'C{i:04}', 'client_name': f'Client {i:04}', 'adviser_id': f'A{(i-1)%12+1:02}' if i != 500 else '', 'segment': rng.choices(['Core', 'Premier', 'Private'], [45, 35, 20])[0], 'status': 'Active'} for i in range(1, 501)]
    tasks, fees, ledger = [], [], []
    months = [(2025 + (3 + i)//12, (3 + i)%12 + 1) for i in range(18)]  # April 2025 to September 2026
    task_id = 0
    for year, month in months:
        for client in clients:
            cid = client['client_id']
            # Different cadences create a realistic mix of scheduled reviews and servicing work.
            if rng.random() < .32:
                task_id += 1
                due = date(year, month, rng.randint(1, 27))
                kind = rng.choices(['Annual review', 'Onboarding', 'Service request'], [45, 15, 40])[0]
                created = due - timedelta(days=rng.randint(7, 45))
                draw = rng.random()
                status = 'Completed' if draw < .73 else ('Cancelled' if draw < .77 else 'Open')
                completed = max(created, due + timedelta(days=rng.randint(-12, 19))) if status == 'Completed' else None
                if completed and completed > AS_OF:
                    status, completed = 'Open', None
                tasks.append({'task_id': f'K{task_id:05}', 'client_id': cid, 'task_type': kind, 'created_date': created.isoformat(), 'due_date': due.isoformat(), 'status': status, 'completed_date': completed.isoformat() if completed else '', 'stage': rng.choice(['Documents', 'Verification', 'Ready for review']) if kind == 'Onboarding' and status == 'Open' else ''})
            # $ values are synthetic monthly advisory fees, recorded in integer cents.
            fee_cents = rng.randint(15000, 90000)
            fee_id = f'F{year}{month:02}{cid}'
            row = {'fee_id': fee_id, 'client_id': cid, 'fee_date': date(year, month, 1).isoformat(), 'amount_cents': fee_cents}
            fees.append(row)
            ledger.append({'ledger_id': f'L{year}{month:02}{cid}', 'fee_id': fee_id, 'posting_date': date(year, month, 2).isoformat(), 'amount_cents': fee_cents})
    # Forward-looking review obligations are part of the snapshot, outside the 18-month history.
    for client in clients[:60]:
        task_id += 1
        due = date(2026, 10, rng.randint(1, 30))
        tasks.append({'task_id': f'K{task_id:05}', 'client_id': client['client_id'], 'task_type': 'Annual review', 'created_date': '2026-09-20', 'due_date': due.isoformat(), 'status': 'Open', 'completed_date': '', 'stage': ''})
    # Deliberate source issues for the investigation story.
    fees.append(dict(fees[0]))  # duplicate identifier, quarantined
    task = next(t for t in tasks if t['status'] == 'Completed' and t['due_date'] < '2026-09-01')
    task['completed_date'] = ''  # unsubstantiated completion, quarantined
    ledger[-1]['amount_cents'] += 25000  # $250 finance difference
    ledger.append({'ledger_id': 'LUNMATCHED', 'fee_id': 'F-NOT-IN-OPERATIONS', 'posting_date': '2026-09-02', 'amount_cents': 17500})
    for name, rows in [('teams', teams), ('advisers', advisers), ('clients', clients), ('tasks', tasks), ('fees', fees), ('ledger', ledger)]:
        write(name, rows)
    return {'clients': len(clients), 'tasks': len(tasks), 'fees': len(fees), 'ledger': len(ledger)}

if __name__ == '__main__':
    print(generate())
