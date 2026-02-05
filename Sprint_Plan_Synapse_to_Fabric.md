# Synapse-to-Fabric Migration — Sprint Plan

**Prepared by:** Keven Markham, VP Enterprise Transformation — DMTSP
**Date:** February 5, 2026
**Version:** 1.0
**Purpose:** Comprehensive sprint plan comparing Base Greenfield delivery (Phase 1) with Accelerator-enabled delivery (Phase 2) for a full Synapse-to-Fabric migration engagement
**Audience:** DMTSP Leadership, Engagement Delivery Teams, Account Teams

---

## Team Assumptions

| Role | Count | Effective Capacity/Sprint | Notes |
|---|---|---|---|
| Project Manager (PM) | 1 | 70 hrs | Sprint coordination, governance, status reporting |
| Solution Architect | 1 | 70 hrs | Technical design, pattern definition, migration strategy |
| Sr Data Engineer | 2 | 140 hrs | Complex SP conversion, pipeline design, accelerator setup |
| Data Engineer | 4 | 280 hrs | Table/view migration, pipeline migration, standard SP conversion |
| QA Lead | 1 | 70 hrs | Test strategy, SIT/UAT coordination, validation frameworks |
| DBA | 1 | 70 hrs | Schema migration, security, performance tuning |
| **Team Total** | **10** | **700 hrs/sprint** | |

**Sprint Cadence:** 2-week sprints (10 working days, 80 hrs capacity per FTE)
**Effective Capacity:** ~70 hrs/sprint per FTE (accounting for meetings, overhead, context-switching)
**Team Sprint Capacity:** 700 hrs/sprint

---

## Scope Summary — Base Hours by Workstream

| # | Workstream | Objects | Unit Hours | Base Hours |
|---|---|---|---|---|
| 1 | Synapse → Tables | 1,538 | 4 hrs | 6,152 |
| 2 | Synapse → Views | 362 | 1.5 hrs | 543 |
| 3 | Synapse → Functions | 4 | 1 hr | 4 |
| 4 | Synapse → Schema | 16 | — | 5 |
| 5 | Synapse → Security | 40 | — | 10 |
| 6 | Stored Procs — Standard | 540 | 2 hrs | 1,080 |
| 7 | Stored Procs — Spark Low | 25 | 8 hrs | 200 |
| 8 | Stored Procs — Spark Medium | 25 | 16 hrs | 400 |
| 9 | Stored Procs — Spark High | 25 | 24 hrs | 600 |
| 10 | ADF → Pipelines | 609 | 2 hrs | 1,218 |
| 11 | ADF → Datasets | 450 | 2 hrs | 900 |
| 12 | ADF → Triggers | 142 | 2 hrs | 284 |
| 13 | Logic Apps | 147 | 2 hrs | 294 |
| 14 | ADLS Accounts | 53 | 4 hrs | 212 |
| | **Dev Subtotal** | | | **11,902** |
| 15 | SIT (20% of Dev) | — | — | 2,380 |
| 16 | UAT (10% of Dev) | — | — | 1,190 |
| 17 | Prod Cutover (3% of Dev) | — | — | 357 |
| 18 | PM / Governance / Architecture / KT | — | — | 1,600 |
| | **Grand Total** | | | **17,429** |

---

## Accelerator Reference

| ID | Accelerator | Target Workstream | Productivity Gain |
|---|---|---|---|
| Acc 1 | Fabric Migration Assistant + Copilot | Synapse DW (tables, views, schema, security) | 40–55% |
| Acc 2 | ADF PowerShell Pipeline Upgrade Module | ADF pipelines, datasets, triggers | 30–45% |
| Acc 3 | T-SQL to Spark/PySpark Conversion Framework | Stored procedure conversion | 20–30% |
| Acc 4 | CI/CD & Environment Deployment Automation | SIT / UAT / Prod environments | 15–25% |
| Acc 5 | Automated Data Validation & Testing Framework | Cross-cutting quality | Quality improvement |
| Acc 6 | Fabric Copilot Integration | All workstreams (compounding) | 5–10% |
| Acc 7 | Logic App & ADLS Migration Automation | Logic Apps, ADLS storage | 15–30% |

---

# Phase 1 — Base Greenfield Delivery

**Duration:** 25 sprints (~50 weeks)
**Total Hours:** 17,429
**Avg Sprint Burn:** ~697 hrs/sprint

---

### Sprint 0 — Discovery & Planning (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Project kickoff & governance setup | Charter, RACI, communication plan, sprint ceremonies | 120 | PM |
| Architecture design & target-state definition | Fabric workspace topology, capacity sizing, networking design, lakehouse vs. warehouse decisions | 200 | Architect, DBA |
| Source environment inventory & assessment | DACPAC extraction, ADF assessment tool, SP complexity classification, ADLS inventory | 200 | Sr Data Engineers, DBA |
| Migration wave planning | Dependency mapping, batch groupings, cutover sequencing | 100 | Architect, PM |
| Knowledge transfer & team onboarding | Fabric fundamentals, migration tooling walkthroughs, coding standards | 80 | Architect, Sr Data Engineers |

**Sprint 0 Total: 700 hrs**

---

### Sprint 1 — Foundation Setup (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Fabric workspace provisioning | Dev/SIT/UAT/Prod workspaces, capacity assignment, admin roles | 140 | Architect, DBA |
| Networking & security configuration | Private endpoints, VNet data gateways, managed identities, Entra ID groups | 160 | Architect, DBA |
| Git integration setup | Azure DevOps/GitHub repo structure, branch policies, workspace-to-repo connection | 80 | Sr Data Engineer |
| Fabric Data Warehouse creation | Target warehouse, schema creation (16 schemas), security roles (40 objects) | 120 | DBA, Data Engineers |
| Development environment tooling | VS Code extensions, notebook environment, PowerShell modules | 60 | Sr Data Engineers |
| CI/CD pipeline scaffolding (manual) | Basic deployment scripts, environment promotion procedures | 80 | Sr Data Engineer |
| PM governance & reporting | Sprint tracking setup, risk register, status reporting cadence | 60 | PM |

