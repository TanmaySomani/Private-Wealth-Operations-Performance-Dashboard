CREATE VIEW client_dimension AS
SELECT c.*, a.adviser_name, a.team_id, t.team_name
FROM clients c LEFT JOIN advisers a ON c.adviser_id = a.adviser_id LEFT JOIN teams t ON a.team_id = t.team_id;

CREATE VIEW task_reporting AS
SELECT k.*, c.client_name, c.segment, c.adviser_id, c.adviser_name, c.team_id, c.team_name,
       CASE WHEN k.status = 'Completed' AND k.completed_date <= k.due_date THEN 1 ELSE 0 END AS completed_on_time,
       CASE WHEN k.status = 'Open' AND k.due_date < (SELECT snapshot_date FROM load_log ORDER BY load_id DESC LIMIT 1) THEN 1 ELSE 0 END AS overdue_at_snapshot,
       CASE WHEN k.status = 'Completed' THEN CAST(julianday(k.completed_date) - julianday(k.created_date) AS INTEGER) END AS turnaround_days
FROM tasks k JOIN client_dimension c ON k.client_id = c.client_id;

CREATE VIEW fee_reporting AS
SELECT f.*, c.client_name, c.segment, c.adviser_id, c.adviser_name, c.team_id, c.team_name
FROM fees f JOIN client_dimension c ON f.client_id = c.client_id;

-- One row per operational fee plus each unmatched finance entry. Ledger duplicates
-- are intentionally aggregated, so a many-to-one match cannot multiply revenue.
CREATE VIEW fee_reconciliation AS
WITH l AS (SELECT fee_id, SUM(amount_cents) amount_cents, COUNT(*) ledger_count, MIN(posting_date) posting_date FROM ledger GROUP BY fee_id)
SELECT f.fee_id, f.client_id, f.fee_date, f.amount_cents AS operational_cents, l.amount_cents AS ledger_cents,
       COALESCE(l.amount_cents, 0) - f.amount_cents AS difference_cents,
       CASE WHEN l.fee_id IS NULL THEN 'Missing in ledger' WHEN l.ledger_count > 1 THEN 'Multiple ledger entries' WHEN l.amount_cents <> f.amount_cents THEN 'Amount mismatch' ELSE 'Matched' END AS match_status,
       c.adviser_id, c.adviser_name, c.team_id, c.team_name
FROM fees f LEFT JOIN l ON f.fee_id = l.fee_id LEFT JOIN client_dimension c ON f.client_id = c.client_id
UNION ALL
SELECT l.fee_id, NULL, l.posting_date, NULL, l.amount_cents, l.amount_cents, 'Missing in operations', NULL, NULL, NULL, NULL
FROM l LEFT JOIN fees f ON f.fee_id = l.fee_id WHERE f.fee_id IS NULL;
