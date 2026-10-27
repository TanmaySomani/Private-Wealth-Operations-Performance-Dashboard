# Problem statement and requirements

## Context

Meridian Private Wealth is fictional. Its operations manager consolidates separate client, service and fee extracts to produce a monthly management pack. A duplicate fee can inflate revenue, a completed review without a completion date can hide overdue work, and a finance posting may not match the operational record. Without documented definitions and an exception register, leaders cannot distinguish operational performance from data defects.

## Objective

Provide a consistent, auditable view of service obligations, adviser capacity and fee reconciliation so management can decide where to intervene and whether figures are fit to share.

## Stakeholders and decisions

| Stakeholder | Decision | Information needed |
|---|---|---|
| Operations manager | Prioritise backlogs and resolve ownership gaps | Overdue work, on-time outcomes, unassigned clients |
| Team manager | Balance workloads and investigate bottlenecks | Caseload, open work, due-task outcomes, turnaround |
| Client services | Progress onboarding and prepare upcoming reviews | Stage, age, client and due date |
| Finance | Investigate differences before publication | Matched and unmatched fees, signed differences |
| Reporting owner | Assess fitness for use | Rejections, exceptions and last successful load |

## Scope and acceptance criteria

- Use reproducible fictional data for 500 clients, 12 advisers, 3 teams and 18 historical months; include upcoming scheduled reviews.
- Display four interactive views with consistent ownership and date filters; distinguish snapshot measures from period flows.
- Define the denominator and cancellation, incomplete and overdue rules explicitly.
- Quarantine duplicated fee identifiers and completed tasks without valid completion dates. Retain unassigned clients and flag them.
- Independently reconcile operations and finance without silently dropping unmatched entries or multiplying fees.
- Deliver runnable source, SQL views, documentation and tests.

## Assumptions and non-goals

Requirements are author-created assumptions; there were no stakeholder interviews. The synthetic fee plan and status distributions are illustrative. Currency is AUD. Real client information, investment returns, live integrations, authentication, production deployment, scheduling and notification automation are outside the implemented prototype. Ownership is as at the snapshot, so the dashboard does not reconstruct historical adviser assignments.
