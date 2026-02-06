# Fabric Migration Assistant — Reusable Product Backlog

**Version:** 1.0
**Author:** Keven Markham, VP Enterprise Transformation — DMTSP
**Date:** February 6, 2026
**Reusability:** Global — this backlog is a reusable template deployed at every Synapse-to-Fabric engagement. Object counts and batch sizes are adjusted per client.
**Related Documents:**
- [Roadmap](roadmap.md) — Strategic phases and rationale
- [Orchestrator](design/orchestrator_fabric_migrate.md) — Sprint-by-sprint execution plan
- [Sprint Plan (root)](../../Sprint_Plan_Synapse_to_Fabric.md) — Full Phase 1/Phase 2 sprint plan

---

## Backlog Overview

| Metric | Value |
|---|---|
| Epics | 5 (E0–E4) |
| Stories | 16 |
| Total Scope | 1,960 objects |
| Total Accelerated Hours | ~3,544 |
| Sprint Range | 0–5, 15 |

### Priority Legend

| Priority | Meaning |
|---|---|
| **P0** | Blocker — must complete before any downstream work |
| **P1** | Critical — on the sprint critical path |
| **P2** | Important — needed for sprint completion |
| **P3** | Nice-to-have — can slip to next sprint if needed |

### Effort Scale

| Size | Hours | Example |
|---|---|---|
| XS | 1–10 | Single config change |
| S | 11–40 | Foundation object migration |
| M | 41–150 | View batch migration |
| L | 151–400 | Table batch migration |
| XL | 401–700 | Full sprint table + view batch |
| XXL | 700+ | Multi-sprint workstream |

---

## Dependency Graph

```
E0: Discovery & Setup (Sprint 0)
  │
  └──► E1: Schema & Foundation (Sprint 1)
         │
         ├──► E2: Table Migration (Sprints 2–5)
         │       │
         │       └──► E4: Connection Rerouting (Sprint 15)
         │
         └──► E3: View Migration (Sprints 2–3)
                 │
                 └──► E4: Connection Rerouting (Sprint 15)
```

---

## Epic E0: Discovery & Setup