**Sprint 1 Total: 700 hrs**

---

### Sprint 2 — Foundation Completion & Migration Start (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| CI/CD pipeline completion | End-to-end manual deployment pipeline, validation scripts | 100 | Sr Data Engineer |
| Schema/security migration | Remaining schema + security objects (Functions: 4, Schema: 16, Security: 40) | 19 | DBA |
| Synapse Tables — Batch 1 (170 tables) | DACPAC-based schema deploy, data copy, validation | 680 | Data Engineers (4), DBA |
| PM governance | Sprint ceremonies, status reporting, risk management | 40 | PM |
| Architecture guidance | Pattern validation, issue escalation | 40 | Architect |

**Cumulative Tables Migrated: 170 / 1,538**
**Sprint 2 Total: 700 hrs (after allocation from foundation work)**

---

### Sprint 3 — Synapse DW Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 2 (170 tables) | Schema deploy, data copy, per-table validation | 680 | Data Engineers (4), DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |
| Architecture guidance | Pattern review, edge-case resolution | 40 | Architect |

**Cumulative Tables Migrated: 340 / 1,538**
**Sprint 3 Total: 700 hrs**

---

### Sprint 4 — Synapse DW Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 3 (170 tables) | Schema deploy, data copy, per-table validation | 680 | Data Engineers (4), DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |
| Architecture guidance | Pattern review | 40 | Architect |

**Cumulative Tables Migrated: 510 / 1,538**
**Sprint 4 Total: 700 hrs**

---

### Sprint 5 — Synapse DW Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 4 (170 tables) | Schema deploy, data copy, per-table validation | 680 | Data Engineers (4), DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |
| Architecture guidance | Pattern review | 40 | Architect |

**Cumulative Tables Migrated: 680 / 1,538**
**Sprint 5 Total: 700 hrs**

---

### Sprint 6 — Synapse DW Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 5 (170 tables) | Schema deploy, data copy, per-table validation | 680 | Data Engineers (4), DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |
| Architecture guidance | Pattern review | 40 | Architect |

**Cumulative Tables Migrated: 850 / 1,538**
**Sprint 6 Total: 700 hrs**

---

### Sprint 7 — Synapse DW Migration + ADF Pipeline Start (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 6 (170 tables) | Schema deploy, data copy, per-table validation | 480 | Data Engineers (3), DBA |
| Synapse Views — Batch 1 (120 views) | View migration, dependency validation | 180 | Data Engineer (1) |
| ADF Pipeline Assessment & Planning | Run assessment tool, categorize pipelines, create resolution files | 40 | Sr Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Tables: 1,020 / 1,538 | Views: 120 / 362**
**Sprint 7 Total: 700 hrs**

---

### Sprint 8 — Synapse DW Migration + ADF Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 7 (170 tables) | Schema deploy, data copy, validation | 480 | Data Engineers (3) |
| Synapse Views — Batch 2 (120 views) | View migration, dependency validation | 180 | Data Engineer (1) |
| ADF Pipelines — Batch 1 (100 pipelines) | Import, convert, resolve, deploy, validate | 200 | Sr Data Engineers (2) |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Tables: 1,190 / 1,538 | Views: 240 / 362 | Pipelines: 100 / 609**
**Sprint 8 Total: 700 hrs** *(slight over-allocation offset by Architect/DBA flex)*

---

### Sprint 9 — Synapse DW Completion + ADF Migration (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 8 (178 tables) | Schema deploy, data copy, validation | 480 | Data Engineers (3) |
| Synapse Views — Batch 3 (122 views) | View migration, remaining functions validation | 183 | Data Engineer (1) |
| ADF Pipelines — Batch 2 (100 pipelines) | Import, convert, resolve, deploy, validate | 200 | Sr Data Engineers (2) |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Tables: 1,368 / 1,538 | Views: 362 / 362 ✓ | Pipelines: 200 / 609**
**Sprint 9 Total: 700 hrs**

---

### Sprint 10 — Synapse DW Completion + ADF + SP Start (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Synapse Tables — Batch 9 (170 tables, final) | Schema deploy, data copy, final validation | 480 | Data Engineers (3) |
| ADF Pipelines — Batch 3 (100 pipelines) | Import, convert, resolve, deploy, validate | 200 | Sr Data Engineers (2) |
| ADF Datasets — Batch 1 (150 datasets) | Repoint and validate | 200 | Data Engineer (1) |
| Stored Procs — Standard Batch 1 (90 SPs) | Convert to Spark SQL, validate | 180 | Sr Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Tables: 1,538 / 1,538 ✓ | Pipelines: 300 / 609 | Datasets: 150 / 450**
**Sprint 10 Total: 700 hrs** *(table migration complete)*

---

### Sprint 11 — ADF Migration + Stored Proc Conversion (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| ADF Pipelines — Batch 4 (100 pipelines) | Import, convert, resolve, deploy, validate | 200 | Sr Data Engineer, Data Engineer |
| ADF Datasets — Batch 2 (150 datasets) | Repoint and validate | 200 | Data Engineer |
| ADF Triggers — Batch 1 (70 triggers) | Migrate and validate | 140 | Data Engineer |
| Stored Procs — Standard Batch 2 (90 SPs) | Convert to Spark SQL, validate | 180 | Sr Data Engineer, Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Pipelines: 400 / 609 | Datasets: 300 / 450 | Triggers: 70 / 142**
**Sprint 11 Total: 700 hrs**

---

