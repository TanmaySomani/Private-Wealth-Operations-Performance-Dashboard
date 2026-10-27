PRAGMA foreign_keys = ON;
CREATE TABLE teams (team_id TEXT PRIMARY KEY, team_name TEXT NOT NULL);
CREATE TABLE advisers (adviser_id TEXT PRIMARY KEY, adviser_name TEXT NOT NULL, team_id TEXT NOT NULL REFERENCES teams(team_id));
CREATE TABLE clients (client_id TEXT PRIMARY KEY, client_name TEXT NOT NULL, adviser_id TEXT REFERENCES advisers(adviser_id), segment TEXT NOT NULL, status TEXT NOT NULL);
CREATE TABLE tasks (task_id TEXT PRIMARY KEY, client_id TEXT NOT NULL REFERENCES clients(client_id), task_type TEXT NOT NULL, created_date TEXT NOT NULL, due_date TEXT NOT NULL, status TEXT NOT NULL, completed_date TEXT, stage TEXT);
CREATE TABLE fees (fee_id TEXT PRIMARY KEY, client_id TEXT NOT NULL REFERENCES clients(client_id), fee_date TEXT NOT NULL, amount_cents INTEGER NOT NULL);
CREATE TABLE ledger (ledger_id TEXT PRIMARY KEY, fee_id TEXT NOT NULL, posting_date TEXT NOT NULL, amount_cents INTEGER NOT NULL);
CREATE TABLE issues (issue_id INTEGER PRIMARY KEY, source TEXT NOT NULL, record_id TEXT NOT NULL, rule TEXT NOT NULL, disposition TEXT NOT NULL, detail TEXT NOT NULL);
CREATE TABLE load_log (load_id INTEGER PRIMARY KEY, snapshot_date TEXT NOT NULL, completed_at_utc TEXT NOT NULL, status TEXT NOT NULL);
