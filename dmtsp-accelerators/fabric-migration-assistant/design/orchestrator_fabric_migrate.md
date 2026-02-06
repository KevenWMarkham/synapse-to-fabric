# Fabric Migration Assistant — Reusable Sprint Orchestrator

**Version:** 1.0
**Author:** Keven Markham, VP Enterprise Transformation — DMTSP
**Date:** February 6, 2026
**Execution Model:** Phase 2 (Accelerated Delivery)
**Reusability:** Global — this orchestrator is a reusable execution template deployed at every Synapse-to-Fabric engagement. Team allocations and batch sizes scale per client.
**Related Documents:**
- [Roadmap](../roadmap.md) — Strategic phases, prerequisites, risk register
- [Backlog](../backlog.md) — Epics, stories, acceptance criteria
- [Sprint Plan (root)](../../../Sprint_Plan_Synapse_to_Fabric.md) — Full Phase 1/Phase 2 sprint plan
- [Accelerator Buildout (root)](../../../Fabric_Migration_Accelerators_DMTSP_Buildout.md) — All 7 accelerator descriptions

---

## Team Allocation Matrix

**Sprint Cadence:** 2-week sprints | **Team Capacity:** 700 hrs/sprint | **10 FTEs**

| Role | Sprint 0 | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | Sprint 15 |
|---|---|---|---|---|---|---|---|
| PM (1×70) | 40 | 40 | 40 | 40 | 40 | 40 | 60 |
| Architect (1×70) | 50 | 20 | — | — | — | — | — |
| Sr Data Engineer ×2 (140) | 80 | 50 | 60 | 60 | — | — | — |
| Data Engineer ×4 (280) | — | — | 260 | 260 | 240 | 260 | 10 |
| QA Lead (1×70) | — | 30 | 30 | 30 | 20 | 30 | 5 |
| DBA (1×70) | 30 | 60 | 30 | 30 | 20 | 30 | 5 |
| **Acc 1 Subtotal** | **200** | **200** | **420** | **420** | **320** | **360** | **80** |

> Remaining capacity per sprint allocated to other accelerators (Acc 2–7) and cross-cutting work. Sprint 4–5 show reduced Acc 1 capacity as Acc 2 ADF work begins.

---

## Sprint Timeline

```
Sprint 0 ──── Sprint 1 ──── Sprint 2 ──── Sprint 3 ──── Sprint 4 ──── Sprint 5 ──── ... ──── Sprint 15
Discovery     Foundation    Batch 1       Batch 2       Batch 3       Batch 4               Reroute
& Setup       & Schema      380 tbl       380 tbl       380 tbl       398 tbl               Connections
              60 objects    180 views     182 views     + ADF Start   + ADF Continue
                                          VIEWS ✓                     TABLES ✓              REROUTE ✓

Week 1-2      Week 3-4      Week 5-6      Week 7-8      Week 9-10     Week 11-12            Week 31-32
700 hrs       671 hrs       700 hrs       700 hrs       700 hrs       700 hrs               303 hrs
```

---

## Sprint 0 — Discovery & Accelerator Setup