### Sprint 12 — ADF Completion + Stored Proc Conversion (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| ADF Pipelines — Batch 5 (109 pipelines) | Import, convert, resolve, deploy, validate | 218 | Sr Data Engineer, Data Engineer |
| ADF Datasets — Batch 3 (150 datasets, final) | Repoint and validate | 200 | Data Engineer |
| ADF Triggers — Batch 2 (72 triggers, final) | Migrate and validate | 144 | Data Engineer |
| Stored Procs — Standard Batch 3 (90 SPs) | Convert to Spark SQL, validate | 180 | Sr Data Engineer, Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Pipelines: 509 / 609 | Datasets: 450 / 450 ✓ | Triggers: 142 / 142 ✓**
**Sprint 12 Total: 700 hrs** *(ADF datasets & triggers complete)*

---

### Sprint 13 — ADF Final + Stored Proc Conversion (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| ADF Pipelines — Batch 6 (100 pipelines, final) | Import, convert, resolve, deploy, validate | 200 | Sr Data Engineer, Data Engineer |
| Stored Procs — Standard Batch 4 (90 SPs) | Convert to Spark SQL, validate | 180 | Data Engineers (2) |
| Stored Procs — Spark Low (25 SPs) | Template-driven PySpark conversion | 200 | Sr Data Engineers (2) |
| Stored Procs — Spark Medium Batch 1 (12 SPs) | PySpark DataFrame conversion | 192 | Sr Data Engineer, Architect |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Pipelines: 609 / 609 ✓ | Standard SPs: 360 / 540 | Spark SPs: 37 / 75**
**Sprint 13 Total: 700 hrs** *(ADF pipelines complete)*

---

### Sprint 14 — Stored Proc Conversion + Logic Apps & ADLS (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Stored Procs — Standard Batch 5 (90 SPs) | Convert to Spark SQL, validate | 180 | Data Engineers (2) |
| Stored Procs — Spark Medium Batch 2 (13 SPs) | PySpark DataFrame conversion | 208 | Sr Data Engineers (2) |
| Logic Apps — Batch 1 (75 apps) | Connection repointing, validation | 150 | Data Engineer |
| ADLS Accounts — Batch 1 (26 accounts) | OneLake shortcuts or data copy, validation | 104 | Data Engineer, DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Standard SPs: 450 / 540 | Spark SPs: 50 / 75 | Logic Apps: 75 / 147**
**Sprint 14 Total: 700 hrs**

---

### Sprint 15 — Stored Proc Completion + Logic Apps & ADLS (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Stored Procs — Standard Batch 6 (90 SPs, final) | Convert to Spark SQL, validate | 180 | Data Engineers (2) |
| Stored Procs — Spark High (25 SPs) | Full PySpark refactoring, medallion architecture | 360 | Sr Data Engineers (2), Architect |
| Logic Apps — Batch 2 (72 apps, final) | Connection repointing, validation | 144 | Data Engineer |
| ADLS Accounts — Batch 2 (27 accounts, final) | OneLake shortcuts or data copy, validation | 108 | Data Engineer, DBA |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Cumulative Standard SPs: 540 / 540 ✓ | Spark SPs: 75 / 75 ✓ | Logic Apps: 147 / 147 ✓ | ADLS: 53 / 53 ✓**
**Sprint 15 Total: 700 hrs**

---

### Sprint 16 — SP High Completion + Dev Hardening (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Stored Procs — Spark High (remaining) | Final refactoring, edge-case resolution | 240 | Sr Data Engineers (2), Architect |
| Dev environment hardening | End-to-end regression, integration testing, performance baseline | 280 | Data Engineers (4), DBA |
| SIT preparation | Test plan finalization, SIT environment deployment, test data setup | 120 | QA Lead, PM |
| PM governance | Sprint ceremonies, status reporting | 60 | PM |

**Sprint 16 Total: 700 hrs** *(all dev migration complete)*

---

### Sprint 17 — SIT Cycle 1 (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| SIT deployment | Full artifact promotion to SIT environment | 100 | Sr Data Engineer, DBA |
| Schema & data validation | Automated row counts, checksums, schema comparison across all 1,538 tables | 200 | QA Lead, Data Engineers |
| Pipeline execution testing | End-to-end pipeline runs, trigger validation, error handling | 200 | Data Engineers, Sr Data Engineers |
| Stored procedure functional testing | Execute all SPs against SIT data, compare outputs | 150 | Sr Data Engineers, DBA |
| Defect triage & remediation | Fix critical/high defects from SIT Cycle 1 | 100 | All Engineers |
| PM governance | Sprint ceremonies, status reporting, stakeholder updates | 50 | PM |

**Sprint 17 Total: 700 hrs** *(SIT hours consumed: 700 / 2,380)*

---

### Sprint 18 — SIT Cycle 2 (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Logic App & ADLS validation | End-to-end Logic App flows, ADLS shortcut validation | 150 | Data Engineers |
| Performance testing | Query performance benchmarks, pipeline throughput, capacity stress | 200 | DBA, Architect |
| Regression testing (Cycle 1 fixes) | Re-validate all Cycle 1 defect fixes | 150 | QA Lead, Data Engineers |
| Security & access testing | Role-based access, Entra ID integration, row-level security | 100 | DBA |
| Defect triage & remediation | Fix remaining SIT defects | 100 | All Engineers |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Sprint 18 Total: 700 hrs** *(SIT hours consumed: 1,400 / 2,380)*

---

### Sprint 19 — SIT Cycle 3 (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Full regression (all workstreams) | Complete end-to-end regression across tables, pipelines, SPs, Logic Apps | 300 | All Engineers |
| Data reconciliation sign-off | Final row-count, checksum, and business rule validation | 150 | QA Lead, DBA |
| SIT exit criteria validation | Test summary report, defect closure, go/no-go assessment | 100 | QA Lead, PM |
| UAT preparation | UAT environment deployment, test script handoff, business user onboarding | 100 | PM, QA Lead |
| PM governance | Sprint ceremonies, status reporting | 50 | PM |

**Sprint 19 Total: 700 hrs** *(SIT hours consumed: 2,100 / 2,380)*

