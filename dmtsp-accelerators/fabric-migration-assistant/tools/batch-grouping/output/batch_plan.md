# Migration Batch Plan

**Generated:** 2026-02-11T17:36:44.941124+00:00
**Tool:** Fabric Migration Batch Planner

---

## Executive Summary

| Metric | Value |
|---|---|
| Total Objects | 20 |
| Total Batches | 5 |
| Total Sprints | 5 |
| Passed Objects | 12 |
| Failed Objects | 8 |
| Pass Rate | 60.0% |

---

## Sprint Timeline

| Sprint | Batch | Type Group | Objects | Passed | Failed | Depends On |
|---|---|---|---|---|---|---|
| 1 | Foundation | foundation | 4 | 3 | 1 | Batch None |
| 2 | Table Batch 1 | table | 5 | 3 | 2 | Batch 1 |
| 6 | View Batch 1 | view | 3 | 2 | 1 | Batch 2, 1 |
| 8 | Stored Procedures | procedure | 3 | 1 | 2 | Batch 2, 3, 1 |
| 9 | Cleanup & External | cleanup | 5 | 3 | 2 | Batch 1, 2, 3, 4 |

---

## Batch Details

### Foundation (Sprint 1)

**Type Group:** foundation
**Objects:** 4 (3 passed, 1 failed)
**Depends On:** None (independent)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `db_datareader` | SECURITY | dbo | Passed | - |
| 2 | `dbo` | SCHEMA | dbo | Passed | - |
| 3 | `fn_CalculateDiscount` | FUNCTION | dbo | Failed | IDENTITY column not supported in Fabric; uses sql_variant... |
| 4 | `fn_GetFiscalYear` | FUNCTION | dbo | Passed | - |

**Failed Objects (1):**

- `dbo.fn_CalculateDiscount` [minor_manual]: IDENTITY column not supported in Fabric; uses sql_variant parameter type

---

### Table Batch 1 (Sprint 2)

**Type Group:** table
**Objects:** 5 (3 passed, 2 failed)
**Depends On:** Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `Customers` | TABLE | dbo | Passed | - |
| 2 | `Products` | TABLE | dbo | Passed | - |
| 3 | `Orders` | TABLE | dbo | Passed | - |
| 4 | `OrderDetails` | TABLE | dbo | Failed | DISTRIBUTION = HASH(OrderID) not supported in Fabric Data... |
| 5 | `Inventory` | TABLE | dbo | Failed | CLUSTERED COLUMNSTORE INDEX with non-default ORDER clause... |

**Failed Objects (2):**

- `dbo.OrderDetails` [auto_fixable]: DISTRIBUTION = HASH(OrderID) not supported in Fabric Data Warehouse
- `dbo.Inventory` [auto_fixable]: CLUSTERED COLUMNSTORE INDEX with non-default ORDER clause; DISTRIBUTION = REPLICATE not supported

---

### View Batch 1 (Sprint 6)

**Type Group:** view
**Objects:** 3 (2 passed, 1 failed)
**Depends On:** Table Batch 1 (batch 2), Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `vw_CustomerSummary` | VIEW | dbo | Passed | - |
| 2 | `vw_OrderReport` | VIEW | dbo | Passed | - |
| 3 | `vw_InventoryStatus` | VIEW | dbo | Failed | MATERIALIZED VIEW not supported in Fabric; convert to sta... |

**Failed Objects (1):**

- `dbo.vw_InventoryStatus` [minor_manual]: MATERIALIZED VIEW not supported in Fabric; convert to standard view with caching

---

### Stored Procedures (Sprint 8)

