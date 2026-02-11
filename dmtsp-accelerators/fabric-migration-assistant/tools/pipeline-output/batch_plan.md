# Migration Batch Plan

**Generated:** 2026-02-11T17:40:47.216625+00:00
**Tool:** Fabric Migration Batch Planner

---

## Executive Summary

| Metric | Value |
|---|---|
| Total Objects | 20 |
| Total Batches | 5 |
| Total Sprints | 5 |
| Passed Objects | 11 |
| Failed Objects | 9 |
| Pass Rate | 55.0% |

---

## Sprint Timeline

| Sprint | Batch | Type Group | Objects | Passed | Failed | Depends On |
|---|---|---|---|---|---|---|
| 1 | Foundation | foundation | 5 | 4 | 1 | Batch None |
| 2 | Table Batch 1 | table | 5 | 3 | 2 | Batch 1 |
| 6 | View Batch 1 | view | 3 | 2 | 1 | Batch 2, 1 |
| 8 | Stored Procedures | procedure | 3 | 1 | 2 | Batch 2, 3, 1 |
| 9 | Cleanup & External | cleanup | 4 | 1 | 3 | Batch 1, 2, 3, 4 |

---

## Batch Details

### Foundation (Sprint 1)

**Type Group:** foundation
**Objects:** 5 (4 passed, 1 failed)
**Depends On:** None (independent)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `SalesSchema` | SCHEMA | dbo | PASSED | - |
| 2 | `db_datareader_sales` | SECURITY | dbo | PASSED | - |
| 3 | `db_datawriter_etl` | SECURITY | dbo | PASSED | - |
| 4 | `fn_FormatCurrency` | FUNCTION | dbo | FAILED | deprecated money data type conversion not supported |
| 5 | `fn_GetFiscalYear` | FUNCTION | dbo | PASSED | - |

**Failed Objects (1):**

- `dbo.fn_FormatCurrency` [minor_manual]: deprecated money data type conversion not supported

---

### Table Batch 1 (Sprint 2)

**Type Group:** table
**Objects:** 5 (3 passed, 2 failed)
**Depends On:** Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `DimCustomer` | TABLE | dbo | PASSED | - |
| 2 | `DimProduct` | TABLE | dbo | PASSED | - |
| 3 | `FactSales` | TABLE | dbo | PASSED | - |
| 4 | `DimDate` | TABLE | dbo | FAILED | DISTRIBUTION type REPLICATE not supported in Fabric Wareh... |
| 5 | `DimGeography` | TABLE | dbo | FAILED | EXTERNAL TABLE requires DATA_SOURCE configuration not ava... |

**Failed Objects (2):**

- `dbo.DimDate` [auto_fixable]: DISTRIBUTION type REPLICATE not supported in Fabric Warehouse
- `dbo.DimGeography` [significant_refactor]: EXTERNAL TABLE requires DATA_SOURCE configuration not available in Fabric

---

### View Batch 1 (Sprint 6)

**Type Group:** view
**Objects:** 3 (2 passed, 1 failed)
**Depends On:** Table Batch 1 (batch 2), Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `vw_SalesSummary` | VIEW | reporting | PASSED | - |
| 2 | `vw_CustomerOrders` | VIEW | reporting | PASSED | - |
| 3 | `vw_ProductPerformance` | VIEW | reporting | FAILED | MATERIALIZED VIEW not supported in Fabric Warehouse |

**Failed Objects (1):**

- `reporting.vw_ProductPerformance` [minor_manual]: MATERIALIZED VIEW not supported in Fabric Warehouse

---

### Stored Procedures (Sprint 8)

**Type Group:** procedure
**Objects:** 3 (1 passed, 2 failed)
**Depends On:** Table Batch 1 (batch 2), View Batch 1 (batch 3), Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `usp_CalculateMetrics` | STORED_PROCEDURE | etl | FAILED | stored procedure contains incompatible cursor-based logic... |
| 2 | `usp_LoadFactSales` | STORED_PROCEDURE | etl | PASSED | - |
| 3 | `usp_RefreshDimCustomer` | STORED_PROCEDURE | etl | FAILED | cross database reference to staging database not supported |