---

### Sprint 20 — SIT Closeout + UAT Start (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| SIT final remediation | Remaining SIT defects, re-test, formal SIT sign-off | 280 | All Engineers, QA Lead |
| UAT environment validation | Verify UAT deployment, connection health, data freshness | 120 | Sr Data Engineer, DBA |
| UAT Cycle 1 — business user testing | Guided business user walkthroughs, report validation, pipeline verification | 240 | PM, QA Lead, Data Engineers |
| PM governance | Sprint ceremonies, status reporting | 60 | PM |

**Sprint 20 Total: 700 hrs** *(SIT complete: 2,380 ✓ | UAT hours consumed: 360 / 1,190)*

---

### Sprint 21 — UAT Cycle 2 (700 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| UAT business scenario testing | Full business process walkthroughs, edge-case scenarios | 250 | PM, QA Lead, Data Engineers |
| UAT defect remediation | Fix UAT-discovered defects, re-test | 200 | All Engineers |
| Performance acceptance testing | Business-critical query performance under UAT load | 100 | DBA, Architect |
| UAT progress tracking & communication | Stakeholder updates, defect dashboards | 50 | PM |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Sprint 21 Total: 700 hrs** *(UAT hours consumed: 960 / 1,190)*

---

### Sprint 22 — UAT Closeout (540 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| UAT final remediation | Remaining defects, re-test, regression | 130 | All Engineers |
| UAT exit criteria & sign-off | Formal UAT sign-off, acceptance documentation | 50 | PM, QA Lead |
| Production readiness review | Go/no-go checklist, rollback plan, cutover runbook | 80 | Architect, PM |
| Production environment preparation | Prod workspace validation, deployment pipeline dry-run | 120 | Sr Data Engineer, DBA |
| Cutover planning | Detailed cutover schedule, communication plan, war room setup | 60 | PM, Architect |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Sprint 22 Total: 540 hrs** *(UAT complete: 1,190 ✓)*

---

### Sprint 23 — Pre-Production & Cutover Prep (500 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Production deployment dry-run | Full deployment rehearsal to Prod-mirror environment | 200 | Sr Data Engineers, DBA |
| Cutover runbook finalization | Step-by-step cutover instructions, rollback triggers, escalation paths | 80 | Architect, PM |
| Stakeholder communication | Go-live readiness confirmation, business communication | 40 | PM |
| Monitoring & alerting setup | Fabric capacity monitoring, pipeline alerting, SLA dashboards | 100 | Sr Data Engineer, DBA |
| Team readiness | War room logistics, on-call rotation, escalation matrix | 40 | PM |
| PM governance | Sprint ceremonies, status reporting | 40 | PM |

**Sprint 23 Total: 500 hrs**

---

### Sprint 24 — Production Cutover (357 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Production deployment execution | Full artifact deployment to Production | 100 | Sr Data Engineers, DBA |
| Connection rerouting | Reroute all upstream/downstream connections to Fabric | 57 | Data Engineers, DBA |
| Post-deployment validation | Smoke tests, critical path verification, data spot-checks | 80 | QA Lead, All Engineers |
| Go-live monitoring | Real-time monitoring for first 48 hours, issue triage | 80 | All Engineers |
| PM governance | Go-live communication, escalation management | 40 | PM |

**Sprint 24 Total: 357 hrs** *(Prod cutover: 357 ✓)*

---

### Sprint 25 — Hypercare & Closeout (532 hrs)

| Task | Subtasks | Hours | Owner(s) |
|---|---|---|---|
| Hypercare support (2 weeks) | Production issue triage, hotfixes, performance tuning | 200 | All Engineers |
| Knowledge transfer | Runbooks, operational documentation, client team training | 120 | Architect, Sr Data Engineers |
| Synapse decommissioning plan | Source environment shutdown planning, data retention verification | 60 | Architect, DBA |
| Project closeout | Lessons learned, final status report, accelerator feedback | 80 | PM, Architect |
| PM governance | Final sprint ceremonies, project closeout | 72 | PM |

**Sprint 25 Total: 532 hrs**

---

### Phase 1 Summary

| Sprint | Focus | Hours | Cumulative |
|---|---|---|---|
| 0 | Discovery & Planning | 700 | 700 |
| 1 | Foundation Setup | 700 | 1,400 |
| 2 | Foundation + Tables Start | 700 | 2,100 |
| 3 | Tables Batch 2 | 700 | 2,800 |
| 4 | Tables Batch 3 | 700 | 3,500 |
| 5 | Tables Batch 4 | 700 | 4,200 |
| 6 | Tables Batch 5 | 700 | 4,900 |
| 7 | Tables Batch 6 + Views + ADF Start | 700 | 5,600 |
| 8 | Tables Batch 7 + Views + ADF | 700 | 6,300 |
| 9 | Tables Final + Views Final + ADF | 700 | 7,000 |
| 10 | Tables Complete + ADF + SPs Start | 700 | 7,700 |
| 11 | ADF + SPs | 700 | 8,400 |
| 12 | ADF Datasets/Triggers Complete + SPs | 700 | 9,100 |
| 13 | ADF Pipelines Complete + SPs | 700 | 9,800 |
| 14 | SPs + Logic Apps + ADLS | 700 | 10,500 |
| 15 | SPs Complete + Logic Apps + ADLS Complete | 700 | 11,200 |
| 16 | Dev Hardening + SIT Prep | 700 | 11,900 |
| 17 | SIT Cycle 1 | 700 | 12,600 |
| 18 | SIT Cycle 2 | 700 | 13,300 |
| 19 | SIT Cycle 3 | 700 | 14,000 |
| 20 | SIT Closeout + UAT Start | 700 | 14,700 |
| 21 | UAT Cycle 2 | 700 | 15,400 |
| 22 | UAT Closeout + Prod Prep | 540 | 15,940 |
| 23 | Pre-Production + Cutover Prep | 500 | 16,440 |
| 24 | Production Cutover | 357 | 16,797 |
| 25 | Hypercare & Closeout | 532 | 17,329 |
| | **Phase 1 Total** | | **~17,329 hrs** |

