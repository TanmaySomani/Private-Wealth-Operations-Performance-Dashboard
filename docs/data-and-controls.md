# Data, lineage and controls

## Grain and model

- `teams`: one row per team; `advisers`: one row per adviser and current team; `clients`: one row per client and current adviser, which can be unassigned.
- `tasks`: one row per service obligation with created, due and completion dates. `task_reporting` enriches tasks with current ownership and computes snapshot flags.
- `fees`: one row per operational fee identifier. `ledger`: one row per finance posting. `fee_reconciliation` aggregates ledger postings by fee ID before joining, then unions finance-only items; signed difference is ledger minus operations.
- `issues`: one row per rejected or retained-with-exception record. `load_log`: the latest successful local build and business snapshot.

`client_dimension` is a flattened current-ownership dimension; `task_reporting` and `fee_reporting` are separate facts, avoiding a task-to-fee many-to-many join. SQL views are in `sql/views.sql`. There is no effective-dated ownership or client history.

## Source-to-report investigation

| Source issue | Detection | Disposition | Effect / next action |
|---|---|---|---|
| Duplicate fee `F202504C0001` | Duplicate fee ID | Second row quarantined | Avoids $185.34 overstatement. Confirm the source system's intended record before removing the duplicate upstream. |
| Task `K00001` marked completed without completion date | Completion date validation | Quarantined | Neither treated as completed nor assumed overdue. Obtain the true status and evidence, correct the source, and rebuild. |
| Client `C0500` has no adviser | Required ownership exception | Retained with exception | Included at firm level; cannot be attributed to a team or adviser until assigned. |
| One finance posting differs by $250 | Fee ID amount comparison | Both records retained; flagged | Finance should investigate and resolve the discrepancy. |
| Finance-only posting of $175 | Fee ID absent from operations | Retained as unmatched | Finance and operations should establish whether the posting is missing upstream or erroneous. |

After quarantine, operations total $4,733,854.34 and finance totals $4,734,279.34. The $425 net difference consists of $250 mismatch plus $175 finance-only posting. This is an **identified, unresolved** difference, not a completed source correction or balanced reconciliation. Rebuild from corrected files to demonstrate resolution; the included generator intentionally reintroduces the issues.

## Pipeline rules and limits

`wealth_dashboard/pipeline.py` checks identifiers, dimension relationships, required dimension attributes, valid task types/statuses and dates, completion logic, non-negative integer amounts and snapshot cut-offs. Invalid fact rows are quarantined with the source record in the issue detail. It retains a client without an adviser. Accepted rows are written to a temporary SQLite database and atomically replace the previous successful build. If a build fails, the prior database stays in place; failed builds are not persisted in a run-history table. This is a small prototype, not a comprehensive production data quality framework.

The generator always regenerates the same sources from seed 42. Dates are ISO 8601, money is integer AUD cents, and load time is UTC. Finance-only records cannot inherit a team or client. Access control and scheduled orchestration are not implemented.
