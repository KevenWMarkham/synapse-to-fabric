# DACPAC Extraction Tool

Automated DACPAC extraction from Azure Synapse Dedicated SQL Pools with built-in verification reporting. Part of the **Fabric Migration Assistant** accelerator within the DMTSP Accelerators suite.

## Purpose

When migrating from Azure Synapse Dedicated SQL Pools to Microsoft Fabric, the first step is capturing the complete database schema as a DACPAC (Data-tier Application Package). This tool automates that process and adds a verification layer that compares the extracted DACPAC contents against the live source catalog to ensure nothing was missed.

The tool handles:

- **Discovery** of the SqlPackage CLI across common installation locations
- **Authentication** via four methods: SQL Auth, Azure AD Interactive, Service Principal, and Managed Identity
- **Extraction** with configurable retry logic and exponential backoff
- **Verification** by comparing source catalog object counts against DACPAC model.xml contents
- **Reporting** in JSON and CSV formats for audit trails and downstream automation

## Prerequisites

| Requirement | Details |
|---|---|
| **SqlPackage CLI** | Install via `dotnet tool install -g microsoft.sqlpackage` or include with Visual Studio / SSDT / Azure Data Studio |
| **PowerShell** | Version 5.1 (Windows PowerShell) or 7.0+ (PowerShell Core) |
| **Network access** | TCP port 1433 to your Synapse SQL endpoint. Ensure firewall rules allow the client IP. |
| **.NET Framework** | 4.7.2+ (typically pre-installed on Windows) for System.IO.Compression.FileSystem |
| **Permissions** | The authenticated identity must have `VIEW DEFINITION` on the target database for catalog queries |

### Installing SqlPackage

```powershell
# Recommended: .NET global tool
dotnet tool install -g microsoft.sqlpackage

# Verify installation
sqlpackage /version
```

## Quick Start

### Azure AD Interactive (recommended for development)

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01"
```

A browser window will open for Azure AD sign-in.

### SQL Authentication

1. Copy `config.template.json` to `config.json`
2. Fill in the `sqlAuth` credentials
3. Run:

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01" `
    -AuthMethod SqlAuth `
    -ConfigPath ./config.json
```

### Service Principal

1. Copy `config.template.json` to `config.json`
2. Fill in the `servicePrincipal` section (tenantId, clientId, clientSecret)
3. Run:

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01" `
    -AuthMethod ServicePrincipal `
    -ConfigPath ./config.json
```

### Managed Identity (from Azure VM or App Service)

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01" `
    -AuthMethod ManagedIdentity
```

### Skip Verification

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01" `
    -SkipVerification
```

### Custom Output Directory

```powershell
.\Extract-SynapseDacpac.ps1 `
    -ServerEndpoint "myworkspace.sql.azuresynapse.net" `
    -DatabaseName "dedicated_pool_01" `
    -OutputPath "D:\migration\exports"
```

## Parameters

| Parameter | Required | Default | Description |
|---|---|---|---|
| `-ServerEndpoint` | Yes | - | Synapse SQL endpoint (e.g., `myworkspace.sql.azuresynapse.net`) |
| `-DatabaseName` | Yes | - | Dedicated SQL pool name |
| `-AuthMethod` | No | `AzureADInteractive` | One of: `SqlAuth`, `AzureADInteractive`, `ServicePrincipal`, `ManagedIdentity` |
| `-OutputPath` | No | `./output` | Directory for DACPAC and report files |
| `-ConfigPath` | No | `./config.json` | Path to JSON configuration file |
| `-SkipVerification` | No | `$false` | Skip the post-extraction verification phase |
| `-Verbose` | No | `$false` | Enable detailed diagnostic output |

## Configuration Reference

Copy `config.template.json` to `config.json` and customize as needed. Command-line parameters override config file values for `serverEndpoint`, `databaseName`, `authMethod`, and `outputPath`.

### connection