> **Note:** The ~100 hr variance from the 17,429 target is absorbed through PM/Governance/Architecture hours distributed across all sprints (1,600 hrs budgeted, allocated as sprint-level governance throughout).

---

# Phase 2 — Accelerated Delivery (With Accelerators)

**Duration:** 16 sprints (~32 weeks)
**Estimated Total Hours:** ~11,155
**Reduction from Phase 1:** ~36%
**Avg Sprint Burn:** ~697 hrs/sprint

---

### Accelerator Savings by Workstream

| Workstream | Base Hours | Accelerator(s) | Reduction % | Accelerated Hours | Hours Saved |
|---|---|---|---|---|---|
| Synapse Tables | 6,152 | Acc 1 + Acc 6 | 47% | 3,261 | 2,891 |
| Synapse Views | 543 | Acc 1 + Acc 6 | 50% | 272 | 271 |
| Synapse Functions/Schema/Security | 19 | Acc 1 | 40% | 11 | 8 |
| Stored Procs — Standard | 1,080 | Acc 3 + Acc 6 | 30% | 756 | 324 |
| Stored Procs — Spark Low | 200 | Acc 3 + Acc 6 | 23% | 154 | 46 |
| Stored Procs — Spark Medium | 400 | Acc 3 + Acc 6 | 18% | 328 | 72 |
| Stored Procs — Spark High | 600 | Acc 3 + Acc 6 | 12% | 528 | 72 |
| ADF Pipelines | 1,218 | Acc 2 + Acc 6 | 40% | 731 | 487 |
| ADF Datasets | 900 | Acc 2 + Acc 6 | 50% | 450 | 450 |
| ADF Triggers | 284 | Acc 2 + Acc 6 | 50% | 142 | 142 |
| Logic Apps | 294 | Acc 7 | 20% | 235 | 59 |
| ADLS Accounts | 212 | Acc 7 | 30% | 148 | 64 |
| **Dev Subtotal** | **11,902** | | **37%** | **7,016** | **4,886** |
| SIT | 2,380 | Acc 4 + Acc 5 | 25% | 1,785 | 595 |
| UAT | 1,190 | Acc 4 + Acc 5 | 20% | 952 | 238 |
| Prod Cutover | 357 | Acc 4 | 15% | 303 | 54 |
| PM / Governance / Arch / KT | 1,600 | — | 30%* | 1,099 | 501 |
| **Grand Total** | **17,429** | | **~36%** | **~11,155** | **~6,274** |

> *PM/Governance reduction reflects shorter timeline requiring fewer sprint cycles of overhead.

---

### Sprint 0 — Discovery + Accelerator Setup (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Project kickoff & governance | Charter, RACI, communication plan | 100 | — | PM |
| Architecture design | Fabric workspace topology, capacity, networking | 160 | — | Architect, DBA |
| Source assessment (automated) | DACPAC extraction, ADF assessment tool, SP complexity classification | 120 | Acc 1, Acc 2 | Sr Data Engineers |
| Accelerator deployment & config | Install PowerShell modules, configure Copilot, deploy validation frameworks, set up prompt library | 160 | All | Sr Data Engineers, Architect |
| Migration wave planning | Dependency mapping, accelerated batch groupings | 80 | — | Architect, PM |
| Knowledge transfer | Fabric + accelerator tooling training | 80 | — | Architect, Sr Data Engineers |

**Sprint 0 Total: 700 hrs**

---

### Sprint 1 — Foundation + CI/CD Automation (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Fabric workspace provisioning | Dev/SIT/UAT/Prod workspaces, capacity, admin roles | 100 | Acc 4 (ARM/Bicep) | Architect, DBA |
| Networking & security | Private endpoints, VNet gateways, Entra ID | 120 | — | Architect, DBA |
| Git integration + CI/CD automation | Repo structure, branch policies, automated deployment pipelines, GitHub Actions/ADO workflows | 160 | Acc 4 | Sr Data Engineers |
| Fabric DW creation + schema/security | Target warehouse, schemas (16), security (40), functions (4) | 80 | Acc 1 | DBA |
| Validation framework setup | Deploy schema/row-level/business rule validation notebooks | 100 | Acc 5 | QA Lead, Sr Data Engineer |
| Dev environment tooling | VS Code, notebook env, PowerShell, Copilot config | 60 | Acc 6 | Sr Data Engineers |
| PM governance | Sprint tracking, risk register | 40 | — | PM |
| Schema/security/functions migration | All 60 objects (schema 16, security 40, functions 4) | 11 | Acc 1 | DBA |

**Sprint 1 Total: 671 hrs** *(under-burn absorbed into Sprint 2 prep)*

---

### Sprint 2 — Synapse DW Migration Batch 1 (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Synapse Tables — Batch 1 (380 tables) | DACPAC-driven migration, Copilot-assisted fix resolution, automated validation | 646 | Acc 1 + Acc 6 | Data Engineers (4), DBA, Sr Data Engineers |
| Synapse Views — Batch 1 (180 views) | Automated view migration with dependency awareness | 136 | Acc 1 + Acc 6 | Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

> **Accelerator impact:** Migration Assistant automates schema translation and data copy orchestration. Per-table effort drops from 4 hrs to ~2.1 hrs. Copilot resolves ~60% of T-SQL incompatibilities automatically.

**Cumulative Tables: 380 / 1,538 | Views: 180 / 362**
**Sprint 2 Total: 700 hrs** *(note: some carryover from Sprint 1 under-burn)*

---