**Sprint:** 0 | **Total Hours:** ~120 | **Roadmap:** [Phase 0](roadmap.md#4-phase-0-discovery--accelerator-setup)

### E0-S1: DACPAC Extraction

| Field | Value |
|---|---|
| **Priority** | P0 |
| **Effort** | S (20 hrs) |
| **Sprint** | 0 |
| **Owner** | Sr Data Engineer |
| **Depends On** | Synapse read-only access |
| **Acceptance Criteria** | DACPAC extracted containing all 1,960 objects; verified via object count comparison against source |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E0-S1.T1 | Connect to Synapse SQL pool via VS 2022 SSDT | 2 | Sr Data Engineer |
| E0-S1.T2 | Extract DACPAC (primary method: VS 2022) | 4 | Sr Data Engineer |
| E0-S1.T3 | Verify DACPAC object count (1,960 objects) | 4 | Sr Data Engineer |
| E0-S1.T4 | Extract DACPAC via SqlPackage CLI (backup method) | 4 | Sr Data Engineer |
| E0-S1.T5 | Document extraction procedure in runbook | 6 | Sr Data Engineer |

### E0-S2: Source Assessment

| Field | Value |
|---|---|
| **Priority** | P0 |
| **Effort** | M (40 hrs) |
| **Sprint** | 0 |
| **Owner** | Sr Data Engineer, DBA |
| **Depends On** | E0-S1 (DACPAC available) |
| **Acceptance Criteria** | Migration Assistant assessment complete; incompatibility report reviewed; primary vs. dependent failures triaged |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E0-S2.T1 | Upload DACPAC to Fabric Migration Assistant | 4 | Sr Data Engineer |
| E0-S2.T2 | Review object inventory and migration status | 8 | Sr Data Engineer, DBA |
| E0-S2.T3 | Analyze incompatibility report | 12 | DBA |
| E0-S2.T4 | Triage primary vs. dependent failures | 8 | DBA, Sr Data Engineer |
| E0-S2.T5 | Document assessment findings | 8 | Sr Data Engineer |

### E0-S3: Copilot Configuration

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | S (30 hrs) |
| **Sprint** | 0 |
| **Owner** | Sr Data Engineer, Architect |
| **Depends On** | Fabric F2/P1 capacity provisioned |
| **Acceptance Criteria** | Copilot enabled and tested; prompt library initialized with 10+ migration fix prompts |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E0-S3.T1 | Verify F2/P1 capacity assignment | 2 | Architect |
| E0-S3.T2 | Enable Copilot in Fabric admin settings | 4 | Architect |
| E0-S3.T3 | Test Copilot fix suggestions against sample failed objects | 8 | Sr Data Engineer |
| E0-S3.T4 | Initialize prompt library with pre-built fix patterns | 12 | Sr Data Engineer |
| E0-S3.T5 | Document Copilot configuration and prompt catalog | 4 | Sr Data Engineer |

### E0-S4: Batch Groupings

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | S (30 hrs) |
| **Sprint** | 0 |
| **Owner** | Architect, DBA |
| **Depends On** | E0-S2 (assessment complete) |
| **Acceptance Criteria** | 4 table batches and 2 view batches defined; dependency ordering confirmed; batch assignments documented |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E0-S4.T1 | Analyze table dependencies and clustering | 10 | DBA, Architect |
| E0-S4.T2 | Define 4 table batches (~380 each) | 6 | Architect |
| E0-S4.T3 | Define 2 view batches (~180 each) | 4 | Architect |
| E0-S4.T4 | Validate dependency ordering across batches | 6 | DBA |
| E0-S4.T5 | Document batch assignments and migration sequence | 4 | Architect |

---

## Epic E1: Schema & Foundation

**Sprint:** 1 | **Total Hours:** ~91 | **Roadmap:** [Phase 1 — Section 5.1](roadmap.md#51-fabric-data-warehouse-creation-sprint-1)

### E1-S1: Fabric DW Creation

| Field | Value |
|---|---|
| **Priority** | P0 |
| **Effort** | XS (10 hrs) |
| **Sprint** | 1 |
| **Owner** | DBA |
| **Depends On** | E0 complete; Fabric workspace provisioned |
| **Acceptance Criteria** | Target Fabric Data Warehouse created; SQL analytics endpoint accessible |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E1-S1.T1 | Create Fabric Data Warehouse in target workspace | 4 | DBA |
| E1-S1.T2 | Configure warehouse settings (collation, defaults) | 3 | DBA |
| E1-S1.T3 | Verify SQL analytics endpoint connectivity | 3 | DBA |

### E1-S2: Schema Migration

| Field | Value |
|---|---|
| **Priority** | P0 |
| **Effort** | XS (3 hrs) |
| **Sprint** | 1 |
| **Owner** | DBA |
| **Depends On** | E1-S1 (Fabric DW created) |
| **Acceptance Criteria** | All 16 schemas created in target DW; names match source |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E1-S2.T1 | Deploy 16 schemas via Migration Assistant | 2 | DBA |
| E1-S2.T2 | Verify schema names and properties | 1 | DBA |

### E1-S3: Security Migration

| Field | Value |
|---|---|
| **Priority** | P0 |
| **Effort** | S (40 hrs) |
| **Sprint** | 1 |
| **Owner** | DBA |
| **Depends On** | E1-S2 (schemas deployed); Entra ID groups configured |
| **Acceptance Criteria** | All 40 security objects migrated; SQL auth users mapped to Entra ID; permissions verified |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E1-S3.T1 | Deploy automated security objects via DACPAC (roles, permissions) | 4 | DBA |
| E1-S3.T2 | Map SQL-authenticated users to Entra ID identities | 16 | DBA |
| E1-S3.T3 | Configure row-level security policies | 10 | DBA |
| E1-S3.T4 | Verify GRANT/REVOKE/DENY permissions match source | 6 | DBA |
| E1-S3.T5 | Security audit and sign-off | 4 | DBA, Architect |

### E1-S4: Function Migration

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | XS (2 hrs) |
| **Sprint** | 1 |
| **Owner** | DBA |
| **Depends On** | E1-S2 (schemas deployed) |
| **Acceptance Criteria** | All 4 functions migrated and tested |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E1-S4.T1 | Deploy 4 functions via Migration Assistant | 1 | DBA |
| E1-S4.T2 | Test function execution in target DW | 1 | DBA |

---

## Epic E2: Table Migration

**Sprints:** 2–5 | **Total Hours:** ~2,292 | **Roadmap:** [Phase 1 — Section 5.3](roadmap.md#53-table-ddl-migration-sprints-25)

### E2-S1: Table Batch 1 (380 tables)

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | XL (646 hrs) |
| **Sprint** | 2 |
| **Owner** | Data Engineers (4), DBA, Sr Data Engineers |
| **Depends On** | E1 complete (foundation objects deployed) |
| **Acceptance Criteria** | 380 tables migrated (DDL + data); row count validation 100% pass; checksum validation pass |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E2-S1.T1 | Upload Batch 1 DACPAC to Migration Assistant | 4 | Sr Data Engineer |
| E2-S1.T2 | Review auto-translated DDL for 380 tables | 30 | Data Engineers (4) |
| E2-S1.T3 | Fix flagged incompatibilities (Copilot-assisted) | 60 | Sr Data Engineers, DBA |
| E2-S1.T4 | Deploy table DDL to target Fabric DW | 20 | Data Engineers (4) |
| E2-S1.T5 | Configure Data Factory copy jobs (standard tables) | 80 | Data Engineers (4) |
| E2-S1.T6 | Configure partitioned copy jobs (large tables) | 40 | Sr Data Engineer |
| E2-S1.T7 | Execute data copy jobs | 120 | Data Engineers (4) |
| E2-S1.T8 | Row count validation | 60 | Data Engineers (4) |
| E2-S1.T9 | Checksum validation on key columns | 80 | Data Engineers (4), QA Lead |
| E2-S1.T10 | Sample record spot-checks | 40 | Data Engineers (2) |
| E2-S1.T11 | Document fix patterns and update prompt library | 12 | Sr Data Engineer |
| | **Subtotal** | **546** | |

> Sprint 2 total for Acc 1 scope: 646 hrs (includes overhead/context-switching buffer)

### E2-S2: Table Batch 2 (380 tables)

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | XL (646 hrs) |
| **Sprint** | 3 |
| **Owner** | Data Engineers (4), DBA, Sr Data Engineers |
| **Depends On** | E2-S1 (Batch 1 validation pass) |
| **Acceptance Criteria** | 760 cumulative tables migrated; all validation gates pass |

**Tasks:** Mirror E2-S1 task structure (E2-S2.T1 through E2-S2.T11) with same hours. Team applies patterns learned in Batch 1 — expect fix resolution to be faster.

### E2-S3: Table Batch 3 (380 tables)

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | L (500 hrs) |
| **Sprint** | 4 |
| **Owner** | Data Engineers (3), DBA |
| **Depends On** | E2-S2 (Batch 2 validation pass) |
| **Acceptance Criteria** | 1,140 cumulative tables migrated; all validation gates pass |

**Tasks:** Same structure as E2-S1 but with reduced capacity (Data Engineers: 3 instead of 4; 1 DE allocated to Acc 2 ADF work starting Sprint 4). Sr Data Engineers shift to ADF assessment.

| ID | Task | Hours | Role |
|---|---|---|---|
| E2-S3.T1–T11 | Same task pattern as Batch 1 | 500 | Data Engineers (3), DBA |

### E2-S4: Table Batch 4 (398 tables, final)

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | L (500 hrs) |
| **Sprint** | 5 |
| **Owner** | Data Engineers (3), DBA |
| **Depends On** | E2-S3 (Batch 3 validation pass) |
| **Acceptance Criteria** | **1,538 / 1,538 tables migrated (100%)**; comprehensive validation pass; TABLE MIGRATION COMPLETE milestone |

**Tasks:** Same structure as E2-S3. Final batch includes 398 tables (remainder). Extra validation rigor for sign-off.

---

## Epic E3: View Migration

**Sprints:** 2–3 | **Total Hours:** ~272 | **Roadmap:** [Phase 1 — Section 5.4](roadmap.md#54-view-ddl-migration-sprints-23)

### E3-S1: View Batch 1 (180 views)

| Field | Value |
|---|---|
| **Priority** | P2 |
| **Effort** | M (136 hrs) |
| **Sprint** | 2 |
| **Owner** | Data Engineer |
| **Depends On** | E2-S1 (Batch 1 tables deployed — views depend on underlying tables) |
| **Acceptance Criteria** | 180 views migrated; dependency resolution confirmed; view queries execute correctly |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E3-S1.T1 | Upload view definitions to Migration Assistant | 4 | Data Engineer |
| E3-S1.T2 | Review auto-translated view DDL | 16 | Data Engineer |
| E3-S1.T3 | Fix incompatible view constructs (Copilot-assisted) | 24 | Data Engineer, Sr Data Engineer |
| E3-S1.T4 | Deploy view DDL to target Fabric DW | 12 | Data Engineer |
| E3-S1.T5 | Validate view query execution | 30 | Data Engineer |
| E3-S1.T6 | Verify view-to-table dependency resolution | 20 | Data Engineer |
| E3-S1.T7 | Row count comparison (view results vs. source) | 20 | Data Engineer |
| E3-S1.T8 | Document view-specific fix patterns | 10 | Data Engineer |

### E3-S2: View Batch 2 (182 views, final)

| Field | Value |
|---|---|
| **Priority** | P2 |
| **Effort** | M (136 hrs) |
| **Sprint** | 3 |
| **Owner** | Data Engineer |
| **Depends On** | E3-S1 (Batch 1 views complete); E2-S2 (Batch 2 tables deployed) |
| **Acceptance Criteria** | **362 / 362 views migrated (100%)**; VIEW MIGRATION COMPLETE milestone |

**Tasks:** Mirror E3-S1 task structure (E3-S2.T1 through E3-S2.T8) with same hours.

---

## Epic E4: Connection Rerouting

**Sprint:** 15 | **Total Hours:** ~15 | **Roadmap:** [Phase 4](roadmap.md#8-phase-4-reroute-connections)

### E4-S1: Connection Inventory

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | XS (5 hrs) |
| **Sprint** | 15 |
| **Owner** | DBA |
| **Depends On** | All table and view migration complete; production deployment |
| **Acceptance Criteria** | Complete inventory of Synapse-pointing connections; rerouting plan documented |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E4-S1.T1 | Query Fabric REST API for all connections | 2 | DBA |
| E4-S1.T2 | Filter and catalog Synapse-pointing connections | 2 | DBA |
| E4-S1.T3 | Create rerouting execution plan | 1 | DBA |

### E4-S2: Execute Connection Rerouting

| Field | Value |
|---|---|
| **Priority** | P1 |
| **Effort** | XS (10 hrs) |
| **Sprint** | 15 |
| **Owner** | Data Engineers, DBA |
| **Depends On** | E4-S1 (inventory complete) |
| **Acceptance Criteria** | All connections rerouted to Fabric DW; Power BI refresh succeeds; downstream pipelines validated |

**Tasks:**

| ID | Task | Hours | Role |
|---|---|---|---|
| E4-S2.T1 | Batch PATCH connections via REST API | 3 | DBA |
| E4-S2.T2 | Validate Power BI semantic model refresh | 2 | Data Engineer |
| E4-S2.T3 | Validate downstream pipeline connections | 2 | Data Engineer |
| E4-S2.T4 | Run smoke tests on critical data paths | 2 | Data Engineer, QA Lead |
| E4-S2.T5 | Sign-off and document rerouting results | 1 | DBA |

---

## Summary

| Epic | Stories | Sprint(s) | Hours | Objects |
|---|---|---|---|---|
| E0: Discovery & Setup | 4 | 0 | ~120 | — |
| E1: Schema & Foundation | 4 | 1 | ~91 | 60 |
| E2: Table Migration | 4 | 2–5 | ~2,292 | 1,538 |
| E3: View Migration | 2 | 2–3 | ~272 | 362 |
| E4: Connection Rerouting | 2 | 15 | ~15 | — |
| **Total** | **16** | **0–5, 15** | **~2,790** | **1,960** |

> Note: Total hours (2,790) represents Acc 1 direct scope. Difference from the 3,544 accelerated hours total includes PM governance, architecture guidance, and cross-accelerator coordination overhead distributed across sprints.

---

*Backlog derived from the [Roadmap](roadmap.md) and aligned with [Phase 2 sprint data](../../Sprint_Plan_Synapse_to_Fabric.md). Each story maps to specific orchestrator tasks in the [execution plan](design/orchestrator_fabric_migrate.md).*
