<#
.SYNOPSIS
    Extracts a DACPAC from an Azure Synapse Dedicated SQL Pool with automated verification.

.DESCRIPTION
    This script automates the full DACPAC extraction lifecycle:
      1. Queries the source Synapse catalog for a baseline object inventory
      2. Invokes SqlPackage.exe to extract the DACPAC with retry logic
      3. Parses the extracted DACPAC and verifies object counts match the source
      4. Generates JSON and CSV validation reports

    Supports multiple authentication methods: SQL Auth, Azure AD Interactive,
    Service Principal (client credentials), and Managed Identity.

.PARAMETER ServerEndpoint
    The Synapse Dedicated SQL Pool endpoint (e.g., myworkspace.sql.azuresynapse.net).

.PARAMETER DatabaseName
    The name of the dedicated SQL pool (database) to extract.

.PARAMETER AuthMethod
    Authentication method. One of: SqlAuth, AzureADInteractive, ServicePrincipal, ManagedIdentity.
    Default: AzureADInteractive.

.PARAMETER OutputPath
    Directory for output files (DACPAC, reports). Default: ./output

.PARAMETER ConfigPath
    Path to a JSON configuration file. Default: ./config.json

.PARAMETER SkipVerification
    If set, skips the post-extraction verification phase.

.PARAMETER Verbose
    Enables verbose diagnostic output.

.EXAMPLE
    # Azure AD Interactive (browser sign-in prompt)
    .\Extract-SynapseDacpac.ps1 -ServerEndpoint "myws.sql.azuresynapse.net" -DatabaseName "dwh_prod"

.EXAMPLE
    # SQL Authentication
    .\Extract-SynapseDacpac.ps1 -ServerEndpoint "myws.sql.azuresynapse.net" -DatabaseName "dwh_prod" `
        -AuthMethod SqlAuth -ConfigPath ./config.json

.EXAMPLE
    # Service Principal with custom output path
    .\Extract-SynapseDacpac.ps1 -ServerEndpoint "myws.sql.azuresynapse.net" -DatabaseName "dwh_prod" `
        -AuthMethod ServicePrincipal -OutputPath "D:\exports" -ConfigPath ./config.json