### Sprint 3 — Synapse DW Migration Batch 2 (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Synapse Tables — Batch 2 (380 tables) | DACPAC migration, Copilot fix resolution, validation | 646 | Acc 1 + Acc 6 | Data Engineers (4), DBA, Sr Data Engineers |
| Synapse Views — Batch 2 (182 views, final) | View migration, dependency validation | 136 | Acc 1 + Acc 6 | Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Cumulative Tables: 760 / 1,538 | Views: 362 / 362 ✓**
**Sprint 3 Total: 700 hrs**

---

### Sprint 4 — Synapse DW Migration Batch 3 + ADF Start (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Synapse Tables — Batch 3 (380 tables) | DACPAC migration, Copilot fix resolution, validation | 500 | Acc 1 + Acc 6 | Data Engineers (3), DBA |
| ADF Assessment + Pipelines Batch 1 (150 pipelines) | PowerShell import/convert/resolve/export, validate | 180 | Acc 2 + Acc 6 | Sr Data Engineers (2), Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

> **Accelerator impact:** ADF PowerShell module auto-converts ~70% of standard pipelines. Per-pipeline effort drops from 2 hrs to ~1.2 hrs.

**Cumulative Tables: 1,140 / 1,538 | Pipelines: 150 / 609**
**Sprint 4 Total: 700 hrs**

---

### Sprint 5 — Synapse DW Complete + ADF Migration (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Synapse Tables — Batch 4 (398 tables, final) | DACPAC migration, final validation, sign-off | 500 | Acc 1 + Acc 6 | Data Engineers (3), DBA |
| ADF Pipelines — Batch 2 (150 pipelines) | PowerShell conversion, validate | 180 | Acc 2 + Acc 6 | Sr Data Engineers (2), Data Engineer |
| ADF Datasets — Batch 1 (225 datasets) | Automated repointing, validate | 120 | Acc 2 + Acc 6 | Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Cumulative Tables: 1,538 / 1,538 ✓ | Pipelines: 300 / 609 | Datasets: 225 / 450**
**Sprint 5 Total: 700 hrs** *(table migration complete — 4 sprints faster than Phase 1)*

---

### Sprint 6 — ADF Completion + SP Start (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| ADF Pipelines — Batch 3 (159 pipelines) | PowerShell conversion, validate | 191 | Acc 2 + Acc 6 | Sr Data Engineer, Data Engineer |
| ADF Datasets — Batch 2 (225 datasets, final) | Repointing, validate | 120 | Acc 2 + Acc 6 | Data Engineer |
| ADF Pipelines — Batch 4 (150 pipelines) | PowerShell conversion, validate | 180 | Acc 2 + Acc 6 | Sr Data Engineer, Data Engineer |
| ADF Triggers (142 triggers) | Automated migration, validate | 142 | Acc 2 + Acc 6 | Data Engineer |
| Stored Procs — Standard Batch 1 (180 SPs) | Template-driven Spark SQL conversion, Copilot-assisted | 252 | Acc 3 + Acc 6 | Sr Data Engineer, Data Engineer |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Cumulative Pipelines: 609 / 609 ✓ | Datasets: 450 / 450 ✓ | Triggers: 142 / 142 ✓ | Standard SPs: 180 / 540**
**Sprint 6 Total: 700 hrs** *(ADF complete — 6 sprints faster than Phase 1)*

---

### Sprint 7 — Stored Proc Conversion (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Stored Procs — Standard Batch 2 (180 SPs) | Spark SQL conversion with templates | 252 | Acc 3 + Acc 6 | Data Engineers (2) |
| Stored Procs — Standard Batch 3 (180 SPs, final) | Spark SQL conversion with templates | 252 | Acc 3 + Acc 6 | Data Engineers (2) |
| Stored Procs — Spark Low (25 SPs) | Template-driven PySpark, starter notebooks | 154 | Acc 3 + Acc 6 | Sr Data Engineers (2) |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

> **Accelerator impact:** Pattern catalog provides pre-built templates for ~80% of standard SP patterns. Copilot assists with remaining conversion and testing.

**Cumulative Standard SPs: 540 / 540 ✓ | Spark Low: 25 / 25 ✓**
**Sprint 7 Total: 698 hrs**

---

### Sprint 8 — Complex SP Conversion + Logic Apps & ADLS (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Stored Procs — Spark Medium (25 SPs) | PySpark DataFrames, pattern library | 328 | Acc 3 + Acc 6 | Sr Data Engineers (2), Architect |
| Stored Procs — Spark High Batch 1 (15 SPs) | Full PySpark refactoring, medallion architecture | 317 | Acc 3 + Acc 6 | Sr Data Engineers (2), Architect |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Cumulative Spark Medium: 25 / 25 ✓ | Spark High: 15 / 25**
**Sprint 8 Total: 685 hrs**

---

### Sprint 9 — SP High Completion + Logic Apps & ADLS (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Stored Procs — Spark High Batch 2 (10 SPs, final) | Full PySpark refactoring | 211 | Acc 3 + Acc 6 | Sr Data Engineers (2), Architect |
| Logic Apps (147 apps) | Batch scripted repointing, validation | 235 | Acc 7 | Data Engineers (2) |
| ADLS Accounts (53 accounts) | OneLake shortcuts, scripted migration | 148 | Acc 7 | Data Engineer, DBA |
| Dev hardening | Integration testing, performance baseline | 60 | — | QA Lead, Data Engineers |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

> **Accelerator impact:** PowerShell batch scripts handle ~75% of Logic App repointing automatically. OneLake shortcut framework eliminates physical data copy for ~60% of ADLS accounts.

**All Dev Migration Complete ✓**
**Sprint 9 Total: 694 hrs**

---