**Duration:** 2 weeks | **Total Sprint Hours:** 700 | **Acc 1 Share:** ~200 hrs
**Backlog Epic:** [E0](../backlog.md#epic-e0-discovery--setup)

### Entry Criteria

- [ ] Synapse SQL pool read-only access granted
- [ ] Fabric workspace provisioned with F2/P1 capacity
- [ ] VS 2022 + SSDT installed on engineer workstations
- [ ] Team onboarded and sprint ceremonies scheduled

### Exit Criteria

- [ ] DACPAC extracted and verified (1,960 objects)
- [ ] Migration Assistant assessment report reviewed
- [ ] Copilot enabled and prompt library initialized
- [ ] 4 table batches + 2 view batches defined and documented

### Tasks

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S0-T1 | Connect to Synapse | Configure VS 2022 SSDT connection to source SQL pool | 2 | Sr DE | E0-S1.T1 |
| S0-T2 | Extract DACPAC (VS 2022) | Right-click → Extract Data-tier Application | 4 | Sr DE | E0-S1.T2 |
| S0-T3 | Verify DACPAC | Confirm 1,960 objects: 1,538 tbl + 362 view + 4 func + 16 schema + 40 security | 4 | Sr DE | E0-S1.T3 |
| S0-T4 | Extract DACPAC (CLI backup) | Run SqlPackage /Action:Extract as documented fallback | 4 | Sr DE | E0-S1.T4 |
| S0-T5 | Upload to Migration Assistant | Upload DACPAC; trigger assessment scan | 4 | Sr DE | E0-S2.T1 |
| S0-T6 | Review assessment report | Object inventory, incompatibility flags, primary/dependent triage | 28 | Sr DE, DBA | E0-S2.T2–T4 |
| S0-T7 | Configure Copilot | Verify F2/P1, enable admin settings, test fix suggestions | 14 | Architect, Sr DE | E0-S3.T1–T3 |
| S0-T8 | Initialize prompt library | Create 10+ migration fix prompts; document in runbook | 16 | Sr DE | E0-S3.T4–T5 |
| S0-T9 | Define batch groupings | Analyze dependencies; define 4 tbl batches + 2 view batches | 30 | Architect, DBA | E0-S4.T1–T5 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M0.1 | DACPAC Extracted | .dacpac file with 1,960 objects verified | Day 3 |
| M0.2 | Assessment Complete | Migration Assistant report reviewed and triaged | Day 6 |
| M0.3 | Copilot Operational | Fix suggestions tested on sample objects | Day 8 |
| M0.4 | Batch Plan Approved | 4 table + 2 view batches documented and signed off | Day 10 |

### Blockers to Escalate

- Synapse access not granted → Escalate to client IT (blocks all work)
- F2/P1 capacity not available → Escalate to Microsoft account team (blocks Copilot)
- DACPAC extraction failure → Fall back to SqlPackage CLI; if both fail, engage Microsoft Support

---

## Sprint 1 — Foundation + Schema/Security/Functions

**Duration:** 2 weeks | **Total Sprint Hours:** 671 | **Acc 1 Share:** ~91 hrs
**Backlog Epic:** [E1](../backlog.md#epic-e1-schema--foundation)

### Entry Criteria

- [ ] Sprint 0 milestones M0.1–M0.4 achieved
- [ ] Fabric workspace networking configured (VNet, private endpoints)
- [ ] Entra ID service principals and security groups ready

### Exit Criteria

- [ ] Fabric Data Warehouse created with SQL analytics endpoint
- [ ] 16 schemas deployed and verified
- [ ] 40 security objects migrated (including Entra ID mapping)
- [ ] 4 functions deployed and tested
- [ ] All 60 foundation objects confirmed in target DW

### Tasks

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S1-T1 | Create Fabric DW | Create warehouse in target workspace | 4 | DBA | E1-S1.T1 |
| S1-T2 | Configure DW settings | Collation, defaults, SQL analytics endpoint | 3 | DBA | E1-S1.T2 |
| S1-T3 | Verify endpoint connectivity | Test SQL analytics endpoint from dev tools | 3 | DBA | E1-S1.T3 |
| S1-T4 | Deploy schemas (16) | Run Migration Assistant schema deployment | 2 | DBA | E1-S2.T1 |
| S1-T5 | Verify schemas | Confirm 16 schema names match source | 1 | DBA | E1-S2.T2 |
| S1-T6 | Deploy automated security | DACPAC-driven roles, permissions, DDM | 4 | DBA | E1-S3.T1 |
| S1-T7 | Map SQL auth → Entra ID | Manual user mapping for SQL-authenticated accounts | 16 | DBA | E1-S3.T2 |
| S1-T8 | Configure RLS policies | Row-level security policy migration | 10 | DBA | E1-S3.T3 |
| S1-T9 | Verify permissions | Compare GRANT/REVOKE/DENY against source | 6 | DBA | E1-S3.T4 |
| S1-T10 | Security audit | Full security comparison and sign-off | 4 | DBA, Architect | E1-S3.T5 |
| S1-T11 | Deploy functions (4) | Migration Assistant function deployment | 1 | DBA | E1-S4.T1 |
| S1-T12 | Test functions | Execute each function; verify output matches source | 1 | DBA | E1-S4.T2 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M1.1 | Fabric DW Created | Warehouse accessible via SQL analytics endpoint | Day 2 |
| M1.2 | Schemas Deployed | 16/16 schemas confirmed | Day 3 |
| M1.3 | Functions Deployed | 4/4 functions tested and passing | Day 4 |
| M1.4 | Security Complete | 40/40 security objects migrated; Entra ID mapping done | Day 8 |
| M1.5 | Foundation Sign-Off | All 60 foundation objects verified | Day 10 |

---

## Sprint 2 — Table Batch 1 + View Batch 1

**Duration:** 2 weeks | **Total Sprint Hours:** 700 | **Acc 1 Share:** ~782 hrs (tables 646 + views 136)
**Backlog Stories:** [E2-S1](../backlog.md#e2-s1-table-batch-1-380-tables), [E3-S1](../backlog.md#e3-s1-view-batch-1-180-views)

> Note: Sprint 2 is the heaviest Acc 1 sprint. Full team allocation plus carryover capacity from Sprint 1 under-burn (671 vs. 700).

### Entry Criteria

- [ ] M1.5 Foundation Sign-Off achieved
- [ ] Validation framework (Acc 5) deployed and tested
- [ ] Batch 1 table list and view list confirmed

### Exit Criteria

- [ ] 380 tables migrated (DDL + data) with validation pass
- [ ] 180 views migrated with dependency resolution confirmed
- [ ] Fix patterns documented and prompt library updated
- [ ] Row count and checksum validation 100% pass

### Tasks — Tables (Batch 1: 380 tables)

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S2-T1 | Upload Batch 1 DACPAC | Load 380-table segment to Migration Assistant | 4 | Sr DE | E2-S1.T1 |
| S2-T2 | Review translated DDL | Verify auto-translated DDL for all 380 tables | 30 | DE (4) | E2-S1.T2 |
| S2-T3 | Fix incompatibilities | Copilot-assisted resolution; primary objects first | 60 | Sr DE, DBA | E2-S1.T3 |
| S2-T4 | Deploy table DDL | Create tables in target Fabric DW | 20 | DE (4) | E2-S1.T4 |
| S2-T5 | Configure copy jobs (standard) | Data Factory copy jobs for tables < 10 GB | 80 | DE (4) | E2-S1.T5 |
| S2-T6 | Configure copy jobs (large) | Partitioned Copy Activity for tables > 10 GB | 40 | Sr DE | E2-S1.T6 |
| S2-T7 | Execute data copy | Run all copy jobs; monitor throughput | 120 | DE (4) | E2-S1.T7 |
| S2-T8 | Row count validation | Source vs. target exact match for 380 tables | 60 | DE (4) | E2-S1.T8 |
| S2-T9 | Checksum validation | Hash comparison on key columns | 80 | DE (4), QA | E2-S1.T9 |
| S2-T10 | Sample spot-checks | 0.1% record comparison | 40 | DE (2) | E2-S1.T10 |
| S2-T11 | Update fix pattern catalog | Document new patterns from Batch 1 | 12 | Sr DE | E2-S1.T11 |

### Tasks — Views (Batch 1: 180 views)

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S2-T12 | Upload view definitions | Load 180-view segment to Migration Assistant | 4 | DE | E3-S1.T1 |
| S2-T13 | Review translated view DDL | Verify auto-translated view definitions | 16 | DE | E3-S1.T2 |
| S2-T14 | Fix view incompatibilities | Copilot-assisted resolution for view constructs | 24 | DE, Sr DE | E3-S1.T3 |
| S2-T15 | Deploy view DDL | Create views in target Fabric DW | 12 | DE | E3-S1.T4 |
| S2-T16 | Validate view execution | Run each view query; verify results | 30 | DE | E3-S1.T5 |
| S2-T17 | Verify dependencies | Confirm view-to-table resolution | 20 | DE | E3-S1.T6 |
| S2-T18 | View row count comparison | Compare view results against source | 20 | DE | E3-S1.T7 |
| S2-T19 | Document view fix patterns | Catalog view-specific fix patterns | 10 | DE | E3-S1.T8 |

### Role Assignment Matrix — Sprint 2

| Role | Table Tasks | View Tasks | Other | Total |
|---|---|---|---|---|
| Data Engineer 1 | S2-T2,T4,T5,T7,T8 | — | — | 170 |
| Data Engineer 2 | S2-T2,T4,T5,T7,T8 | — | — | 170 |
| Data Engineer 3 | S2-T2,T4,T5,T7,T9,T10 | — | — | 170 |
| Data Engineer 4 | — | S2-T12 through T19 | — | 136 |
| Sr Data Engineer 1 | S2-T1,T3,T6,T11 | — | — | 58 |
| Sr Data Engineer 2 | S2-T3 | S2-T14 | — | 38 |
| DBA | S2-T3 | — | — | 30 |
| QA Lead | S2-T9 | — | — | 30 |
| PM | — | — | Governance | 40 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M2.1 | DDL Deployed (Tables) | 380 table definitions created in Fabric DW | Day 4 |
| M2.2 | Data Copy Started | All copy jobs running for Batch 1 | Day 5 |
| M2.3 | Data Copy Complete | All 380 tables fully copied | Day 7 |
| M2.4 | Table Validation Pass | Row count + checksum 100% pass | Day 9 |
| M2.5 | Views Deployed | 180 views migrated and validated | Day 10 |

**Cumulative Progress:** Tables: 380 / 1,538 (25%) | Views: 180 / 362 (50%)

---

## Sprint 3 — Table Batch 2 + View Batch 2 (Final)

**Duration:** 2 weeks | **Total Sprint Hours:** 700 | **Acc 1 Share:** ~782 hrs (tables 646 + views 136)
**Backlog Stories:** [E2-S2](../backlog.md#e2-s2-table-batch-2-380-tables), [E3-S2](../backlog.md#e3-s2-view-batch-2-182-views-final)

### Entry Criteria

- [ ] M2.4 Table Validation Pass achieved (Batch 1)
- [ ] M2.5 Views Deployed achieved (View Batch 1)
- [ ] Fix patterns from Sprint 2 incorporated into prompt library

### Exit Criteria

- [ ] 760 cumulative tables migrated with validation pass
- [ ] **362 / 362 views migrated — VIEW MIGRATION COMPLETE**
- [ ] All view dependencies resolved against underlying tables

### Tasks — Tables (Batch 2: 380 tables)

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S3-T1 | Upload Batch 2 DACPAC | Load 380-table segment | 4 | Sr DE | E2-S2.T1 |
| S3-T2 | Review translated DDL | Verify DDL for 380 tables | 25 | DE (4) | E2-S2.T2 |
| S3-T3 | Fix incompatibilities | Apply Batch 1 patterns; resolve new issues | 45 | Sr DE, DBA | E2-S2.T3 |
| S3-T4 | Deploy table DDL | Create tables in target DW | 18 | DE (4) | E2-S2.T4 |
| S3-T5 | Configure + execute copy jobs | Standard + partitioned copy | 180 | DE (4), Sr DE | E2-S2.T5–T7 |
| S3-T6 | Row count validation | Source vs. target for 380 tables | 55 | DE (4) | E2-S2.T8 |
| S3-T7 | Checksum validation | Hash comparison | 70 | DE (4), QA | E2-S2.T9 |
| S3-T8 | Sample spot-checks | 0.1% record comparison | 35 | DE (2) | E2-S2.T10 |
| S3-T9 | Update pattern catalog | New patterns from Batch 2 | 8 | Sr DE | E2-S2.T11 |

> Note: Hours slightly reduced vs. Sprint 2 due to pattern reuse (team learning curve).

### Tasks — Views (Batch 2: 182 views, final)

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S3-T10 | Upload view definitions | Load 182-view segment | 4 | DE | E3-S2.T1 |
| S3-T11 | Review + fix + deploy views | Apply Sprint 2 view patterns | 48 | DE, Sr DE | E3-S2.T2–T4 |
| S3-T12 | Validate views | Query execution + dependency + row count | 60 | DE | E3-S2.T5–T7 |
| S3-T13 | Document final view patterns | Complete view fix catalog | 10 | DE | E3-S2.T8 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M3.1 | Batch 2 DDL Deployed | 380 table definitions created | Day 4 |
| M3.2 | Batch 2 Data Copy Complete | All 380 tables fully copied | Day 7 |
| M3.3 | Batch 2 Validation Pass | Row count + checksum 100% pass | Day 9 |
| M3.4 | **VIEW MIGRATION COMPLETE** | **362 / 362 views migrated and validated** | Day 10 |

**Cumulative Progress:** Tables: 760 / 1,538 (49%) | Views: 362 / 362 (100%)

---

## Sprint 4 — Table Batch 3 + ADF Start

**Duration:** 2 weeks | **Total Sprint Hours:** 700 | **Acc 1 Share:** ~500 hrs
**Backlog Story:** [E2-S3](../backlog.md#e2-s3-table-batch-3-380-tables)

> Reduced Acc 1 capacity: Sr Data Engineers and 1 Data Engineer shift to Acc 2 (ADF PowerShell upgrade).

### Entry Criteria

- [ ] M3.3 Batch 2 Validation Pass achieved
- [ ] ADF assessment tool ready (Acc 2 Sprint 4 work)

### Exit Criteria

- [ ] 1,140 cumulative tables migrated with validation pass
- [ ] Team velocity maintained despite reduced headcount

### Tasks

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S4-T1 | Upload Batch 3 DACPAC | Load 380-table segment | 4 | DE | E2-S3.T1 |
| S4-T2 | Review + fix DDL | Translate, fix (leveraging pattern catalog) | 60 | DE (3), DBA | E2-S3.T2–T3 |
| S4-T3 | Deploy table DDL | Create tables | 16 | DE (3) | E2-S3.T4 |
| S4-T4 | Configure + execute copy | Standard + partitioned copy jobs | 160 | DE (3) | E2-S3.T5–T7 |
| S4-T5 | Full validation suite | Row count + checksum + spot-checks | 120 | DE (3), QA | E2-S3.T8–T10 |
| S4-T6 | Update pattern catalog | Incremental updates | 4 | DE | E2-S3.T11 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M4.1 | Batch 3 DDL Deployed | 380 table definitions created | Day 4 |
| M4.2 | Batch 3 Data Complete | All 380 tables copied | Day 7 |
| M4.3 | Batch 3 Validation Pass | 100% validation pass | Day 10 |

**Cumulative Progress:** Tables: 1,140 / 1,538 (74%) | Views: 362 / 362 (100%)

---

## Sprint 5 — Table Batch 4 (Final) + ADF Continue

**Duration:** 2 weeks | **Total Sprint Hours:** 700 | **Acc 1 Share:** ~500 hrs
**Backlog Story:** [E2-S4](../backlog.md#e2-s4-table-batch-4-398-tables-final)

### Entry Criteria

- [ ] M4.3 Batch 3 Validation Pass achieved

### Exit Criteria

- [ ] **1,538 / 1,538 tables migrated — TABLE MIGRATION COMPLETE**
- [ ] Comprehensive cross-batch validation pass
- [ ] Migration runbook finalized with all patterns documented

### Tasks

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S5-T1 | Upload Batch 4 DACPAC | Load 398-table segment (final) | 4 | DE | E2-S4.T1 |
| S5-T2 | Review + fix DDL | Translate, fix (leveraging full pattern catalog) | 55 | DE (3), DBA | E2-S4.T2–T3 |
| S5-T3 | Deploy table DDL | Create tables | 16 | DE (3) | E2-S4.T4 |
| S5-T4 | Configure + execute copy | Standard + partitioned copy jobs | 160 | DE (3) | E2-S4.T5–T7 |
| S5-T5 | Full validation suite | Row count + checksum + spot-checks | 120 | DE (3), QA | E2-S4.T8–T10 |
| S5-T6 | Cross-batch validation | Verify all 1,538 tables pass row count + checksum | 40 | QA, DBA | E2-S4.T11 |
| S5-T7 | Finalize pattern catalog | Complete migration runbook for reuse | 8 | Sr DE | E2-S4.T11 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M5.1 | Batch 4 DDL Deployed | 398 table definitions created | Day 4 |
| M5.2 | Batch 4 Data Complete | All 398 tables copied | Day 7 |
| M5.3 | Batch 4 Validation Pass | 100% validation pass | Day 9 |
| M5.4 | **TABLE MIGRATION COMPLETE** | **1,538 / 1,538 tables verified** | Day 10 |

**Cumulative Progress:** Tables: 1,538 / 1,538 (100%) | Views: 362 / 362 (100%)

---

## Sprint 15 — Production Cutover (Connection Rerouting)

**Duration:** 2 weeks | **Total Sprint Hours:** 303 | **Acc 1 Share:** ~15 hrs
**Backlog Epic:** [E4](../backlog.md#epic-e4-connection-rerouting)

> Sprint 15 is the production cutover sprint. Acc 1 connection rerouting is a small but critical slice of the overall cutover.

### Entry Criteria

- [ ] Production deployment complete (Acc 4 CI/CD pipeline)
- [ ] All 1,960 objects verified in production Fabric DW
- [ ] Cutover runbook approved

### Exit Criteria

- [ ] All Synapse connections rerouted to Fabric DW
- [ ] Power BI, pipeline, and Logic App downstream validation pass
- [ ] Connection rerouting sign-off

### Tasks

| ID | Task | Subtasks | Hours | Role | Backlog Ref |
|---|---|---|---|---|---|
| S15-T1 | Query connections API | `GET /v1/connections`; filter Synapse endpoints | 2 | DBA | E4-S1.T1 |
| S15-T2 | Catalog connections | Document all Synapse-pointing connections | 2 | DBA | E4-S1.T2 |
| S15-T3 | Create rerouting plan | Map each connection to Fabric DW endpoint | 1 | DBA | E4-S1.T3 |
| S15-T4 | Execute batch PATCH | `PATCH /v1/connections/{id}` for each connection | 3 | DBA | E4-S2.T1 |
| S15-T5 | Validate Power BI | Refresh semantic models; verify data | 2 | DE | E4-S2.T2 |
| S15-T6 | Validate pipelines | Run downstream pipelines; check connections | 2 | DE | E4-S2.T3 |
| S15-T7 | Smoke tests | Critical data path end-to-end verification | 2 | DE, QA | E4-S2.T4 |
| S15-T8 | Sign-off | Document rerouting results; formal sign-off | 1 | DBA | E4-S2.T5 |

### Milestones

| ID | Milestone | Criteria | Sprint Day |
|---|---|---|---|
| M15.1 | Connections Inventoried | All Synapse connections cataloged | Day 1 |
| M15.2 | Rerouting Complete | All PATCH operations successful | Day 2 |
| M15.3 | Downstream Validated | Power BI + pipelines + Logic Apps confirmed | Day 3 |

---

## Cross-Sprint Metrics

### Object Progress Tracker

| Object Type | Count | Sprint 0 | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | Sprint 15 |
|---|---|---|---|---|---|---|---|---|
| Schemas | 16 | — | 16 ✓ | — | — | — | — | — |
| Security | 40 | — | 40 ✓ | — | — | — | — | — |
| Functions | 4 | — | 4 ✓ | — | — | — | — | — |
| Tables | 1,538 | — | — | 380 | 760 | 1,140 | **1,538** ✓ | — |
| Views | 362 | — | — | 180 | **362** ✓ | — | — | — |
| Connections | — | — | — | — | — | — | — | ✓ |
| **Cumulative** | **1,960** | **0** | **60** | **620** | **1,182** | **1,200** | **1,960** | **Done** |

### Cumulative Hours Burn (Acc 1 Scope)

| Sprint | Sprint Hours | Cumulative | % of 3,544 Budget |
|---|---|---|---|
| 0 | 200 | 200 | 6% |
| 1 | 91 | 291 | 8% |
| 2 | 782 | 1,073 | 30% |
| 3 | 782 | 1,855 | 52% |
| 4 | 500 | 2,355 | 66% |
| 5 | 500 | 2,855 | 81% |
| 15 | 15 | 2,870 | 81% |

> Remaining ~674 hrs (19%) are PM governance, architecture guidance, and cross-accelerator coordination distributed across all sprints.

### Milestone Summary

| ID | Milestone | Sprint | Day | Status |
|---|---|---|---|---|
| M0.1 | DACPAC Extracted | 0 | 3 | |
| M0.2 | Assessment Complete | 0 | 6 | |
| M0.3 | Copilot Operational | 0 | 8 | |
| M0.4 | Batch Plan Approved | 0 | 10 | |
| M1.1 | Fabric DW Created | 1 | 2 | |
| M1.2 | Schemas Deployed (16) | 1 | 3 | |
| M1.3 | Functions Deployed (4) | 1 | 4 | |
| M1.4 | Security Complete (40) | 1 | 8 | |
| M1.5 | Foundation Sign-Off (60 objects) | 1 | 10 | |
| M2.1 | Batch 1 DDL Deployed | 2 | 4 | |
| M2.2 | Batch 1 Copy Started | 2 | 5 | |
| M2.3 | Batch 1 Copy Complete | 2 | 7 | |
| M2.4 | Batch 1 Validation Pass | 2 | 9 | |
| M2.5 | View Batch 1 Deployed (180) | 2 | 10 | |
| M3.1 | Batch 2 DDL Deployed | 3 | 4 | |
| M3.2 | Batch 2 Copy Complete | 3 | 7 | |
| M3.3 | Batch 2 Validation Pass | 3 | 9 | |
| M3.4 | **VIEW MIGRATION COMPLETE (362)** | 3 | 10 | |
| M4.1 | Batch 3 DDL Deployed | 4 | 4 | |
| M4.2 | Batch 3 Copy Complete | 4 | 7 | |
| M4.3 | Batch 3 Validation Pass | 4 | 10 | |
| M5.1 | Batch 4 DDL Deployed | 5 | 4 | |
| M5.2 | Batch 4 Copy Complete | 5 | 7 | |
| M5.3 | Batch 4 Validation Pass | 5 | 9 | |
| M5.4 | **TABLE MIGRATION COMPLETE (1,538)** | 5 | 10 | |
| M15.1 | Connections Inventoried | 15 | 1 | |
| M15.2 | Rerouting Complete | 15 | 2 | |
| M15.3 | Downstream Validated | 15 | 3 | |

---

## Appendix A: Data Type Mapping Quick Reference

| Synapse Type | Fabric Type | Action |
|---|---|---|
| `money` | `decimal(19,4)` | Auto-mapped |
| `smallmoney` | `decimal(10,4)` | Auto-mapped |
| `datetime` | `datetime2(3)` | Auto-mapped |
| `smalldatetime` | `datetime2(0)` | Auto-mapped |
| `datetimeoffset` | `datetime2` + offset col | Manual split |
| `nchar(n)` / `nvarchar(n)` | `char(n)` / `varchar(n)` | Auto-mapped |
| `ntext` / `text` | `varchar(max)` | Auto-mapped |
| `image` | `varbinary(max)` | Auto-mapped |
| `geometry` / `geography` | Not supported | WKT string workaround |
| `hierarchyid` | Not supported | Flatten to string |
| `sql_variant` | Not supported | Typed decomposition |
| `xml` | `varchar(max)` | String storage |
| `uniqueidentifier` | `varchar(36)` | String representation |

---

## Appendix B: Copilot Prompt Templates

### Fix Distribution Hint

```
This table DDL contains DISTRIBUTION = HASH(column_name) which is not
supported in Fabric Data Warehouse. Remove the distribution hint entirely
and keep the rest of the CREATE TABLE statement unchanged. Fabric handles
distribution automatically.
```

### Fix Clustered Columnstore Index

```
This CREATE TABLE references a CLUSTERED COLUMNSTORE INDEX which uses
Synapse-specific syntax. Convert to a standard CREATE TABLE without the
explicit index specification. Fabric DW uses columnstore by default.
```

### Fix IDENTITY Column

```
This table uses IDENTITY(1,1) which has limited support in Fabric.
Replace with a computed column using surrogate_key() or create a
separate sequence object. Preserve the column name and data type.
```

### Fix Materialized View

```
This CREATE MATERIALIZED VIEW is not supported in Fabric. Convert to
a standard CREATE VIEW. If performance is critical, add a note to
evaluate caching strategies post-migration.
```

### Fix External Table

```
This references an EXTERNAL TABLE pointing to ADLS storage. Replace
with a OneLake shortcut reference or convert to a standard table with
data copied via Data Factory. Document the original external source path.
```

---

## Appendix C: Per-Table Validation Checklist

For each table in every batch, validate:

- [ ] **Schema match** — Column names, data types, nullability match source
- [ ] **Row count** — Exact match between source and target
- [ ] **Checksum** — Hash of key columns matches (HASHBYTES equivalent)
- [ ] **Null patterns** — NULL count per nullable column matches source
- [ ] **Min/Max values** — Boundary values match for numeric and date columns
- [ ] **Sample records** — Random 0.1% sample matches source (100% for tables < 100 rows)
- [ ] **Constraints** — Primary keys, unique constraints in place
- [ ] **Indexes** — Required indexes created (Fabric may optimize differently)

---

## Appendix D: Escalation Procedures

| Issue | First Response | Escalation Path | SLA |
|---|---|---|---|
| DACPAC extraction failure | Try SqlPackage CLI | Microsoft Support | 4 hrs |
| Migration Assistant timeout/crash | Retry; reduce batch size | Microsoft Support | 4 hrs |
| Copilot unavailable | Use manual fix patterns | Microsoft account team | 8 hrs |
| Data copy failure (capacity) | Reduce parallelism; retry | Architect → capacity resize | 2 hrs |
| Row count mismatch | Re-run copy for affected tables | Sr DE investigation | 4 hrs |
| Checksum mismatch | Sample record comparison | DBA deep-dive | 8 hrs |
| Security gap discovered | Immediate manual fix | DBA + Architect | 2 hrs |
| Connection rerouting failure | Manual connection update | DBA → Microsoft Support | 2 hrs |

---

*This orchestrator aligns exactly with Phase 2 sprint data from the [Sprint Plan](../../../Sprint_Plan_Synapse_to_Fabric.md). All task IDs cross-reference the [Backlog](../backlog.md) using the pattern E{epic}-S{story}.T{task}. Sprint hours map to PHASE2_SPRINTS in [sprint-data.js](../../../dmtsp-accelerators/sprint-data.js).*