**Failed Objects (2):**

- `etl.usp_CalculateMetrics` [significant_refactor]: stored procedure contains incompatible cursor-based logic requiring refactor
- `etl.usp_RefreshDimCustomer` [significant_refactor]: cross database reference to staging database not supported

---

### Cleanup & External (Sprint 9)

**Type Group:** cleanup
**Objects:** 4 (1 passed, 3 failed)
**Depends On:** Foundation (batch 1), Table Batch 1 (batch 2), View Batch 1 (batch 3), Stored Procedures (batch 4)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `stat_DimCustomer_Region` | STATISTICS | dbo | FAILED | STATISTICS auto-create syntax incompatible with Fabric |
| 2 | `stat_FactSales_Date` | STATISTICS | dbo | PASSED | - |
| 3 | `ext_CustomerFeed` | EXTERNAL_TABLE | staging | FAILED | EXTERNAL TABLE requires DATA_SOURCE blob storage configur... |
| 4 | `ext_ProductCatalog` | EXTERNAL_TABLE | staging | FAILED | EXTERNAL TABLE requires DATA_SOURCE ADLS Gen2 configuration |

**Failed Objects (3):**

- `dbo.stat_DimCustomer_Region` [auto_fixable]: STATISTICS auto-create syntax incompatible with Fabric
- `staging.ext_CustomerFeed` [significant_refactor]: EXTERNAL TABLE requires DATA_SOURCE blob storage configuration
- `staging.ext_ProductCatalog` [significant_refactor]: EXTERNAL TABLE requires DATA_SOURCE ADLS Gen2 configuration

---

## Dependency Analysis

| Metric | Value |
|---|---|
| Total Nodes | 24 |
| Total Edges | 22 |
| Dependency Layers | 2 |
| Max Chain Depth | 1 |
| Circular Dependencies | 0 |
| Root Nodes (no deps) | 12 |
| Leaf Nodes (no dependents) | 19 |

---

## Migration Order Checklist

Execute batches in the following order. Each batch should be fully
migrated and validated before proceeding to the next.

- [ ] **Sprint 1 - Foundation** (5 objects)
  - [x] `dbo.SalesSchema` (SCHEMA)
  - [x] `dbo.db_datareader_sales` (SECURITY)
  - [x] `dbo.db_datawriter_etl` (SECURITY)
  - [ ] `dbo.fn_FormatCurrency` (FUNCTION)
  - [x] `dbo.fn_GetFiscalYear` (FUNCTION)
- [ ] **Sprint 2 - Table Batch 1** (5 objects)
  - [x] `dbo.DimCustomer` (TABLE)
  - [x] `dbo.DimProduct` (TABLE)
  - [x] `dbo.FactSales` (TABLE)
  - [ ] `dbo.DimDate` (TABLE)
  - [ ] `dbo.DimGeography` (TABLE)
- [ ] **Sprint 6 - View Batch 1** (3 objects)
  - [x] `reporting.vw_SalesSummary` (VIEW)
  - [x] `reporting.vw_CustomerOrders` (VIEW)
  - [ ] `reporting.vw_ProductPerformance` (VIEW)
- [ ] **Sprint 8 - Stored Procedures** (3 objects)
  - [ ] `etl.usp_CalculateMetrics` (STORED_PROCEDURE)
  - [x] `etl.usp_LoadFactSales` (STORED_PROCEDURE)
  - [ ] `etl.usp_RefreshDimCustomer` (STORED_PROCEDURE)
- [ ] **Sprint 9 - Cleanup & External** (4 objects)
  - [ ] `dbo.stat_DimCustomer_Region` (STATISTICS)
  - [x] `dbo.stat_FactSales_Date` (STATISTICS)
  - [ ] `staging.ext_CustomerFeed` (EXTERNAL_TABLE)
  - [ ] `staging.ext_ProductCatalog` (EXTERNAL_TABLE)

---

*Report generated by the Fabric Migration Batch Planner. Review and adjust batch assignments before sprint execution.*