### Sprint 10 — SIT Cycle 1 (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Automated SIT deployment | CI/CD pipeline-driven full deployment to SIT | 60 | Acc 4 | Sr Data Engineer |
| Automated schema & data validation | Validation framework: row counts, checksums, schema comparison for 1,538 tables | 200 | Acc 5 | QA Lead, Data Engineers |
| Pipeline execution testing | Automated pipeline test runs with assertion checks | 180 | Acc 4 + Acc 5 | Data Engineers, Sr Data Engineers |
| SP functional testing | Execute all SPs, automated output comparison | 120 | Acc 5 | Sr Data Engineers |
| Defect triage & remediation | Fix critical/high defects | 100 | Acc 6 | All Engineers |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

> **Accelerator impact:** Automated validation framework catches ~80% of data issues in first SIT cycle vs. ~50% with manual validation. CI/CD automation eliminates manual deployment effort.

**Sprint 10 Total: 700 hrs** *(SIT hours consumed: 700 / 1,785)*

---

### Sprint 11 — SIT Cycle 2 (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Logic App & ADLS validation | End-to-end flow validation, shortcut integrity | 100 | Acc 5 | Data Engineers |
| Performance testing | Automated benchmark suite, capacity stress testing | 180 | Acc 5 | DBA, Architect |
| Regression testing (Cycle 1 fixes) | Automated re-validation of all fixes | 120 | Acc 5 | QA Lead, Data Engineers |
| Security & access testing | Role-based access, Entra ID, RLS | 80 | — | DBA |
| Defect triage & remediation | Fix remaining SIT defects | 100 | Acc 6 | All Engineers |
| SIT exit preparation | Test summary, defect analysis | 60 | — | QA Lead, PM |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Sprint 11 Total: 680 hrs** *(SIT hours consumed: 1,380 / 1,785)*

---

### Sprint 12 — SIT Closeout + UAT Prep (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| SIT final regression & sign-off | Full regression, SIT exit criteria validation | 280 | Acc 5 | All Engineers, QA Lead |
| SIT remediation (remaining) | Final defect fixes | 125 | Acc 6 | All Engineers |
| UAT environment deployment | Automated CI/CD promotion to UAT | 60 | Acc 4 | Sr Data Engineer |
| UAT preparation | Test scripts, business user onboarding, UAT kickoff | 100 | — | PM, QA Lead |
| UAT Cycle 1 start | Initial business user testing | 100 | — | PM, Data Engineers |
| PM governance | Sprint ceremonies, status reporting | 35 | — | PM |

**SIT Complete: 1,785 ✓**
**Sprint 12 Total: 700 hrs**

---

### Sprint 13 — UAT (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| UAT business scenario testing | Full business process walkthroughs, edge cases | 250 | — | PM, QA Lead, Data Engineers |
| UAT defect remediation | Fix UAT defects, re-test | 180 | Acc 6 | All Engineers |
| Performance acceptance testing | Business-critical query performance | 80 | Acc 5 | DBA, Architect |
| Production readiness planning | Go/no-go checklist, rollback plan, cutover runbook | 80 | Acc 4 | Architect, PM |
| UAT progress tracking | Stakeholder updates, defect dashboards | 40 | — | PM |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**Sprint 13 Total: 670 hrs** *(UAT hours consumed: 650 / 952)*

---

### Sprint 14 — UAT Closeout + Pre-Production (700 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| UAT final remediation & sign-off | Remaining defects, formal UAT acceptance | 200 | Acc 6 | All Engineers, QA Lead |
| Production dry-run | Automated deployment rehearsal via CI/CD pipeline | 120 | Acc 4 | Sr Data Engineers, DBA |
| Cutover runbook finalization | Step-by-step instructions, rollback triggers | 60 | Acc 4 | Architect, PM |
| Monitoring & alerting setup | Capacity monitoring, pipeline alerting, SLA dashboards | 80 | Acc 4 | Sr Data Engineer, DBA |
| Prod environment validation | Connection health, data freshness, security | 60 | Acc 5 | DBA |
| Stakeholder communication | Go-live readiness confirmation | 30 | — | PM |
| PM governance | Sprint ceremonies, status reporting | 40 | — | PM |

**UAT Complete: 952 ✓**
**Sprint 14 Total: 590 hrs**

---

### Sprint 15 — Production Cutover (303 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Automated production deployment | CI/CD pipeline execution for full Prod deployment | 60 | Acc 4 | Sr Data Engineers, DBA |
| Connection rerouting | Automated reroute of upstream/downstream connections | 43 | Acc 4 | Data Engineers, DBA |
| Post-deployment validation | Automated smoke tests, critical path verification | 60 | Acc 5 | QA Lead, All Engineers |
| Go-live monitoring | Real-time monitoring for first 48 hours | 80 | Acc 4 | All Engineers |
| PM governance | Go-live communication, escalation management | 60 | — | PM |

**Prod Cutover Complete: 303 ✓**
**Sprint 15 Total: 303 hrs**

---

### Sprint 16 — Hypercare & Closeout (487 hrs)

| Task | Subtasks | Hours | Accelerator | Owner(s) |
|---|---|---|---|---|
| Hypercare support (2 weeks) | Production issue triage, hotfixes, tuning | 180 | Acc 6 | All Engineers |
| Knowledge transfer | Operational runbooks, client team training | 100 | — | Architect, Sr Data Engineers |
| Synapse decommissioning plan | Shutdown planning, data retention verification | 50 | — | Architect, DBA |
| Accelerator retrospective | Document accelerator effectiveness, update pattern library | 60 | — | Sr Data Engineers, Architect |
| Project closeout | Lessons learned, final report, accelerator feedback | 60 | — | PM, Architect |
| PM governance | Final ceremonies, closeout | 37 | — | PM |

**Sprint 16 Total: 487 hrs**

---

### Phase 2 Summary

