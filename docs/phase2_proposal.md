# Phase 2 proposal

Phase 1 delivered a reconciled monthly reporting platform. These options build on it, in the order I would recommend.

| # | Option | Value to the client | Effort |
|---|---|---|---|
| 1 | Automated releases with fabric-cicd and GitHub Actions | Repeatable deployments with no manual steps and an approval gate before TEST and production | Medium |
| 2 | Purview glossary, ownership and data quality rules | Business ownership of definitions such as Revenue and Trips, visible to every analyst | Small |
| 3 | Alerting on failed runs and reconciliation (Teams or email) | The support team hears about failures before the client does | Small |
| 4 | Live trip feed with Eventstream and Eventhouse | An operations view that updates within minutes instead of monthly | Medium |
| 5 | Copilot in Power BI on a paid capacity | Self-service questions in plain English on top of the governed model | Small |

## Suggested sequence

- **Sprint 1:** options 1 and 3, so releases and support are solid before anything new is added.
- **Sprint 2:** option 2, to give the business ownership of definitions.
- **Sprint 3:** options 4 and 5, once the client confirms the operational use case and capacity budget.

## Questions for the client

1. Who owns the definition of Revenue and should refunds be shown separately?
2. What tolerance is acceptable for late-arriving trips?
3. Is a near real-time view worth the extra capacity cost for their operations team?
