# Metric dictionary

Snapshot date: **30 September 2026**. Data and targets are fictional. Month selectors include the first through last day of each selected month, inclusive.

| Metric | Definition | Scope and caveat |
|---|---|---|
| Active clients | Count of distinct accepted clients with status Active | Current snapshot; ignores month selection. All 500 are active by design. |
| Recorded fees | Sum of accepted operational fee amounts / 100 | Fee date in selected period; no adjustment for finance exceptions. |
| Fees vs plan | (Recorded fees / synthetic plan) − 1 | $100,000 per team per selected month; firm plan is $300,000/month. Firm revenue includes unassigned clients. No adviser-level target. |
| On-time completion | Tasks completed on or before due date / all non-cancelled tasks due in selected period | Open and late completed tasks are in the denominator; cancelled tasks excluded. Invalid tasks are quarantined, so results are conditional on accepted data. A zero denominator is displayed as a dash. |
| Overdue reviews | Open annual reviews with due date strictly before snapshot | Snapshot balance; ignores month selection. A review due on snapshot day is not overdue. |
| Open tasks | All accepted tasks with status Open | Snapshot balance; includes future due dates; ignores month selection. |
| Overdue tasks | Open tasks with due date strictly before snapshot | Snapshot balance. |
| Upcoming reviews | Open annual reviews due from snapshot through snapshot + 30 days inclusive | Snapshot balance; source extract only. |
| Days overdue | Max(snapshot − due date, 0) in whole days | 0 covers due today and future tasks; 1–30, 31–60, 61+ are overdue bands. |
| Median turnaround | Median completion date − creation date in days | Completed accepted tasks due in selected period. |
| Reconciliation difference | Ledger cents minus operational cents, including unmatched values as zero on the missing side | Matches by fee ID. Finance-only items have no client/team; appear only in all-firm view. Operational fee date determines matched/missing-ledger period; posting date determines finance-only period. |
| Fee exception | Fee ID with unmatched side, unequal amounts, or multiple ledger entries | Finance ledger is aggregated by fee ID before comparison. |
| Quarantined rows | Number of unsafe source rows excluded from accepted tables | Whole load; not filtered by team or period. |

Snapshot metrics use accepted records and current ownership. Data errors can affect the apparent result: the unsupported completed review is excluded, not counted as overdue, until a source owner establishes its true status.