**Type Group:** procedure
**Objects:** 3 (1 passed, 2 failed)
**Depends On:** Table Batch 1 (batch 2), View Batch 1 (batch 3), Foundation (batch 1)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `usp_GenerateReport` | STORED_PROCEDURE | dbo | Failed | Uses RESULT SETS clause and workload classifier reference... |
| 2 | `usp_ProcessDailyOrders` | STORED_PROCEDURE | dbo | Passed | - |
| 3 | `usp_RefreshInventory` | STORED_PROCEDURE | dbo | Failed | Cross-database reference to [StagingDB].[dbo].[RawInvento... |

**Failed Objects (2):**

- `dbo.usp_GenerateReport` [auto_fixable]: Uses RESULT SETS clause and workload classifier reference not supported in Fabric
- `dbo.usp_RefreshInventory` [significant_refactor]: Cross-database reference to [StagingDB].[dbo].[RawInventory]; EXEC with dynamic SQL using sp_executesql with OUTPUT

---

### Cleanup & External (Sprint 9)

**Type Group:** cleanup
**Objects:** 5 (3 passed, 2 failed)
**Depends On:** Foundation (batch 1), Table Batch 1 (batch 2), View Batch 1 (batch 3), Stored Procedures (batch 4)

| # | Object Name | Type | Schema | Status | Failure Reason |
|---|---|---|---|---|---|
| 1 | `ext_AzureBlobSource` | EXTERNAL_DATA_SOURCE | dbo | Passed | - |
| 2 | `ext_CsvFormat` | EXTERNAL_FILE_FORMAT | dbo | Passed | - |
| 3 | `ext_ExchangeRates` | EXTERNAL_TABLE | dbo | Failed | EXTERNAL TABLE with DATA_SOURCE pointing to ADLS Gen2; mu... |
| 4 | `ext_MarketData` | EXTERNAL_TABLE | dbo | Failed | EXTERNAL TABLE with DATA_SOURCE pointing to Azure Blob St... |
| 5 | `stat_Orders_OrderDate` | STATISTICS | dbo | Passed | - |

**Failed Objects (2):**

- `dbo.ext_ExchangeRates` [auto_fixable]: EXTERNAL TABLE with DATA_SOURCE pointing to ADLS Gen2; must convert to OneLake shortcut
- `dbo.ext_MarketData` [auto_fixable]: EXTERNAL TABLE with DATA_SOURCE pointing to Azure Blob Storage; must convert to OneLake shortcut or Fabric Lakehouse table

---

## Dependency Analysis

| Metric | Value |
|---|---|
| Total Nodes | 20 |
| Total Edges | 38 |
| Dependency Layers | 6 |
| Max Chain Depth | 5 |
| Circular Dependencies | 0 |
| Root Nodes (no deps) | 3 |
| Leaf Nodes (no dependents) | 8 |

---

## Migration Order Checklist

Execute batches in the following order. Each batch should be fully
migrated and validated before proceeding to the next.

- [ ] **Sprint 1 - Foundation** (4 objects)
  - [x] `dbo.db_datareader` (SECURITY)
  - [x] `dbo.dbo` (SCHEMA)
  - [ ] `dbo.fn_CalculateDiscount` (FUNCTION)
  - [x] `dbo.fn_GetFiscalYear` (FUNCTION)
- [ ] **Sprint 2 - Table Batch 1** (5 objects)
  - [x] `dbo.Customers` (TABLE)
  - [x] `dbo.Products` (TABLE)
  - [x] `dbo.Orders` (TABLE)
  - [ ] `dbo.OrderDetails` (TABLE)
  - [ ] `dbo.Inventory` (TABLE)
- [ ] **Sprint 6 - View Batch 1** (3 objects)
  - [x] `dbo.vw_CustomerSummary` (VIEW)
  - [x] `dbo.vw_OrderReport` (VIEW)
  - [ ] `dbo.vw_InventoryStatus` (VIEW)
- [ ] **Sprint 8 - Stored Procedures** (3 objects)
  - [ ] `dbo.usp_GenerateReport` (STORED_PROCEDURE)
  - [x] `dbo.usp_ProcessDailyOrders` (STORED_PROCEDURE)
  - [ ] `dbo.usp_RefreshInventory` (STORED_PROCEDURE)
- [ ] **Sprint 9 - Cleanup & External** (5 objects)
  - [x] `dbo.ext_AzureBlobSource` (EXTERNAL_DATA_SOURCE)
  - [x] `dbo.ext_CsvFormat` (EXTERNAL_FILE_FORMAT)
  - [ ] `dbo.ext_ExchangeRates` (EXTERNAL_TABLE)
  - [ ] `dbo.ext_MarketData` (EXTERNAL_TABLE)
  - [x] `dbo.stat_Orders_OrderDate` (STATISTICS)

---

*Report generated by the Fabric Migration Batch Planner. Review and adjust batch assignments before sprint execution.*