| Field | Type | Description |
|---|---|---|
| `serverEndpoint` | string | Synapse SQL endpoint FQDN |
| `databaseName` | string | Dedicated SQL pool name |
| `authMethod` | string | Authentication method |
| `sqlAuth.username` | string | SQL login username (SqlAuth only) |
| `sqlAuth.password` | string | SQL login password (SqlAuth only) |
| `servicePrincipal.tenantId` | string | Azure AD tenant ID (ServicePrincipal only) |
| `servicePrincipal.clientId` | string | App registration client ID (ServicePrincipal only) |
| `servicePrincipal.clientSecret` | string | App registration client secret (ServicePrincipal only) |

### extraction

| Field | Type | Default | Description |
|---|---|---|---|
| `outputPath` | string | `./output` | Directory for generated files |
| `sqlPackagePath` | string | `auto` | Path to SqlPackage.exe, or `auto` for auto-discovery |
| `extractionProperties.ExtractAllTableData` | bool | `false` | Include table data in DACPAC (not recommended for schema-only migration) |
| `extractionProperties.VerifyExtraction` | bool | `true` | SqlPackage internal verification flag |
| `extractionProperties.CommandTimeout` | int | `120` | SQL command timeout in seconds |
| `retryPolicy.maxAttempts` | int | `3` | Maximum extraction retry attempts |
| `retryPolicy.delaySeconds` | int | `10` | Initial delay between retries (seconds) |
| `retryPolicy.backoffMultiplier` | number | `2` | Exponential backoff multiplier |

### verification

| Field | Type | Default | Description |
|---|---|---|---|
| `enabled` | bool | `true` | Enable post-extraction verification |
| `objectCountTolerance` | int | `0` | Acceptable count difference (0 = exact match) |
| `reportFormats` | string[] | `["json","csv"]` | Report output formats |
| `objectTypes` | string[] | *(see below)* | Object types to verify |

Default object types: `TABLE`, `VIEW`, `STORED_PROCEDURE`, `FUNCTION`, `SCHEMA`, `EXTERNAL_TABLE`, `EXTERNAL_DATA_SOURCE`, `EXTERNAL_FILE_FORMAT`, `STATISTICS`

## Output Files

After a successful run, the output directory contains:

| File | Description |
|---|---|
| `<database>_<timestamp>.dacpac` | The extracted DACPAC file containing the full database schema |
| `extraction_log_<timestamp>.txt` | SqlPackage stdout/stderr output from the extraction |
| `validation_report_<timestamp>.json` | Detailed verification report with metadata, counts, and comparison results |
| `validation_report_<timestamp>.csv` | Tabular verification report (ObjectType, SourceCount, ExtractedCount, Delta, Status) |

### JSON Report Structure

```json
{
  "metadata": {
    "generatedAt": "2025-01-15T10:30:00.0000000-05:00",
    "toolVersion": "1.0.0",
    "serverEndpoint": "myworkspace.sql.azuresynapse.net",
    "databaseName": "dedicated_pool_01",
    "overallStatus": "PASS",
    "summary": {
      "totalTypes": 9,
      "passed": 9,
      "warnings": 0,
      "failures": 0
    }
  },
  "sourceCounts": { "TABLE": 150, "VIEW": 45, ... },
  "extractedCounts": { "TABLE": 150, "VIEW": 45, ... },
  "comparison": [
    { "objectType": "TABLE", "sourceCount": 150, "extractedCount": 150, "delta": 0, "status": "PASS" }
  ]
}
```

## Verification Process

The verification phase compares object counts between the live Synapse catalog and the extracted DACPAC:

1. **Source Baseline** (Phase 1): Queries `sys.objects`, `sys.schemas`, `sys.external_tables`, `sys.external_data_sources`, `sys.external_file_formats`, and `sys.stats` to count all user-defined objects by type.

2. **DACPAC Parsing** (Phase 3): Extracts `model.xml` from the DACPAC (a ZIP archive) and counts XML elements by their DAC model type, mapping them to catalog type names (e.g., `SqlTable` maps to `TABLE`).

