# RAID log

| ID | Type | Item | Action | Status |
|---|---|---|---|---|
| R1 | Risk | Trial capacity lapses before handover | All items are in Git. Reassign workspaces to a paid F capacity in the same region | Open |
| R2 | Risk | Source publisher changes column types between months | Declared type map in bronze. Type drift caught at load | Mitigated |
| A1 | Assumption | TLC data dictionary codes are the agreed reference data | Confirm with the client's data owner | Open |
| A2 | Assumption | Trips up to one day outside the file month are valid late arrivals | Confirm the tolerance with the client | Open |
| A3 | Assumption | Negative totals (refunds and voids) are excluded from revenue | Quarantined pending a client rule | Open |
| I1 | Issue | January 2025 files add `cbd_congestion_fee` | `mergeSchema` in bronze, 0 for earlier months in silver, added to gold and the model | Closed |
| I2 | Issue | HTTP copy returned 403 for monthly files | Relative URL expression was not resolving. Fixed with string interpolation `@{item()}` | Closed |
| I3 | Issue | Copilot draft placed notebook cell metadata before the code, breaking the Fabric Git format | Caught in pull request review and corrected before merge | Closed |
| I4 | Issue | Report visuals failed for the test analyst | Direct Lake was using the viewer's identity. Switched the model to a fixed identity connection | Closed |
| I5 | Issue | Lakehouse SQL endpoint can lag behind Spark writes | Refresh step documented in the runbook | Open |
| I6 | Issue | First warehouse deployment to TEST failed: the reconciliation view referenced lakehouse tables that did not exist in an empty TEST stage, leaving an unbound wh_gold | Deleted the orphan and staged the release: storage and code, load data in TEST, warehouse, then model, report and orchestration | Closed |
| I7 | Issue | Direct Lake on OneLake model stayed bound to the DEV warehouse after deployment and data source rules are not available for Direct Lake | Repointed the source expression to TEST's workspace and warehouse IDs in TMDL view as a documented post-deployment step. Long term: fabric-cicd find and replace on the IDs during release | Closed |
| I8 | Issue | TEST pl_master Script activities failed to log in to wh_gold: deployment swapped the warehouse ID to TEST but kept DEV's SQL endpoint hostname (the hostname encodes the workspace ID) | Reselected TEST's wh_gold on the three Script activities as a post-deployment step. Long term: fabric-cicd find and replace on the SQL endpoint hostname | Closed |
| D1 | Dependency | TLC publishes files monthly | Month parameter on `pl_master` so late files load on their own | Open |