| Sprint | Focus | Hours | Cumulative |
|---|---|---|---|
| 0 | Discovery + Accelerator Setup | 700 | 700 |
| 1 | Foundation + CI/CD Automation | 671 | 1,371 |
| 2 | Synapse DW Batch 1 | 700 | 2,071 |
| 3 | Synapse DW Batch 2 + Views Complete | 700 | 2,771 |
| 4 | Synapse DW Batch 3 + ADF Start | 700 | 3,471 |
| 5 | Synapse DW Complete + ADF | 700 | 4,171 |
| 6 | ADF Complete + SP Start | 700 | 4,871 |
| 7 | SP Standard + Spark Low Complete | 698 | 5,569 |
| 8 | SP Medium + High Start | 685 | 6,254 |
| 9 | SP High Complete + Logic Apps + ADLS Complete | 694 | 6,948 |
| 10 | SIT Cycle 1 | 700 | 7,648 |
| 11 | SIT Cycle 2 | 680 | 8,328 |
| 12 | SIT Closeout + UAT Start | 700 | 9,028 |
| 13 | UAT | 670 | 9,698 |
| 14 | UAT Closeout + Pre-Production | 590 | 10,288 |
| 15 | Production Cutover | 303 | 10,591 |
| 16 | Hypercare & Closeout | 487 | 11,078 |
| | **Phase 2 Total** | | **~11,078 hrs** |

---

# Phase 1 vs. Phase 2 — Comparison Summary

| Metric | Phase 1 (Base) | Phase 2 (Accelerated) | Delta |
|---|---|---|---|
| **Total Sprints** | 25 | 16 | **9 fewer (36%)** |
| **Calendar Duration** | ~50 weeks | ~32 weeks | **18 weeks faster** |
| **Total Hours** | ~17,329 | ~11,078 | **~6,251 hrs saved** |
| **Dev Hours** | 11,902 | ~7,016 | **~4,886 hrs saved (41%)** |
| **SIT Hours** | 2,380 | 1,785 | **595 hrs saved (25%)** |
| **UAT Hours** | 1,190 | 952 | **238 hrs saved (20%)** |
| **Prod Hours** | 357 | 303 | **54 hrs saved (15%)** |
| **Overhead Hours** | 1,600 | 1,099 | **501 hrs saved (31%)** |

### Workstream Completion Milestones

| Workstream | Phase 1 Complete | Phase 2 Complete | Sprints Saved |
|---|---|---|---|
| Synapse Tables (1,538) | Sprint 10 | Sprint 5 | 5 |
| Synapse Views (362) | Sprint 9 | Sprint 3 | 6 |
| ADF Pipelines (609) | Sprint 13 | Sprint 6 | 7 |
| ADF Datasets (450) | Sprint 12 | Sprint 6 | 6 |
| ADF Triggers (142) | Sprint 12 | Sprint 6 | 6 |
| Stored Procs — All (615) | Sprint 15 | Sprint 9 | 6 |
| Logic Apps (147) | Sprint 15 | Sprint 9 | 6 |
| ADLS Accounts (53) | Sprint 15 | Sprint 9 | 6 |
| SIT Complete | Sprint 20 | Sprint 12 | 8 |
| UAT Complete | Sprint 22 | Sprint 14 | 8 |
| Production Go-Live | Sprint 24 | Sprint 15 | 9 |

### Cost Impact (at blended $175/hr)

| | Phase 1 | Phase 2 | Savings |
|---|---|---|---|
| **Total Cost** | ~$3,033K | ~$1,939K | **~$1,094K (36%)** |

> Blended rate is illustrative. Actual rates vary by role and engagement structure.

---

# Risk Considerations & Dependencies

### Technical Risks

| Risk | Impact | Mitigation | Phase Affected |
|---|---|---|---|
| T-SQL incompatibilities exceed estimates | SP conversion overruns | Pre-migration DACPAC analysis + Copilot-assisted resolution | Both |
| Fabric capacity constraints during peak migration | Slower data copy throughput | Right-size F-SKU capacity; schedule large table copies during off-hours | Both |
| ADF pipelines with unsupported activities | Manual rebuild required for "Not Compatible" pipelines | Assessment tool categorization in Sprint 0; allocate buffer | Both |
| Complex SP conversion patterns not in template library | Higher-than-expected effort on Spark High SPs | Iterative template library enrichment; senior engineer focus | Phase 2 |
| OneLake shortcut limitations for ADLS | Physical data copy required instead of shortcuts | Decision framework evaluation per account in Sprint 0 | Phase 2 |

### Organizational Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Client stakeholder availability for UAT | UAT cycle delays | Early UAT planning, scheduled business user commitments |
| Team ramp-up on Fabric platform | Lower productivity in early sprints | Sprint 0 KT + accelerator training; senior-led pair programming |
| Scope creep (additional objects discovered) | Timeline extension | Strict change control; re-baseline at Sprint 0 exit |
| Accelerator build not complete before engagement start | Phase 2 savings not achievable | Pre-engagement accelerator readiness checkpoint; fallback to Phase 1 timeline |

### Dependencies

| Dependency | Required By | Owner |
|---|---|---|
| Microsoft Fabric capacity provisioned | Sprint 1 | Client / Microsoft |
| Azure Synapse source access (read-only) | Sprint 0 | Client IT |
| Entra ID groups and service principals configured | Sprint 1 | Client IT / Security |
| VNet Data Gateway deployed | Sprint 1 | Client IT / Networking |
| ADF source environment access | Sprint 0 (assessment) | Client IT |
| ADLS storage account access | Sprint 9 (Phase 2) / Sprint 14 (Phase 1) | Client IT |
| Business SMEs for UAT | Sprint 13 (Phase 2) / Sprint 20 (Phase 1) | Client Business |
| Accelerator assets built and validated | Sprint 0 (Phase 2 only) | DMTSP Accelerator Team |

---

*This sprint plan is based on the object counts, complexity distributions, and accelerator productivity estimates documented in the [Fabric Migration Accelerators — DMTSP Buildout Recommendation](Fabric_Migration_Accelerators_DMTSP_Buildout.md). Actual sprint durations will vary based on environment complexity, team proficiency, and client readiness. Re-baseline at Sprint 0 exit gate.*
