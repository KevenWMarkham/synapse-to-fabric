# Fabric Migration Assistant — Strategic Roadmap

**Version:** 1.0
**Author:** Keven Markham, VP Enterprise Transformation — DMTSP
**Date:** February 6, 2026
**Status:** Draft
**Related Documents:**
- [Backlog](backlog.md) — Epics, stories, and tasks derived from this roadmap
- [Orchestrator](design/orchestrator_fabric_migrate.md) — Sprint-by-sprint execution plan
- [Sprint Plan (root)](../../Sprint_Plan_Synapse_to_Fabric.md) — Full Phase 1/Phase 2 sprint plan
- [Accelerator Buildout (root)](../../Fabric_Migration_Accelerators_DMTSP_Buildout.md) — All 7 accelerator descriptions

---

## 1. Executive Summary

The **Fabric Migration Assistant** (Acc 1) is a reusable global accelerator for migrating Azure Synapse Analytics dedicated SQL pools into Microsoft Fabric Data Warehouse. Built once and deployed across every Synapse-to-Fabric engagement, it provides a native, guided four-step migration experience: **Copy Metadata** (DACPAC upload and T-SQL translation), **Fix Problems** (Copilot-assisted incompatibility resolution), **Copy Data** (Fabric Data Factory copy jobs), and **Reroute Connections** (REST API connection redirect). The object counts below represent a reference implementation; actual counts are scaled per client.

### Scope

| Object Type | Count |
|---|---|
| Tables | 1,538 |
| Views | 362 |
| Functions | 4 |
| Schemas | 16 |
| Security Objects | 40 |
| **Total** | **1,960** |

### Hours Impact

| Metric | Hours |
|---|---|
| Base Hours (Phase 1 — Synapse DW workstream) | 6,714 |
| Accelerated Hours (Phase 2 — with Acc 1 + Acc 6) | 3,544 |
| **Hours Saved** | **3,170** |
| **Reduction** | **47%** |

> Base hours = Tables (6,152) + Views (543) + Functions (4) + Schema (5) + Security (10) = 6,714
> Accelerated hours = Tables (3,261) + Views (272) + Functions+Schema+Security (11) = 3,544

This roadmap covers the reusable Acc 1 scope within Phase 2 delivery: **Sprints 0–5 (discovery through table/view migration)** and **Sprint 15 (connection rerouting)**. The framework is designed to be deployed as-is at every client engagement, with object counts and batch sizes adjusted to match each client's environment.

---

## 2. Scope & Object Inventory

### 2.1 Object Breakdown

| # | Object Type | Count | Unit Hrs (Base) | Base Hrs | Unit Hrs (Acc) | Acc Hrs | Reduction |
|---|---|---|---|---|---|---|---|
| 1 | Tables | 1,538 | 4.0 | 6,152 | ~2.1 | 3,261 | 47% |
| 2 | Views | 362 | 1.5 | 543 | ~0.75 | 272 | 50% |
| 3 | Functions | 4 | 1.0 | 4 | ~0.5 | 2 | 50% |
| 4 | Schemas | 16 | — | 5 | — | 3 | 40% |
| 5 | Security | 40 | — | 10 | — | 6 | 40% |
| | **Total** | **1,960** | | **6,714** | | **3,544** | **47%** |

### 2.2 Out of Scope (Other Accelerators)

The following workstreams are handled by other accelerators and are **not** covered in this roadmap:

- ADF Pipelines / Datasets / Triggers → Acc 2 (ADF PowerShell Upgrade Module)
- Stored Procedures → Acc 3 (T-SQL to Spark Framework)
- CI/CD & Environment Deployment → Acc 4
- Data Validation Framework → Acc 5
- Logic Apps & ADLS → Acc 7

### 2.3 Dependency Map

Objects must be migrated in dependency order:

```
Schemas (16)
  └── Functions (4)
       └── Security (40)
            └── Tables (1,538) ── 4 batches × ~380
                 └── Views (362) ── 2 batches × ~180
```

Tables depend on schemas, functions, and security being in place. Views depend on their underlying tables being migrated first.

---

## 3. Prerequisites & Dependencies

### 3.1 Client Environment

- [ ] Synapse Access — Read-only access to source dedicated SQL pool (Sprint 0)
- [ ] Fabric Capacity — F2 or P1 capacity provisioned (required for Copilot) (Sprint 0)
- [ ] Entra ID — Service principals + security groups configured (Sprint 1)
- [ ] VNet Data Gateway — Deployed and connected to Fabric workspace (Sprint 1)
- [ ] Network Connectivity — Private endpoints between Synapse and Fabric (Sprint 1)

### 3.2 Tooling

- [ ] Visual Studio 2022 + SSDT — DACPAC extraction (primary method) — v17.x + SSDT
- [ ] SqlPackage CLI — DACPAC extraction (alternative / CI method) — Latest
- [ ] Fabric Migration Assistant — Schema translation + migration orchestration — GA (Oct 2025)
- [ ] Fabric Copilot — AI-assisted fix resolution — Requires F2/P1
- [ ] Fabric Data Factory — Copy jobs for data migration — GA
- [ ] PowerShell — Automation scripts — v7.x

### 3.3 Team

| Role | Count | Sprint Capacity | Acc 1 Allocation |
|---|---|---|---|
| Project Manager | 1 | 70 hrs | Governance, status |
| Solution Architect | 1 | 70 hrs | Design, pattern validation |
| Sr Data Engineer | 2 | 140 hrs | Accelerator setup, complex fixes |
| Data Engineer | 4 | 280 hrs | Table/view migration execution |
| QA Lead | 1 | 70 hrs | Validation framework |
| DBA | 1 | 70 hrs | Schema, security, performance |
| **Total** | **10** | **700 hrs/sprint** | |

### 3.4 External Dependencies

- [ ] Microsoft Migration Factory — Free personalized migration support — engage in Sprint 0 (Owner: Microsoft)
- [ ] Copilot availability — Requires F2/P1 capacity; confirm license in Sprint 0 (Owner: Microsoft)
- [ ] Acc 5 (Validation Framework) — Validation notebooks needed by Sprint 2 (Owner: DMTSP Team)
- [ ] Acc 4 (CI/CD) — Deployment pipelines needed for SIT promotion, Sprint 10+ (Owner: DMTSP Team)

---

## 4. Phase 0: Discovery & Accelerator Setup

