# Fabric Migration Assessment Report

**Generated:** 2026-02-11T17:35:51Z
**Source:** examples/sample_assessment.csv
**Tool:** Fabric Migration Assessment Processor v1.0.0

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Objects | 20 |
| Passed | 11 |
| Failed | 9 |
| Warnings | 0 |
| Pass Rate | 55.0% |

## Object Inventory

| Type | Total | Passed | Failed | Warning |
|------|-------|--------|--------|---------|
| EXTERNAL_TABLE | 2 | 0 | 2 | 0 |
| FUNCTION | 2 | 1 | 1 | 0 |
| SCHEMA | 1 | 1 | 0 | 0 |
| SECURITY | 2 | 2 | 0 | 0 |
| STATISTICS | 2 | 1 | 1 | 0 |
| STORED_PROCEDURE | 3 | 1 | 2 | 0 |
| TABLE | 5 | 3 | 2 | 0 |
| VIEW | 3 | 2 | 1 | 0 |

## Failure Analysis

### Primary Failures (Root Causes): 9

| Object | Type | Failure Reason | Impact Score |
|--------|------|----------------|--------------|
| dbo.DimDate | TABLE | DISTRIBUTION type REPLICATE not supported in Fabric Warehouse | 2 |
| dbo.DimGeography | TABLE | EXTERNAL TABLE requires DATA_SOURCE configuration not available in Fabric | 0 |
| reporting.vw_ProductPerformance | VIEW | MATERIALIZED VIEW not supported in Fabric Warehouse | 0 |
| etl.usp_RefreshDimCustomer | STORED_PROCEDURE | cross database reference to staging database not supported | 0 |
| etl.usp_CalculateMetrics | STORED_PROCEDURE | stored procedure contains incompatible cursor-based logic requiring refactor | 0 |
| dbo.fn_FormatCurrency | FUNCTION | deprecated money data type conversion not supported | 0 |
| staging.ext_CustomerFeed | EXTERNAL_TABLE | EXTERNAL TABLE requires DATA_SOURCE blob storage configuration | 0 |
| staging.ext_ProductCatalog | EXTERNAL_TABLE | EXTERNAL TABLE requires DATA_SOURCE ADLS Gen2 configuration | 0 |
| dbo.stat_DimCustomer_Region | STATISTICS | STATISTICS auto-create syntax incompatible with Fabric | 0 |

### Dependent Failures (Cascading): 0

### Dependency Graph Summary

- Total nodes: 20
- Total edges: 6
- Max chain depth: 2

**Top 5 Most Impactful Failures:**

1. **dbo.DimDate** (impact: 2) - DISTRIBUTION type REPLICATE not supported in Fabric Warehous
1. **dbo.DimGeography** (impact: 0) - EXTERNAL TABLE requires DATA_SOURCE configuration not availa
1. **reporting.vw_ProductPerformance** (impact: 0) - MATERIALIZED VIEW not supported in Fabric Warehouse
1. **etl.usp_RefreshDimCustomer** (impact: 0) - cross database reference to staging database not supported
1. **etl.usp_CalculateMetrics** (impact: 0) - stored procedure contains incompatible cursor-based logic re

## Triage Breakdown

Total failures: 9

| Category | Count | Percentage | Description |
|----------|-------|------------|-------------|
| Auto-Fixable | 2 | 22.2% | Can be automatically fixed by Copilot prompts or scripts |
| Minor Manual | 2 | 22.2% | Requires minor manual intervention (< 1 hour per object) |
| Significant Refactor | 5 | 55.6% | Requires significant refactoring (> 1 hour per object) |
| Uncategorized | 0 | 0.0% | Does not match any known failure pattern |

## Dependency Chains

Dependency chains for the most impactful failures:

### dbo.DimDate

Impact score: 2 downstream objects blocked


### dbo.DimGeography

Impact score: 0 downstream objects blocked


### reporting.vw_ProductPerformance

Impact score: 0 downstream objects blocked


## Recommended Actions