.EXAMPLE
    # Managed Identity (from Azure VM) with verification skipped
    .\Extract-SynapseDacpac.ps1 -ServerEndpoint "myws.sql.azuresynapse.net" -DatabaseName "dwh_prod" `
        -AuthMethod ManagedIdentity -SkipVerification

.NOTES
    Version: 1.0.0
    Tool:    DACPAC Extraction Tool - Fabric Migration Assistant
    Module:  DMTSP Accelerators
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, HelpMessage = "Synapse SQL endpoint (e.g., myworkspace.sql.azuresynapse.net)")]
    [ValidateNotNullOrEmpty()]
    [string]$ServerEndpoint,

    [Parameter(Mandatory = $true, HelpMessage = "Dedicated SQL pool database name")]
    [ValidateNotNullOrEmpty()]
    [string]$DatabaseName,

    [Parameter(Mandatory = $false)]
    [ValidateSet('SqlAuth', 'AzureADInteractive', 'ServicePrincipal', 'ManagedIdentity')]
    [string]$AuthMethod = 'AzureADInteractive',

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = './output',

    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = './config.json',

    [Parameter(Mandatory = $false)]
    [switch]$SkipVerification
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
$TOOL_VERSION = "1.0.0"
$TOOL_NAME = "DACPAC Extraction Tool"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
function Show-Banner {
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Green
    Write-Host "    $TOOL_NAME v$TOOL_VERSION" -ForegroundColor Green
    Write-Host "    Fabric Migration Assistant - DMTSP Accelerators" -ForegroundColor Green
    Write-Host "  ============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Server:   $ServerEndpoint" -ForegroundColor White
    Write-Host "  Database: $DatabaseName" -ForegroundColor White
    Write-Host "  Auth:     $AuthMethod" -ForegroundColor White
    Write-Host "  Output:   $OutputPath" -ForegroundColor White
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Configuration Loading
# ---------------------------------------------------------------------------
function Import-Configuration {
    param([string]$Path)

    $config = @{
        connection   = @{
            serverEndpoint = $ServerEndpoint
            databaseName   = $DatabaseName
            authMethod     = $AuthMethod
            sqlAuth        = @{ username = ""; password = "" }
            servicePrincipal = @{ tenantId = ""; clientId = ""; clientSecret = "" }
        }
        extraction   = @{
            outputPath           = $OutputPath
            sqlPackagePath       = "auto"
            extractionProperties = @{
                ExtractAllTableData = $false
                VerifyExtraction    = $true
                CommandTimeout      = 120
            }
            retryPolicy          = @{
                maxAttempts       = 3
                delaySeconds      = 10
                backoffMultiplier = 2
            }
        }
        verification = @{
            enabled              = $true
            objectCountTolerance = 0
            reportFormats        = @("json", "csv")
            objectTypes          = @(
                "TABLE", "VIEW", "STORED_PROCEDURE", "FUNCTION",
                "SCHEMA", "EXTERNAL_TABLE", "EXTERNAL_DATA_SOURCE",
                "EXTERNAL_FILE_FORMAT", "STATISTICS"
            )
        }
    }

    # Load config file if it exists
    if (Test-Path -Path $Path -PathType Leaf) {
        Write-Host "  Loading configuration from: $Path" -ForegroundColor Cyan
        try {
            $fileConfig = Get-Content -Path $Path -Raw | ConvertFrom-Json

            # Merge connection settings
            if ($fileConfig.connection) {
                if ($fileConfig.connection.sqlAuth) {
                    if ($fileConfig.connection.sqlAuth.username) {
                        $config.connection.sqlAuth.username = $fileConfig.connection.sqlAuth.username
                    }
                    if ($fileConfig.connection.sqlAuth.password) {
                        $config.connection.sqlAuth.password = $fileConfig.connection.sqlAuth.password
                    }
                }
                if ($fileConfig.connection.servicePrincipal) {
                    if ($fileConfig.connection.servicePrincipal.tenantId) {
                        $config.connection.servicePrincipal.tenantId = $fileConfig.connection.servicePrincipal.tenantId
                    }
                    if ($fileConfig.connection.servicePrincipal.clientId) {
                        $config.connection.servicePrincipal.clientId = $fileConfig.connection.servicePrincipal.clientId
                    }
                    if ($fileConfig.connection.servicePrincipal.clientSecret) {
                        $config.connection.servicePrincipal.clientSecret = $fileConfig.connection.servicePrincipal.clientSecret
                    }
                }
            }

            # Merge extraction settings
            if ($fileConfig.extraction) {
                if ($fileConfig.extraction.sqlPackagePath) {
                    $config.extraction.sqlPackagePath = $fileConfig.extraction.sqlPackagePath
                }
                if ($fileConfig.extraction.outputPath -and $OutputPath -eq './output') {
                    $config.extraction.outputPath = $fileConfig.extraction.outputPath
                }
                if ($fileConfig.extraction.extractionProperties) {
                    $props = $fileConfig.extraction.extractionProperties
                    if ($null -ne $props.ExtractAllTableData) {
                        $config.extraction.extractionProperties.ExtractAllTableData = [bool]$props.ExtractAllTableData
                    }
                    if ($null -ne $props.VerifyExtraction) {
                        $config.extraction.extractionProperties.VerifyExtraction = [bool]$props.VerifyExtraction
                    }
                    if ($props.CommandTimeout) {
                        $config.extraction.extractionProperties.CommandTimeout = [int]$props.CommandTimeout
                    }
                }
                if ($fileConfig.extraction.retryPolicy) {
                    $retry = $fileConfig.extraction.retryPolicy
                    if ($retry.maxAttempts) {
                        $config.extraction.retryPolicy.maxAttempts = [int]$retry.maxAttempts
                    }
                    if ($retry.delaySeconds) {
                        $config.extraction.retryPolicy.delaySeconds = [int]$retry.delaySeconds
                    }
                    if ($retry.backoffMultiplier) {
                        $config.extraction.retryPolicy.backoffMultiplier = [double]$retry.backoffMultiplier
                    }
                }
            }

            # Merge verification settings
            if ($fileConfig.verification) {
                if ($null -ne $fileConfig.verification.enabled) {
                    $config.verification.enabled = [bool]$fileConfig.verification.enabled
                }
                if ($null -ne $fileConfig.verification.objectCountTolerance) {
                    $config.verification.objectCountTolerance = [int]$fileConfig.verification.objectCountTolerance
                }
                if ($fileConfig.verification.reportFormats) {
                    $config.verification.reportFormats = @($fileConfig.verification.reportFormats)
                }
                if ($fileConfig.verification.objectTypes) {
                    $config.verification.objectTypes = @($fileConfig.verification.objectTypes)
                }
            }

            Write-Host "  Configuration loaded successfully." -ForegroundColor Green
        }
        catch {
            Write-Warning "  Failed to parse config file: $($_.Exception.Message). Using defaults."
        }
    }
    else {
        Write-Host "  No config file found at $Path. Using parameter values and defaults." -ForegroundColor Yellow
    }

    # Apply parameter overrides (parameters always take precedence)
    $config.connection.serverEndpoint = $ServerEndpoint
    $config.connection.databaseName = $DatabaseName
    $config.connection.authMethod = $AuthMethod
    if ($OutputPath -ne './output') {
        $config.extraction.outputPath = $OutputPath
    }

    return $config
}

# ---------------------------------------------------------------------------
# Prerequisite Validation
# ---------------------------------------------------------------------------
function Test-Prerequisites {
    param(
        [hashtable]$Config,
        [string]$SqlPackagePath
    )

    $issues = [System.Collections.ArrayList]::new()

    Write-Host "  Validating prerequisites..." -ForegroundColor Cyan

    # 1. SqlPackage availability
    Write-Host "    [1/3] SqlPackage CLI............" -NoNewline
    if (Test-Path -Path $SqlPackagePath -PathType Leaf) {
        Write-Host "FOUND" -ForegroundColor Green
        Write-Host "          Path: $SqlPackagePath" -ForegroundColor Gray
    }
    else {
        Write-Host "NOT FOUND" -ForegroundColor Red
        [void]$issues.Add("SqlPackage.exe not found at: $SqlPackagePath")
    }

    # 2. Network connectivity
    Write-Host "    [2/3] Network connectivity......" -NoNewline
    $hostname = $Config.connection.serverEndpoint
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectResult = $tcpClient.BeginConnect($hostname, 1433, $null, $null)
        $waitSuccess = $connectResult.AsyncWaitHandle.WaitOne(10000, $false)
        if ($waitSuccess -and $tcpClient.Connected) {
            Write-Host "OK" -ForegroundColor Green
        }
        else {
            Write-Host "TIMEOUT" -ForegroundColor Red
            [void]$issues.Add("Cannot reach $hostname on port 1433. Check firewall rules and network connectivity.")
        }
        $tcpClient.Close()
    }
    catch {
        Write-Host "FAILED" -ForegroundColor Red
        [void]$issues.Add("Network test to $hostname`:1433 failed: $($_.Exception.Message)")
    }

    # 3. Authentication credentials
    Write-Host "    [3/3] Auth credentials.........." -NoNewline
    $authMethod = $Config.connection.authMethod
    switch ($authMethod) {
        'SqlAuth' {
            if ($Config.connection.sqlAuth.username -and $Config.connection.sqlAuth.password) {
                Write-Host "OK (SQL Auth)" -ForegroundColor Green
            }
            else {
                Write-Host "MISSING" -ForegroundColor Red
                [void]$issues.Add("SQL Authentication selected but username/password not provided in config.")
            }
        }
        'AzureADInteractive' {
            Write-Host "OK (Interactive - browser prompt)" -ForegroundColor Green
        }
        'ServicePrincipal' {
            $sp = $Config.connection.servicePrincipal
            if ($sp.tenantId -and $sp.clientId -and $sp.clientSecret) {
                Write-Host "OK (Service Principal)" -ForegroundColor Green
            }
            else {
                Write-Host "MISSING" -ForegroundColor Red
                $missing = @()
                if (-not $sp.tenantId) { $missing += "tenantId" }
                if (-not $sp.clientId) { $missing += "clientId" }
                if (-not $sp.clientSecret) { $missing += "clientSecret" }
                [void]$issues.Add("Service Principal auth selected but missing: $($missing -join ', ')")
            }
        }
        'ManagedIdentity' {
            Write-Host "OK (Managed Identity - runtime)" -ForegroundColor Green
        }
    }

    Write-Host ""

    if ($issues.Count -gt 0) {
        Write-Host "  Prerequisite issues found:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "    - $issue" -ForegroundColor Red
        }
        throw "Prerequisites not met. Resolve the above issues and retry."
    }

    Write-Host "  All prerequisites validated." -ForegroundColor Green
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

$overallStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$exitCode = 0
$generatedFiles = [System.Collections.ArrayList]::new()

try {
    # --- Banner ---
    Show-Banner

    # --- Load Configuration ---
    Write-Host "  [Phase 0] Configuration" -ForegroundColor White
    Write-Host "  ----------------------------------------" -ForegroundColor Gray
    $config = Import-Configuration -Path $ConfigPath
    $resolvedOutputPath = $config.extraction.outputPath
    Write-Host ""

    # --- Import Modules ---
    $modulesDir = Join-Path $SCRIPT_DIR "modules"
    $sqlWrapperModule = Join-Path $modulesDir "SqlPackageWrapper.psm1"
    $validationModule = Join-Path $modulesDir "ValidationReport.psm1"

    if (-not (Test-Path $sqlWrapperModule)) {
        throw "Required module not found: $sqlWrapperModule"
    }
    if (-not (Test-Path $validationModule)) {
        throw "Required module not found: $validationModule"
    }

    Import-Module $sqlWrapperModule -Force -ErrorAction Stop
    Import-Module $validationModule -Force -ErrorAction Stop
    Write-Verbose "Modules imported successfully."

    # --- Find SqlPackage ---
    $sqlPackagePath = Find-SqlPackage -ConfigPath $config.extraction.sqlPackagePath

    # --- Validate Prerequisites ---
    Test-Prerequisites -Config $config -SqlPackagePath $sqlPackagePath

    # --- Create Output Directory ---
    if (-not (Test-Path -Path $resolvedOutputPath -PathType Container)) {
        New-Item -Path $resolvedOutputPath -ItemType Directory -Force | Out-Null
        Write-Verbose "Created output directory: $resolvedOutputPath"
    }

    # ===================================================================
    # Phase 1: Pre-extraction Baseline
    # ===================================================================
    Write-Host "  [Phase 1] Pre-extraction Baseline" -ForegroundColor White
    Write-Host "  ----------------------------------------" -ForegroundColor Gray

    $sourceCounts = @{}

    try {
        Write-Host "  Querying source catalog for object inventory..." -ForegroundColor Cyan

        $sourceCountParams = @{
            ServerEndpoint = $config.connection.serverEndpoint
            DatabaseName   = $config.connection.databaseName
            AuthMethod     = $config.connection.authMethod
            CommandTimeout = $config.extraction.extractionProperties.CommandTimeout
        }

        if ($config.connection.authMethod -eq 'SqlAuth') {
            $sourceCountParams.SqlAuthCredentials = $config.connection.sqlAuth
        }
        elseif ($config.connection.authMethod -eq 'ServicePrincipal') {
            $sourceCountParams.ServicePrincipalCredentials = $config.connection.servicePrincipal
        }

        $sourceCounts = Get-SourceObjectCounts @sourceCountParams

        # Display baseline summary
        Write-Host ""
        Write-Host "  Source Object Inventory:" -ForegroundColor White
        Write-Host ("  {0,-25} {1,>8}" -f "Object Type", "Count")
        Write-Host ("  {0}" -f ("-" * 35))

        $totalObjects = 0
        foreach ($type in ($sourceCounts.Keys | Sort-Object)) {
            $count = $sourceCounts[$type]
            $totalObjects += $count
            Write-Host ("  {0,-25} {1,8}" -f $type, $count)
        }
        Write-Host ("  {0}" -f ("-" * 35))
        Write-Host ("  {0,-25} {1,8}" -f "TOTAL", $totalObjects) -ForegroundColor White
        Write-Host ""
    }
    catch {
        Write-Host "  Failed to query source catalog: $($_.Exception.Message)" -ForegroundColor Red
        Write-Warning "  Continuing without baseline. Verification may be limited."
        Write-Host ""
    }

    # ===================================================================
    # Phase 2: DACPAC Extraction
    # ===================================================================
    Write-Host "  [Phase 2] DACPAC Extraction" -ForegroundColor White
    Write-Host "  ----------------------------------------" -ForegroundColor Gray

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $dacpacFileName = "$($config.connection.databaseName)_$timestamp.dacpac"
    $dacpacFilePath = Join-Path $resolvedOutputPath $dacpacFileName

    Write-Host "  Target file: $dacpacFilePath" -ForegroundColor Cyan

    try {
        # Build arguments
        $buildArgs = @{
            ServerEndpoint       = $config.connection.serverEndpoint
            DatabaseName         = $config.connection.databaseName
            AuthMethod           = $config.connection.authMethod
            OutputFile           = $dacpacFilePath
            ExtractionProperties = $config.extraction.extractionProperties
        }

        if ($config.connection.authMethod -eq 'SqlAuth') {
            $buildArgs.SqlAuthCredentials = $config.connection.sqlAuth
        }
        elseif ($config.connection.authMethod -eq 'ServicePrincipal') {
            $buildArgs.ServicePrincipalCredentials = $config.connection.servicePrincipal
        }

        $sqlPackageArgs = Build-SqlPackageArguments @buildArgs

        # Execute extraction with retry
        $extractResult = Invoke-SqlPackageExtract `
            -SqlPackagePath $sqlPackagePath `
            -Arguments $sqlPackageArgs `
            -MaxAttempts $config.extraction.retryPolicy.maxAttempts `
            -DelaySeconds $config.extraction.retryPolicy.delaySeconds `
            -BackoffMultiplier $config.extraction.retryPolicy.backoffMultiplier

        if ($extractResult.Success) {
            Write-Host ""
            Write-Host "  DACPAC extracted successfully." -ForegroundColor Green
            Write-Host "  File: $dacpacFilePath" -ForegroundColor Cyan
            Write-Host "  Duration: $($extractResult.Duration)" -ForegroundColor Cyan
            Write-Host "  Attempts: $($extractResult.Attempts)" -ForegroundColor Cyan
            [void]$generatedFiles.Add($dacpacFilePath)

            # Save extraction log
            $logFilePath = Join-Path $resolvedOutputPath "extraction_log_$timestamp.txt"
            Set-Content -Path $logFilePath -Value $extractResult.Log -Encoding UTF8
            [void]$generatedFiles.Add($logFilePath)
            Write-Host "  Log: $logFilePath" -ForegroundColor Cyan
        }
        else {
            Write-Host ""
            Write-Host "  DACPAC extraction FAILED after $($extractResult.Attempts) attempts." -ForegroundColor Red
            Write-Host "  Duration: $($extractResult.Duration)" -ForegroundColor Red

            # Save failure log
            $logFilePath = Join-Path $resolvedOutputPath "extraction_failure_log_$timestamp.txt"
            Set-Content -Path $logFilePath -Value $extractResult.Log -Encoding UTF8
            [void]$generatedFiles.Add($logFilePath)
            Write-Host "  Failure log: $logFilePath" -ForegroundColor Yellow

            throw "DACPAC extraction failed. Review the log at: $logFilePath"
        }
    }
    catch {
        if ($_.Exception.Message -match "DACPAC extraction failed") {
            throw
        }
        Write-Host "  Extraction error: $($_.Exception.Message)" -ForegroundColor Red
        throw "DACPAC extraction encountered a fatal error: $($_.Exception.Message)"
    }

    Write-Host ""

    # ===================================================================
    # Phase 3: Verification
    # ===================================================================
    if (-not $SkipVerification -and $config.verification.enabled) {
        Write-Host "  [Phase 3] Post-extraction Verification" -ForegroundColor White
        Write-Host "  ----------------------------------------" -ForegroundColor Gray

        try {
            # Parse DACPAC for extracted counts
            Write-Host "  Parsing DACPAC for extracted object counts..." -ForegroundColor Cyan
            $extractedCounts = Read-DacpacObjectCounts -DacpacPath $dacpacFilePath

            Write-Host "  Extracted Object Counts:" -ForegroundColor White
            foreach ($type in ($extractedCounts.Keys | Sort-Object)) {
                Write-Host ("    {0,-25} {1,8}" -f $type, $extractedCounts[$type])
            }
            Write-Host ""

            # Compare counts
            Write-Host "  Comparing source vs extracted counts..." -ForegroundColor Cyan
            $comparisonResults = Compare-ObjectCounts `
                -SourceCounts $sourceCounts `
                -ExtractedCounts $extractedCounts `
                -Tolerance $config.verification.objectCountTolerance `
                -ObjectTypes $config.verification.objectTypes

            # Export report
            $reportFiles = Export-ValidationReport `
                -ComparisonResults $comparisonResults `
                -SourceCounts $sourceCounts `
                -ExtractedCounts $extractedCounts `
                -OutputPath $resolvedOutputPath `
                -DatabaseName $config.connection.databaseName `
                -ServerEndpoint $config.connection.serverEndpoint `
                -ReportFormats $config.verification.reportFormats

            foreach ($f in $reportFiles) {
                [void]$generatedFiles.Add($f)
            }

            # Check for failures
            $failCount = ($comparisonResults | Where-Object { $_.Status -eq "FAIL" }).Count
            if ($failCount -gt 0) {
                Write-Host "  Verification completed with $failCount FAILURE(s)." -ForegroundColor Yellow
                Write-Host "  Review the report and investigate missing objects before proceeding." -ForegroundColor Yellow
            }
            else {
                Write-Host "  Verification PASSED. All object counts match." -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  Verification error: $($_.Exception.Message)" -ForegroundColor Red
            Write-Warning "  Verification failed but DACPAC extraction was successful."
            Write-Warning "  You can re-run verification manually or inspect the DACPAC directly."
        }
    }
    elseif ($SkipVerification) {
        Write-Host "  [Phase 3] Verification SKIPPED (-SkipVerification)" -ForegroundColor Yellow
    }
    else {
        Write-Host "  [Phase 3] Verification DISABLED in configuration" -ForegroundColor Yellow
    }

    Write-Host ""
}
catch {
    $exitCode = 1
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Red
    Write-Host "    FATAL ERROR" -ForegroundColor Red
    Write-Host "  ============================================================" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""

    if ($_.ScriptStackTrace) {
        Write-Verbose "Stack trace:`n$($_.ScriptStackTrace)"
    }
}
finally {
    $overallStopwatch.Stop()

    # --- Final Summary ---
    Write-Host "  ============================================================" -ForegroundColor White
    Write-Host "    Execution Summary" -ForegroundColor White
    Write-Host "  ============================================================" -ForegroundColor White
    Write-Host ""

    if ($exitCode -eq 0) {
        Write-Host "  Status:   SUCCESS" -ForegroundColor Green
    }
    else {
        Write-Host "  Status:   FAILED" -ForegroundColor Red
    }

    Write-Host "  Duration: $($overallStopwatch.Elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor White
    Write-Host ""

    if ($generatedFiles.Count -gt 0) {
        Write-Host "  Generated Files:" -ForegroundColor White
        foreach ($file in $generatedFiles) {
            $fileSize = ""
            if (Test-Path -Path $file -PathType Leaf) {
                $sizeBytes = (Get-Item $file).Length
                if ($sizeBytes -ge 1MB) {
                    $fileSize = " ({0:N1} MB)" -f ($sizeBytes / 1MB)
                }
                elseif ($sizeBytes -ge 1KB) {
                    $fileSize = " ({0:N1} KB)" -f ($sizeBytes / 1KB)
                }
                else {
                    $fileSize = " ($sizeBytes bytes)"
                }
            }
            Write-Host "    - $file$fileSize" -ForegroundColor Cyan
        }
        Write-Host ""
    }

    Write-Host "  Next Steps:" -ForegroundColor White
    if ($exitCode -eq 0) {
        Write-Host "    1. Review the verification report for any warnings" -ForegroundColor Gray
        Write-Host "    2. Feed the DACPAC into the Assessment Processor tool" -ForegroundColor Gray
        Write-Host "    3. Run: .\tools\assessment-processor\Invoke-Assessment.ps1 -DacpacPath `"$dacpacFilePath`"" -ForegroundColor Gray
    }
    else {
        Write-Host "    1. Review the error messages above" -ForegroundColor Gray
        Write-Host "    2. Check the troubleshooting section in README.md" -ForegroundColor Gray
        Write-Host "    3. Verify network connectivity and credentials" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Green
    Write-Host ""

    # Remove imported modules to avoid state leakage
    Remove-Module -Name SqlPackageWrapper -ErrorAction SilentlyContinue
    Remove-Module -Name ValidationReport -ErrorAction SilentlyContinue

    exit $exitCode
}