3. **Comparison**: For each object type, calculates the delta between source and extracted counts. Status is assigned as:
   - **PASS**: Delta is within tolerance (default: exact match)
   - **WARN**: Extracted count exceeds source count (possible system-generated objects)
   - **FAIL**: Extracted count is less than source count (objects may be missing)

4. **Reporting**: Results are written to JSON and CSV files and displayed in a color-coded console table.

## Troubleshooting

### SqlPackage not found

```
SqlPackage.exe could not be found. Install it via: dotnet tool install -g microsoft.sqlpackage
```

**Solution**: Install SqlPackage as a .NET global tool, or set the `extraction.sqlPackagePath` field in your config to the full path of SqlPackage.exe.

### Connection timeout or network error

```
Cannot reach myworkspace.sql.azuresynapse.net on port 1433
```

**Solutions**:
- Verify the Synapse workspace firewall allows your client IP address
- Check that the dedicated SQL pool is running (not paused)
- Ensure DNS resolution works: `nslookup myworkspace.sql.azuresynapse.net`
- If behind a corporate proxy, ensure TCP 1433 is not blocked

### Authentication failures

**SQL Auth**: Verify username and password in `config.json`. Ensure the SQL login exists and has access to the database.

**Azure AD Interactive**: Ensure your Azure AD account has been granted access to the Synapse workspace. A browser window must be available for interactive sign-in.

**Service Principal**: Verify `tenantId`, `clientId`, and `clientSecret` are correct. The service principal must be granted the `db_datareader` and `VIEW DEFINITION` roles on the database.

**Managed Identity**: Ensure the script is running on an Azure resource (VM, App Service, etc.) with a system-assigned or user-assigned managed identity that has been granted access to the Synapse workspace.

### Extraction fails with timeout

```
SqlPackage extraction failed with exit code 1
```

**Solutions**:
- Increase `extraction.extractionProperties.CommandTimeout` in config (default: 120 seconds)
- Increase `extraction.retryPolicy.maxAttempts` for transient failures
- Check Synapse SQL pool resource utilization (DWU capacity)
- Try during off-peak hours for large databases

### Verification shows FAIL for some object types

**Possible causes**:
- Objects created/dropped between baseline query and extraction
- Permission differences (identity used for catalog query vs SqlPackage may see different objects)
- SqlPackage version limitations with certain Synapse-specific objects

**Solutions**:
- Re-run the extraction during a maintenance window when no DDL changes are occurring
- Increase `verification.objectCountTolerance` if minor discrepancies are acceptable
- Review the detailed report to identify which specific object types have mismatches
- Cross-reference with SSMS or Azure Data Studio object explorer

### DACPAC model.xml parsing errors

```
model.xml not found inside DACPAC. The file may be corrupted.
```

**Solutions**:
- Verify the DACPAC file is not zero bytes
- Try extracting the DACPAC manually with a ZIP tool to check contents
- Re-run the extraction with `-Verbose` to capture detailed SqlPackage output

## Integration with Next Steps

After successful extraction and verification, feed the DACPAC into the **Assessment Processor** tool:

```powershell
# From the fabric-migration-assistant tools directory
.\assessment-processor\Invoke-Assessment.ps1 -DacpacPath ".\dacpac-extract\output\mydb_20250115_103000.dacpac"
```

The Assessment Processor will analyze the DACPAC contents and generate a compatibility report for Microsoft Fabric, identifying:
- Supported vs unsupported T-SQL constructs
- Required syntax transformations
- PolyBase/external table migration considerations
- Recommended Fabric lakehouse or warehouse target mapping

## Project Structure

```
dacpac-extract/
  Extract-SynapseDacpac.ps1      # Main extraction script
  config.template.json            # Configuration template
  README.md                       # This file
  modules/
    SqlPackageWrapper.psm1        # SqlPackage discovery, argument building, execution
    ValidationReport.psm1         # Catalog queries, DACPAC parsing, comparison, reporting
  output/                         # Generated at runtime (gitignored)
    <database>_<timestamp>.dacpac
    extraction_log_<timestamp>.txt
    validation_report_<timestamp>.json
    validation_report_<timestamp>.csv
```