1. **dbo.DimDate** (TABLE) - [Auto-Fixable] [ROOT CAUSE]
   - DISTRIBUTION type REPLICATE not supported in Fabric Warehouse (Copilot prompts: DIST-001, DIST-002, DIST-003)

2. **dbo.stat_DimCustomer_Region** (STATISTICS) - [Auto-Fixable] [ROOT CAUSE]
   - STATISTICS auto-create syntax incompatible with Fabric (Copilot prompts: STAT-001)

3. **reporting.vw_ProductPerformance** (VIEW) - [Minor Manual] [ROOT CAUSE]
   - MATERIALIZED VIEW not supported in Fabric Warehouse (Copilot prompts: MVIEW-001, MVIEW-002)

4. **dbo.fn_FormatCurrency** (FUNCTION) - [Minor Manual] [ROOT CAUSE]
   - deprecated money data type conversion not supported (Copilot prompts: DTYPE-001, DTYPE-002)

5. **dbo.DimGeography** (TABLE) - [Significant Refactor] [ROOT CAUSE]
   - EXTERNAL TABLE requires DATA_SOURCE configuration not available in Fabric (Copilot prompts: EXT-001, EXT-002, EXT-003)

6. **etl.usp_RefreshDimCustomer** (STORED_PROCEDURE) - [Significant Refactor] [ROOT CAUSE]
   - cross database reference to staging database not supported (Copilot prompts: XREF-001, XREF-002)

7. **etl.usp_CalculateMetrics** (STORED_PROCEDURE) - [Significant Refactor] [ROOT CAUSE]
   - stored procedure contains incompatible cursor-based logic requiring refactor (Copilot prompts: PROC-001, PROC-002)

8. **staging.ext_CustomerFeed** (EXTERNAL_TABLE) - [Significant Refactor] [ROOT CAUSE]
   - EXTERNAL TABLE requires DATA_SOURCE blob storage configuration (Copilot prompts: EXT-001, EXT-002, EXT-003)

9. **staging.ext_ProductCatalog** (EXTERNAL_TABLE) - [Significant Refactor] [ROOT CAUSE]
   - EXTERNAL TABLE requires DATA_SOURCE ADLS Gen2 configuration (Copilot prompts: EXT-001, EXT-002, EXT-003)

## Migration Order

Objects grouped into layers for safe migration ordering (all objects in a layer can be migrated in parallel):

### Layer 1 (16 objects)

- dbo.db_datareader_sales
- dbo.db_datawriter_etl
- dbo.DimCustomer
- dbo.DimDate
- dbo.DimProduct
- dbo.fn_FormatCurrency
- dbo.fn_GetFiscalYear
- dbo.SalesSchema
- etl.usp_CalculateMetrics
- etl.usp_LoadFactSales
- etl.usp_RefreshDimCustomer
- reporting.vw_CustomerOrders
- reporting.vw_ProductPerformance
- reporting.vw_SalesSummary
- staging.ext_CustomerFeed
- staging.ext_ProductCatalog

### Layer 2 (3 objects)

- dbo.DimGeography
- dbo.FactSales
- dbo.stat_DimCustomer_Region

### Layer 3 (1 objects)

- dbo.stat_FactSales_Date

## Copilot Prompt Suggestions

- **dbo.DimDate**: DIST-001, DIST-002, DIST-003
- **dbo.DimGeography**: EXT-001, EXT-002, EXT-003
- **dbo.fn_FormatCurrency**: DTYPE-001, DTYPE-002
- **dbo.stat_DimCustomer_Region**: STAT-001
- **etl.usp_CalculateMetrics**: PROC-001, PROC-002
- **etl.usp_RefreshDimCustomer**: XREF-001, XREF-002
- **reporting.vw_ProductPerformance**: MVIEW-001, MVIEW-002
- **staging.ext_CustomerFeed**: EXT-001, EXT-002, EXT-003
- **staging.ext_ProductCatalog**: EXT-001, EXT-002, EXT-003

---
*Generated by Fabric Migration Assessment Processor v1.0.0 on 2026-02-11T17:35:51Z*
