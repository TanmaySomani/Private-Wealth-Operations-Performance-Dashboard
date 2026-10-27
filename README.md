# Private Wealth Operations & Performance Dashboard

A portfolio case study for a fictional Australian private wealth advisory firm. It turns fragmented service and finance extracts into an interactive **Streamlit** management dashboard, and a reproducible SQL reporting model. All names, figures, budgets, and events are synthetic. No claim is made about a real firm's data or requirements.

**Live dashboard:** [wealth-operations-dashboard.streamlit.app](https://wealth-operations-dashboard.streamlit.app/)

## The business problem

An operations manager receives separate client, adviser, service and finance spreadsheets. Inconsistent records make it hard to answer which client commitments are overdue, where workloads are building, and whether recorded fees match the finance ledger. Manual reconciliation slows reporting and makes it difficult to know whether management can trust the result.

**Decision to support:** prioritise overdue client obligations, allocate service capacity and investigate fee or data-quality exceptions before publishing a management pack. This project deliberately adds source errors, makes them visible, and prevents unsafe rows from inflating the dashboard.

## Run the dashboard

Requires Python 3.10–3.13 and pip. Python 3.12 is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m wealth_dashboard.generate   # optional: regenerate deterministic synthetic CSVs
python -m wealth_dashboard.pipeline   # rebuild the SQLite reporting database
python -m streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`. To run the independent pipeline checks: `python -m unittest discover -s tests -v`.

The dashboard contains four pages:

1. **Executive overview:** clients, fees versus a clearly labelled synthetic plan, overdue reviews, on-time delivery and trends.
2. **Team & adviser scorecards:** caseload, overdue workload, due-task outcomes and median turnaround.
3. **Client service operations:** open onboarding, ageing, upcoming reviews and a prioritised queue.
4. **Reporting assurance:** quarantined rows, ownership exceptions, finance reconciliation and the last successful local load.

The sidebar's team, adviser and month selectors affect relevant flows; snapshot workload and client counts ignore the period selector. Unassigned clients appear at firm level, and finance-only exceptions appear only at firm level because they have no client or team. Validation counts always cover the whole load. See the [metric dictionary](docs/metrics.md) before interpreting figures.

## How it works

```text
Synthetic CSV extracts ──> validation + quarantine ──> SQLite dimensions / facts / views
                         └─> issue register                 └─> Streamlit dashboard
Finance ledger ───────────> reconciliation view
```

The generator uses a fixed seed and a 30 September 2026 business snapshot. The historical period is April 2025–September 2026, with 60 scheduled reviews in October. Fees are integer cents throughout the pipeline. Accepted tables and SQL views are in `data/curated/wealth.db`; raw CSVs are in `data/raw/`. The database is rebuilt to a temporary file and swapped only after a successful load. The pipeline records the latest successful local build, not an automated refresh history.

The illustrative monthly fee plan is $100,000 per team; it is not inferred from revenue or a real budget. No adviser-level target is defined. Client ownership and statuses are current snapshots, not historical slowly changing dimensions. The dataset is deliberately designed for demonstration, so its results are not industry benchmarks.

## Explore the case study

- [Requirements and problem definition](docs/problem-and-requirements.md)
- [Metric dictionary and filter rules](docs/metrics.md)
- [Data model, quality controls and lineage](docs/data-and-controls.md)
- [Management findings and recommended actions](docs/management-commentary.md)
- [Test log and known limitations](docs/test-log.md)
- [SQL schema](sql/schema.sql) and [reporting views](sql/views.sql)

## Portfolio positioning

A truthful description for a CV or interview:

> Built a Streamlit private-wealth operations reporting prototype using Python and SQL, with synthetic service and finance data, validation controls and fee reconciliation.

**Prototype scope:** Streamlit is a local prototype without authentication or row-level security. Do not use it with real client data.
