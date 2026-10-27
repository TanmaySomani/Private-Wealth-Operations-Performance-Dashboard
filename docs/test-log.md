# Test log

Run locally with `python -m unittest discover -s tests -v`. The tests rebuild a temporary database from deterministic source extracts.

| Check | Expected result | Result |
|---|---|---|
| Client count and known exceptions | 500 clients; two quarantined rows and one retained ownership exception | Passed |
| Duplicate and invalid task controls | 9,000 accepted fees; no completed tasks without a completion date | Passed |
| Reconciliation conservation | View totals equal each underlying table; one mismatch and one finance-only entry; net $425 | Passed |
| Snapshot and on-time flags | No overdue flag for closed/future tasks; on-time only when completed by due date | Passed |
| Failed rebuild | Missing source raises an error and leaves the previous database byte-for-byte intact | Passed |

The generated extracts use seed 42. Load timestamps vary. These checks establish specific pipeline invariants; they are not an independent audit or a test of all possible malformed inputs. Production authentication, scheduled refresh, automation and live user acceptance have not been tested.

On 27 October 2026, Streamlit AppTest ran all four pages without exceptions, including a Central team and Adviser 05 filter selection. A local browser preview was also used to check the executive layout. This does not establish production usability, accessibility or security.