**Sprint:** 0 | **Hours:** ~120 (Acc 1 share of Sprint 0's 700 hrs)
**Backlog Epic:** [E0](backlog.md#epic-e0-discovery--setup)
**Orchestrator:** [Sprint 0](design/orchestrator_fabric_migrate.md#sprint-0--discovery--accelerator-setup)

### 4.1 DACPAC Extraction

Extract the source schema using one of two methods:

**Method A — Visual Studio 2022 + SSDT:**
- [ ] Open VS 2022 → SQL Server Object Explorer → connect to Synapse SQL pool
- [ ] Right-click database → Extract Data-tier Application → save `.dacpac`
- [ ] Verify extraction includes all 1,960 objects

**Method B — SqlPackage CLI:**
```bash
SqlPackage /Action:Extract /TargetFile:source.dacpac \
  /SourceServerName:<synapse-endpoint> \
  /SourceDatabaseName:<database> \
  /SourceUser:<user> /SourcePassword:<password>
```

- [ ] DACPAC extracted successfully (Method A or B)
- [ ] Object count verified: 1,960 total

### 4.2 Source Assessment Upload

Upload DACPAC to Fabric Migration Assistant. The tool generates:

- [ ] Object inventory with migration status (pass/fail/warning)
- [ ] Incompatibility report (unsupported T-SQL constructs)
- [ ] Dependency graph (primary vs. dependent object failures)
- [ ] Assessment findings documented

### 4.3 Copilot Configuration

- [ ] Confirm F2 or P1 capacity is assigned to workspace
- [ ] Enable Copilot in Fabric admin settings
- [ ] Test Copilot fix suggestions against sample failed objects
- [ ] Initialize prompt library with pre-built fix patterns (see Appendix)

### 4.4 Batch Planning

Group objects into migration batches based on dependency analysis:

| Batch | Tables | Views | Sprint |
|---|---|---|---|
| Batch 1 | 380 | 180 | Sprint 2 |
| Batch 2 | 380 | 182 | Sprint 3 |
| Batch 3 | 380 | — | Sprint 4 |
| Batch 4 | 398 | — | Sprint 5 |
| **Total** | **1,538** | **362** | |

- [ ] Batch groupings defined and documented
- [ ] Dependency ordering validated across batches
- [ ] **Phase 0 Complete**

---

## 5. Phase 1: Copy Metadata

**Sprints:** 1–5 | **Total Acc 1 Hours:** ~2,573
**Backlog Epics:** [E1](backlog.md#epic-e1-schema--foundation), [E2](backlog.md#epic-e2-table-migration), [E3](backlog.md#epic-e3-view-migration)

### 5.1 Fabric Data Warehouse Creation (Sprint 1)

Create the target Fabric Data Warehouse and migrate foundation objects:

| Object Type | Count | Hours | Method |
|---|---|---|---|
| Fabric DW creation | 1 | 10 | Portal / API |
| Schemas | 16 | 3 | DACPAC auto-translate |
| Security objects | 40 | 6 | DACPAC + manual Entra ID mapping |
| Functions | 4 | 2 | DACPAC auto-translate |
| **Subtotal** | **61** | **21** | |

> Note: SQL-authenticated users require manual conversion to Entra ID identities. Budget ~6 hrs for security objects reflects this manual work.

- [ ] Fabric Data Warehouse created
- [ ] SQL analytics endpoint accessible and tested
- [ ] 16 schemas deployed and verified
- [ ] 40 security objects migrated (incl. Entra ID mapping)
- [ ] 4 functions deployed and tested
- [ ] **Foundation Sign-Off — 60 objects confirmed**

### 5.2 Schema & Security Migration

The Migration Assistant handles schema creation automatically during DACPAC upload. Security objects migrate with the following coverage:

- **Automated:** Roles, GRANT/REVOKE/DENY permissions, dynamic data masking
- **Manual:** SQL-authenticated users → Entra ID mapping, row-level security policies

- [ ] Automated security objects deployed via DACPAC
- [ ] SQL auth users mapped to Entra ID identities
- [ ] Row-level security policies configured
- [ ] Permissions audit pass (GRANT/REVOKE/DENY match source)

### 5.3 Table DDL Migration (Sprints 2–5)

Each batch follows the same workflow:

1. **Upload** — Load batch DACPAC segment to Migration Assistant
2. **Translate** — Tool auto-converts T-SQL DDL to Fabric-compatible syntax
3. **Fix** — Copilot flags incompatible constructs; resolve using fix patterns
4. **Deploy** — Create table DDL in target Fabric DW
5. **Validate** — Schema comparison (Acc 5 framework)

**Batch Progress:**

- [ ] Batch 1 — 380 tables migrated (DDL + data + validation) — Sprint 2
- [ ] Batch 2 — 380 tables migrated (DDL + data + validation) — Sprint 3
- [ ] Batch 3 — 380 tables migrated (DDL + data + validation) — Sprint 4
- [ ] Batch 4 — 398 tables migrated (DDL + data + validation) — Sprint 5
- [ ] **TABLE MIGRATION COMPLETE — 1,538 / 1,538**

### 5.4 View DDL Migration (Sprints 2–3)

Views run in parallel with table batches 1–2, as views depend on their underlying tables:

| Batch | Views | Depends On | Sprint |
|---|---|---|---|
| View Batch 1 | 180 | Table Batch 1 (380 tables deployed) | Sprint 2 |
| View Batch 2 | 182 | Table Batch 2 (760 tables deployed) | Sprint 3 |

- [ ] View Batch 1 — 180 views migrated and validated — Sprint 2
- [ ] View Batch 2 — 182 views migrated and validated — Sprint 3
- [ ] **VIEW MIGRATION COMPLETE — 362 / 362**
- [ ] **Phase 1 Complete — All 1,960 objects migrated**

### 5.5 Data Type Mapping Reference

The Migration Assistant handles most data type translations automatically. The following mappings require attention:

| Synapse Type | Fabric Type | Notes |
|---|---|---|
| `money` | `decimal(19,4)` | Precision preserved |
| `smallmoney` | `decimal(10,4)` | Precision preserved |
| `datetime` | `datetime2(3)` | Higher precision default |
| `smalldatetime` | `datetime2(0)` | Rounded to minutes |
| `datetimeoffset` | `datetime2` + offset column | Split required; no native support |
| `nchar(n)` | `char(n)` | Unicode normalization |
| `nvarchar(n)` | `varchar(n)` | Unicode normalization |
| `ntext` | `varchar(max)` | Deprecated type conversion |
| `text` | `varchar(max)` | Deprecated type conversion |
| `image` | `varbinary(max)` | Binary data preservation |
| `geometry` | Not supported | Requires workaround (WKT string) |
| `geography` | Not supported | Requires workaround (WKT string) |
| `hierarchyid` | Not supported | Flatten to string path |
| `sql_variant` | Not supported | Requires typed column decomposition |
| `xml` | `varchar(max)` | Stored as string; parse in application |
| `rowversion`/`timestamp` | `bigint` | Versioning behavior changes |
| `uniqueidentifier` | `varchar(36)` | Stored as string representation |

---

## 6. Phase 2: Fix Problems

**Embedded in Sprints 2–5** | **Hours:** ~500 (included in batch work)
**Backlog:** Tasks within [E2](backlog.md#epic-e2-table-migration) and [E3](backlog.md#epic-e3-view-migration) stories

### 6.1 Copilot-Assisted Resolution Workflow

1. **Triage** — Migration Assistant flags failed objects as "primary" (root cause) or "dependent" (downstream failures)
2. **Fix primary objects first** — Resolving a primary object often auto-fixes 3–5 dependent objects
3. **Copilot analysis** — For each failed object, Copilot analyzes the script, identifies the incompatible construct, and suggests a fix with inline comments
4. **Apply and validate** — Apply fix, re-run migration, confirm dependent objects resolve
5. **Catalog the pattern** — Add new fix patterns to the prompt library for reuse

### 6.2 Common Fix Patterns

| Pattern | Frequency | Resolution |
|---|---|---|
| Distribution hints (`DISTRIBUTION = HASH`) | High | Remove — Fabric handles distribution |
| Clustered columnstore index syntax | High | Simplify to standard index or remove |
| `IDENTITY` columns | Medium | Use `surrogate_key()` function or sequence |
| Materialized views | Medium | Convert to standard views + caching |
| External tables | Medium | Replace with OneLake shortcuts |
| `CTAS` statements | Medium | Convert to `CREATE TABLE` + `INSERT` |
| Workload management refs | Low | Remove — not applicable in Fabric |
| Cross-database references | Low | Remap to cross-warehouse shortcuts |

### 6.3 Expected Fix Volume

Based on typical Synapse environments:
- **~60% of failed objects** auto-resolve via Copilot suggestion
- **~30%** require minor manual editing with Copilot guidance
- **~10%** require significant manual refactoring

**Phase 2 Completion:**

- [ ] All primary object failures resolved
- [ ] All dependent object failures resolved
- [ ] Fix pattern catalog contains 20+ documented patterns
- [ ] Copilot prompt library updated with new patterns
- [ ] **Phase 2 Complete — All incompatibilities resolved**

---

## 7. Phase 3: Copy Data

**Embedded in Sprints 2–5** | **Hours:** Included in table batch work
**Backlog:** Data copy tasks within [E2](backlog.md#epic-e2-table-migration) stories

### 7.1 Fabric Data Factory Copy Jobs

Data migration follows DDL deployment within each batch:

1. **Connect** to source Synapse SQL pool via Fabric Data Factory
2. **Select tables** for the current batch
3. **Configure column mappings** — verify data type alignment per mapping table (Section 5.5)
4. **Execute copy** — one-time full copy for migration

### 7.2 Migration Methods

Microsoft documents 7 methods for data ingestion into Fabric Warehouse. For this migration:

| Method | Use Case | Batch Application |
|---|---|---|
| Copy job (full) | Standard tables < 10 GB | Primary method for most tables |
| Copy job (partitioned) | Large fact tables > 10 GB | Partition by date/key for throughput |
| ADLS extract + COPY command | Very large tables > 50 GB | Extract to parquet, bulk load |
| Dataflow Gen2 | Complex transformations during copy | Edge cases with type conversion |
| Notebook (Spark) | Custom logic required | Fallback for problematic tables |
| Shortcut | No physical copy needed | ADLS-backed tables (if applicable) |
| Mirroring | Near-real-time sync | Post-migration ongoing sync |

### 7.3 Validation

For each batch, validate:
- [ ] **Row counts** — Source vs. target exact match
- [ ] **Checksums** — Hash comparison on key columns
- [ ] **Sample records** — Spot-check 0.1% of records
- [ ] **Null/empty patterns** — Verify nullable columns didn't lose data

**Data Copy Completion:**

- [ ] Batch 1 data validation pass (380 tables)
- [ ] Batch 2 data validation pass (380 tables)
- [ ] Batch 3 data validation pass (380 tables)
- [ ] Batch 4 data validation pass (398 tables)
- [ ] Cross-batch validation — all 1,538 tables pass row count + checksum
- [ ] **Phase 3 Complete — All data copied and validated**

---

## 8. Phase 4: Reroute Connections

**Sprint:** 15 | **Hours:** ~15
**Backlog Epic:** [E4](backlog.md#epic-e4-connection-rerouting)
**Orchestrator:** [Sprint 15](design/orchestrator_fabric_migrate.md#sprint-15--production-cutover)

### 8.1 Connection Inventory

Use the Fabric REST API to identify all connections pointing to the old Synapse source:

```
GET https://api.fabric.microsoft.com/v1/connections
```

Filter results for connections referencing the Synapse SQL pool endpoint.

### 8.2 Batch PATCH Rerouting

For each connection, update the target to the Fabric Data Warehouse:

```
PATCH https://api.fabric.microsoft.com/v1/connections/{connectionId}
```

Update the connection string from the Synapse endpoint to the Fabric SQL analytics endpoint.

### 8.3 Downstream Validation

After rerouting:
- [ ] Power BI semantic models refresh successfully
- [ ] Downstream pipelines connect to Fabric DW
- [ ] Logic App connections validated (coordinated with Acc 7)
- [ ] Smoke tests pass on critical data paths

**Phase 4 Completion:**

- [ ] Connection inventory complete (REST API query)
- [ ] All connections rerouted via batch PATCH
- [ ] Downstream validation pass
- [ ] **Phase 4 Complete — All connections rerouted**

---

## 9. Risk Register

| ID | Risk | Probability | Impact | Mitigation | Phase |
|---|---|---|---|---|---|
| R1 | T-SQL incompatibilities exceed estimates | Medium | High | Pre-flight DACPAC analysis in Sprint 0; Copilot prompt library; 20% buffer | Phase 1–2 |
| R2 | Fabric capacity constraints during peak migration | Medium | Medium | Right-size F-SKU; schedule large table copies off-hours; monitor CU usage | Phase 3 |
| R3 | DACPAC extraction failures | Low | High | Test extraction in Sprint 0; have SqlPackage CLI as fallback; verify all 1,960 objects | Phase 0 |
| R4 | Copilot unavailability or degraded quality | Low | Medium | Manual fix fallback; maintain fix pattern catalog independent of Copilot | Phase 2 |
| R5 | Silent data loss during copy | Low | Critical | Row count + checksum validation per batch (Acc 5); no batch sign-off without passing validation | Phase 3 |
| R6 | Security gaps after migration | Medium | High | Security audit post-migration; compare Entra ID mapping against source SQL auth; penetration test | Phase 1 |
| R7 | View dependency resolution failures | Medium | Medium | Strict dependency ordering; migrate views only after underlying tables pass validation | Phase 1 |
| R8 | Large fact table copy throughput | Medium | Medium | Partitioned Copy Activity; ADLS extract fallback; off-hours scheduling | Phase 3 |

---

## 10. Success Criteria

### 10.1 Quantitative

- [ ] Object migration completeness — 100% of 1,960 objects (object count comparison)
- [ ] Row count accuracy — 100% match, source vs. target (automated row count validation)
- [ ] Data checksum accuracy — 100% match on key columns (hash comparison framework)
- [ ] Hours within estimate — within 10% of 3,544 accelerated hours (sprint burn tracking)
- [ ] Fix pattern catalog growth — 20+ documented patterns (pattern catalog review)

### 10.2 Qualitative

- [ ] Copilot prompt library enhanced — 10+ new migration-specific prompts documented
- [ ] Team velocity improvement — Batch 4 throughput > Batch 1 throughput (learning curve)
- [ ] Zero production data incidents — no data loss or corruption discovered post-cutover
- [ ] Reusable runbook delivered — DACPAC extraction + migration runbook ready for next engagement

---

## 11. Microsoft Documentation References

| # | Topic | URL |
|---|---|---|
| 1 | Fabric Migration Assistant overview | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-assistant |
| 2 | Migration Assistant — Copy Metadata step | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-assistant-copy-metadata |
| 3 | Migration Assistant — Fix Problems step | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-assistant-fix-problems |
| 4 | Migration Assistant — Copy Data step | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-assistant-copy-data |
| 5 | Migration Assistant — Reroute Connections step | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-assistant-reroute-connections |
| 6 | DACPAC extraction with SqlPackage | https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage-extract |
| 7 | DACPAC extraction with VS 2022 / SSDT | https://learn.microsoft.com/en-us/sql/ssdt/extract-publish-and-register-dacpac-files |
| 8 | T-SQL surface area — supported features | https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area |
| 9 | Data types in Fabric DW | https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types |
| 10 | Fabric Data Factory copy jobs | https://learn.microsoft.com/en-us/fabric/data-factory/copy-data-activity |
| 11 | Migration strategy — Synapse to Fabric | https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-synapse-dedicated-sql-pool-warehouse |
| 12 | Migration methods (7 ingestion paths) | https://learn.microsoft.com/en-us/fabric/data-warehouse/ingest-data |
| 13 | Connections REST API | https://learn.microsoft.com/en-us/rest/api/fabric/core/connections |
| 14 | ADF migration to Fabric Data Factory | https://learn.microsoft.com/en-us/fabric/data-factory/upgrade-paths |

---

*This roadmap is based on Phase 2 sprint data from the [Sprint Plan](../../Sprint_Plan_Synapse_to_Fabric.md) and accelerator specifications from the [DMTSP Buildout Recommendation](../../Fabric_Migration_Accelerators_DMTSP_Buildout.md). Re-baseline at Sprint 0 exit gate.*
