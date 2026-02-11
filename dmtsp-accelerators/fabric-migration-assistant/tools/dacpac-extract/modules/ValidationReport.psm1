<#
.SYNOPSIS
    Validation and reporting module for DACPAC extraction verification.

.DESCRIPTION
    Provides functions to query Synapse catalog object counts, parse DACPAC
    model.xml for extracted object counts, compare results, and export
    validation reports in JSON and CSV formats.

.NOTES
    Module: ValidationReport
    Version: 1.0.0
    Required: PowerShell 5.1+ or PowerShell 7+
#>

Set-StrictMode -Version Latest

function Get-SourceObjectCounts {
    <#
    .SYNOPSIS
        Queries the Synapse Dedicated SQL Pool catalog for object counts by type.

    .DESCRIPTION
        Connects to the source Synapse database and queries system catalog views
        (sys.objects, sys.schemas, sys.external_tables, sys.external_data_sources,
        sys.external_file_formats, sys.stats, sys.database_principals) to count
        objects by type.

    .PARAMETER ServerEndpoint
        The Synapse SQL endpoint.

    .PARAMETER DatabaseName
        The database name.

    .PARAMETER AuthMethod
        Authentication method used for the connection.

    .PARAMETER SqlAuthCredentials
        Hashtable with 'username' and 'password' for SQL auth.

    .PARAMETER ServicePrincipalCredentials
        Hashtable with 'tenantId', 'clientId', 'clientSecret' for service principal auth.

    .PARAMETER CommandTimeout
        Query timeout in seconds (default: 120).

    .OUTPUTS
        System.Collections.Hashtable - Keys are object type names, values are counts.

    .EXAMPLE
        $counts = Get-SourceObjectCounts -ServerEndpoint "myws.sql.azuresynapse.net" `
            -DatabaseName "mydb" -AuthMethod "AzureADInteractive"
    #>
    [CmdletBinding()]
    [OutputType([hashtable])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ServerEndpoint,

        [Parameter(Mandatory = $true)]
        [string]$DatabaseName,

        [Parameter(Mandatory = $true)]
        [ValidateSet('SqlAuth', 'AzureADInteractive', 'ServicePrincipal', 'ManagedIdentity')]
        [string]$AuthMethod,

        [Parameter(Mandatory = $false)]
        [hashtable]$SqlAuthCredentials,

        [Parameter(Mandatory = $false)]
        [hashtable]$ServicePrincipalCredentials,

        [Parameter(Mandatory = $false)]
        [int]$CommandTimeout = 120
    )

    $connectionString = Build-ConnectionString -ServerEndpoint $ServerEndpoint `
        -DatabaseName $DatabaseName -AuthMethod $AuthMethod `
        -SqlAuthCredentials $SqlAuthCredentials `
        -ServicePrincipalCredentials $ServicePrincipalCredentials

    $accessToken = $null
    if ($AuthMethod -eq 'ServicePrincipal') {
        $tokenEndpoint = "https://login.microsoftonline.com/$($ServicePrincipalCredentials.tenantId)/oauth2/v2.0/token"
        $body = @{
            grant_type    = "client_credentials"
            client_id     = $ServicePrincipalCredentials.clientId
            client_secret = $ServicePrincipalCredentials.clientSecret
            scope         = "https://database.windows.net/.default"
        }
        $tokenResponse = Invoke-RestMethod -Method Post -Uri $tokenEndpoint -Body $body -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop
        $accessToken = $tokenResponse.access_token
    }
    elseif ($AuthMethod -eq 'ManagedIdentity') {
        $imdsUri = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2019-08-01&resource=https://database.windows.net/"
        $tokenResponse = Invoke-RestMethod -Method Get -Uri $imdsUri -Headers @{ "Metadata" = "true" } -ErrorAction Stop
        $accessToken = $tokenResponse.access_token
    }

    $counts = @{}

    $catalogQuery = @"
-- Standard database objects from sys.objects
SELECT
    CASE o.type
        WHEN 'U'  THEN 'TABLE'
        WHEN 'V'  THEN 'VIEW'
        WHEN 'P'  THEN 'STORED_PROCEDURE'
        WHEN 'FN' THEN 'FUNCTION'
        WHEN 'IF' THEN 'FUNCTION'
        WHEN 'TF' THEN 'FUNCTION'
        WHEN 'AF' THEN 'FUNCTION'
        WHEN 'FS' THEN 'FUNCTION'
        WHEN 'FT' THEN 'FUNCTION'
        ELSE 'OTHER_' + RTRIM(o.type)
    END AS ObjectType,
    COUNT(*) AS ObjectCount
FROM sys.objects o
INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
WHERE o.is_ms_shipped = 0
  AND s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
  AND o.type IN ('U', 'V', 'P', 'FN', 'IF', 'TF', 'AF', 'FS', 'FT')
GROUP BY
    CASE o.type
        WHEN 'U'  THEN 'TABLE'
        WHEN 'V'  THEN 'VIEW'
        WHEN 'P'  THEN 'STORED_PROCEDURE'
        WHEN 'FN' THEN 'FUNCTION'
        WHEN 'IF' THEN 'FUNCTION'
        WHEN 'TF' THEN 'FUNCTION'
        WHEN 'AF' THEN 'FUNCTION'
        WHEN 'FS' THEN 'FUNCTION'
        WHEN 'FT' THEN 'FUNCTION'
        ELSE 'OTHER_' + RTRIM(o.type)
    END;
"@

    $schemaQuery = @"
SELECT COUNT(*) AS ObjectCount
FROM sys.schemas
WHERE name NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest', 'db_owner',
    'db_accessadmin', 'db_securityadmin', 'db_ddladmin', 'db_backupoperator',
    'db_datareader', 'db_datawriter', 'db_denydatareader', 'db_denydatawriter');
"@

    $externalTableQuery = @"
SELECT COUNT(*) AS ObjectCount FROM sys.external_tables;
"@

    $externalDataSourceQuery = @"
SELECT COUNT(*) AS ObjectCount FROM sys.external_data_sources;
"@

    $externalFileFormatQuery = @"
SELECT COUNT(*) AS ObjectCount FROM sys.external_file_formats;
"@

    $statisticsQuery = @"
SELECT COUNT(*) AS ObjectCount
FROM sys.stats s
INNER JOIN sys.objects o ON s.object_id = o.object_id
INNER JOIN sys.schemas sc ON o.schema_id = sc.schema_id
WHERE o.is_ms_shipped = 0
  AND sc.name NOT IN ('sys', 'INFORMATION_SCHEMA')
  AND s.auto_created = 0
  AND s.user_created = 1;
"@

    $connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)

    if ($accessToken) {
        $connection.AccessToken = $accessToken
    }

    try {
        Write-Verbose "Connecting to $ServerEndpoint/$DatabaseName for catalog query..."
        $connection.Open()

        # Execute catalog query for standard objects
        $catalogResults = Invoke-SqlQuery -Connection $connection -Query $catalogQuery -Timeout $CommandTimeout
        foreach ($row in $catalogResults) {
            $typeName = $row.ObjectType.ToString().Trim()
            $count = [int]$row.ObjectCount
            if ($counts.ContainsKey($typeName)) {
                $counts[$typeName] += $count
            }
            else {
                $counts[$typeName] = $count
            }
        }

        # Schema count
        $schemaResults = Invoke-SqlQuery -Connection $connection -Query $schemaQuery -Timeout $CommandTimeout
        if ($schemaResults -and $schemaResults.Count -gt 0) {
            $counts["SCHEMA"] = [int]$schemaResults[0].ObjectCount
        }
        else {
            $counts["SCHEMA"] = 0
        }

        # External tables
        $extTableResults = Invoke-SqlQuery -Connection $connection -Query $externalTableQuery -Timeout $CommandTimeout
        if ($extTableResults -and $extTableResults.Count -gt 0) {
            $counts["EXTERNAL_TABLE"] = [int]$extTableResults[0].ObjectCount
        }
        else {
            $counts["EXTERNAL_TABLE"] = 0
        }

        # External data sources
        $extDsResults = Invoke-SqlQuery -Connection $connection -Query $externalDataSourceQuery -Timeout $CommandTimeout
        if ($extDsResults -and $extDsResults.Count -gt 0) {
            $counts["EXTERNAL_DATA_SOURCE"] = [int]$extDsResults[0].ObjectCount
        }
        else {
            $counts["EXTERNAL_DATA_SOURCE"] = 0
        }

        # External file formats
        $extFfResults = Invoke-SqlQuery -Connection $connection -Query $externalFileFormatQuery -Timeout $CommandTimeout
        if ($extFfResults -and $extFfResults.Count -gt 0) {
            $counts["EXTERNAL_FILE_FORMAT"] = [int]$extFfResults[0].ObjectCount
        }
        else {
            $counts["EXTERNAL_FILE_FORMAT"] = 0
        }

        # User-created statistics
        $statsResults = Invoke-SqlQuery -Connection $connection -Query $statisticsQuery -Timeout $CommandTimeout
        if ($statsResults -and $statsResults.Count -gt 0) {
            $counts["STATISTICS"] = [int]$statsResults[0].ObjectCount
        }
        else {
            $counts["STATISTICS"] = 0
        }
    }
    catch {
        throw "Failed to query source catalog on $ServerEndpoint/$DatabaseName. $($_.Exception.Message)"
    }
    finally {
        if ($connection.State -eq 'Open') {
            $connection.Close()
        }
        $connection.Dispose()
    }

    return $counts
}

function Invoke-SqlQuery {
    <#
    .SYNOPSIS
        Executes a SQL query on an open SqlConnection and returns results as an array of hashtables.

    .PARAMETER Connection
        An open System.Data.SqlClient.SqlConnection.

    .PARAMETER Query
        The SQL query to execute.

    .PARAMETER Timeout
        Command timeout in seconds.

    .OUTPUTS
        System.Collections.ArrayList - Each element is a hashtable of column name to value.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [System.Data.SqlClient.SqlConnection]$Connection,

        [Parameter(Mandatory = $true)]
        [string]$Query,

        [Parameter(Mandatory = $false)]
        [int]$Timeout = 120
    )

    $command = $Connection.CreateCommand()
    $command.CommandText = $Query
    $command.CommandTimeout = $Timeout

    $results = [System.Collections.ArrayList]::new()

    try {
        $reader = $command.ExecuteReader()
        while ($reader.Read()) {
            $row = @{}
            for ($i = 0; $i -lt $reader.FieldCount; $i++) {
                $row[$reader.GetName($i)] = $reader.GetValue($i)
            }
            [void]$results.Add($row)
        }
        $reader.Close()
    }
    catch {
        throw "SQL query execution failed: $($_.Exception.Message)`nQuery: $Query"
    }
    finally {
        $command.Dispose()
    }

    return $results
}

function Build-ConnectionString {
    <#
    .SYNOPSIS
        Builds a SQL connection string based on the authentication method.

    .PARAMETER ServerEndpoint
        The Synapse SQL endpoint.

    .PARAMETER DatabaseName
        The database name.

    .PARAMETER AuthMethod
        Authentication method.

    .PARAMETER SqlAuthCredentials
        Hashtable with username and password for SQL auth.

    .PARAMETER ServicePrincipalCredentials
        Hashtable with tenantId, clientId, clientSecret for service principal auth.

    .OUTPUTS
        System.String - ADO.NET connection string.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ServerEndpoint,

        [Parameter(Mandatory = $true)]
        [string]$DatabaseName,

        [Parameter(Mandatory = $true)]
        [string]$AuthMethod,

        [Parameter(Mandatory = $false)]
        [hashtable]$SqlAuthCredentials,

        [Parameter(Mandatory = $false)]
        [hashtable]$ServicePrincipalCredentials
    )

    $builder = New-Object System.Data.SqlClient.SqlConnectionStringBuilder
    $builder["Data Source"] = "tcp:$ServerEndpoint,1433"
    $builder["Initial Catalog"] = $DatabaseName
    $builder["Encrypt"] = $true
    $builder["TrustServerCertificate"] = $false
    $builder["Connection Timeout"] = 30

    switch ($AuthMethod) {
        'SqlAuth' {
            if (-not $SqlAuthCredentials -or -not $SqlAuthCredentials.username -or -not $SqlAuthCredentials.password) {
                throw "SQL Authentication requires username and password."
            }
            $builder["User ID"] = $SqlAuthCredentials.username
            $builder["Password"] = $SqlAuthCredentials.password
        }
        'AzureADInteractive' {
            $builder["Authentication"] = "Active Directory Interactive"
        }
        'ServicePrincipal' {
            # Token-based; connection string without credentials, token set on SqlConnection.AccessToken
        }
        'ManagedIdentity' {
            # Token-based; connection string without credentials, token set on SqlConnection.AccessToken
        }
    }

    return $builder.ConnectionString
}

function Read-DacpacObjectCounts {
    <#
    .SYNOPSIS
        Parses a DACPAC file to count extracted database objects by type.

    .DESCRIPTION
        A DACPAC file is a ZIP archive containing model.xml which describes all
        database objects. This function extracts model.xml, parses it as XML,
        and counts elements by their DacPac model type, mapping them to standard
        catalog type names.

    .PARAMETER DacpacPath
        Full path to the .dacpac file.

    .OUTPUTS
        System.Collections.Hashtable - Keys are object type names, values are counts.

    .EXAMPLE
        $counts = Read-DacpacObjectCounts -DacpacPath "./output/mydb.dacpac"
    #>
    [CmdletBinding()]
    [OutputType([hashtable])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$DacpacPath
    )

    if (-not (Test-Path -Path $DacpacPath -PathType Leaf)) {
        throw "DACPAC file not found: $DacpacPath"
    }

    # DACPAC model type to catalog type mapping
    $typeMapping = @{
        "SqlTable"                = "TABLE"
        "SqlView"                 = "VIEW"
        "SqlProcedure"            = "STORED_PROCEDURE"
        "SqlScalarFunction"       = "FUNCTION"
        "SqlTableValuedFunction"  = "FUNCTION"
        "SqlInlineTableValuedFunction" = "FUNCTION"
        "SqlMultiStatementTableValuedFunction" = "FUNCTION"
        "SqlAggregateFunction"    = "FUNCTION"
        "SqlClrFunction"          = "FUNCTION"
        "SqlSchema"               = "SCHEMA"
        "SqlExternalTable"        = "EXTERNAL_TABLE"
        "SqlExternalDataSource"   = "EXTERNAL_DATA_SOURCE"
        "SqlExternalFileFormat"   = "EXTERNAL_FILE_FORMAT"
        "SqlStatistics"           = "STATISTICS"
    }

    $tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "dacpac_extract_$([System.Guid]::NewGuid().ToString('N'))"

    try {
        Write-Verbose "Extracting DACPAC to temporary directory: $tempDir"
        New-Item -Path $tempDir -ItemType Directory -Force | Out-Null

        # Extract the DACPAC (ZIP archive)
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::ExtractToDirectory($DacpacPath, $tempDir)

        $modelXmlPath = Join-Path $tempDir "model.xml"
        if (-not (Test-Path -Path $modelXmlPath -PathType Leaf)) {
            throw "model.xml not found inside DACPAC. The file may be corrupted."
        }

        Write-Verbose "Parsing model.xml..."
        [xml]$modelXml = Get-Content -Path $modelXmlPath -Raw

        # Register the DAC namespace
        $nsManager = New-Object System.Xml.XmlNamespaceManager($modelXml.NameTable)
        $dacNamespace = $modelXml.DocumentElement.NamespaceURI
        if ($dacNamespace) {
            $nsManager.AddNamespace("dac", $dacNamespace)
        }

        $counts = @{}

        # Count elements by Type attribute
        $allElements = $modelXml.SelectNodes("//dac:Element[@Type]", $nsManager)
        if (-not $allElements -or $allElements.Count -eq 0) {
            # Fallback: try without namespace
            $allElements = $modelXml.SelectNodes("//*[@Type]")
        }

        if ($allElements) {
            foreach ($element in $allElements) {
                $dacType = $element.GetAttribute("Type")

                # Extract the simple type name (strip namespace prefix if present)
                $simpleType = $dacType
                if ($dacType -match '\.([^.]+)$') {
                    $simpleType = $Matches[1]
                }

                if ($typeMapping.ContainsKey($simpleType)) {
                    $catalogType = $typeMapping[$simpleType]
                    if ($counts.ContainsKey($catalogType)) {
                        $counts[$catalogType]++
                    }
                    else {
                        $counts[$catalogType] = 1
                    }
                }
            }
        }

        # Filter out built-in schemas (dbo, guest, etc.)
        $builtInSchemas = @("dbo", "guest", "sys", "INFORMATION_SCHEMA",
            "db_owner", "db_accessadmin", "db_securityadmin", "db_ddladmin",
            "db_backupoperator", "db_datareader", "db_datawriter",
            "db_denydatareader", "db_denydatawriter")

        if ($counts.ContainsKey("SCHEMA")) {
            # Recount schemas excluding built-in ones
            $schemaCount = 0
            $schemaElements = $modelXml.SelectNodes("//dac:Element[@Type='SqlSchema']", $nsManager)
            if (-not $schemaElements -or $schemaElements.Count -eq 0) {
                $schemaElements = $modelXml.SelectNodes("//*[@Type='SqlSchema']")
            }
            if ($schemaElements) {
                foreach ($schemaEl in $schemaElements) {
                    $schemaName = $schemaEl.GetAttribute("Name")
                    # Strip brackets and schema prefix
                    $schemaName = $schemaName -replace '[\[\]]', ''
                    if ($schemaName -and ($schemaName -notin $builtInSchemas)) {
                        $schemaCount++
                    }
                }
            }
            $counts["SCHEMA"] = $schemaCount
        }

        Write-Verbose "DACPAC object counts parsed successfully."
        return $counts
    }
    catch {
        throw "Failed to parse DACPAC file: $($_.Exception.Message)"
    }
    finally {
        # Clean up temp directory
        if (Test-Path -Path $tempDir -PathType Container) {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

function Compare-ObjectCounts {
    <#
    .SYNOPSIS
        Compares source catalog object counts against DACPAC extracted counts.

    .DESCRIPTION
        Produces a comparison result for each object type, calculating the delta
        and flagging mismatches based on a configurable tolerance threshold.

    .PARAMETER SourceCounts
        Hashtable of object type -> count from the source catalog.

    .PARAMETER ExtractedCounts
        Hashtable of object type -> count from the DACPAC.

    .PARAMETER Tolerance
        Acceptable count difference threshold (default: 0 = exact match required).

    .PARAMETER ObjectTypes
        Array of object type names to include in the comparison. If empty, all
        types found in either source or extracted counts are compared.

    .OUTPUTS
        System.Collections.ArrayList - Each element is a PSCustomObject with:
            ObjectType     [string] - The object type name
            SourceCount    [int]    - Count from source catalog
            ExtractedCount [int]    - Count from DACPAC
            Delta          [int]    - Difference (Source - Extracted)
            Status         [string] - "PASS", "WARN", or "FAIL"

    .EXAMPLE
        $results = Compare-ObjectCounts -SourceCounts $src -ExtractedCounts $ext -Tolerance 0
    #>
    [CmdletBinding()]
    [OutputType([System.Collections.ArrayList])]
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$SourceCounts,

        [Parameter(Mandatory = $true)]
        [hashtable]$ExtractedCounts,

        [Parameter(Mandatory = $false)]
        [int]$Tolerance = 0,

        [Parameter(Mandatory = $false)]
        [string[]]$ObjectTypes = @()
    )

    # Determine which types to compare
    if ($ObjectTypes.Count -eq 0) {
        $allTypes = @($SourceCounts.Keys) + @($ExtractedCounts.Keys) | Select-Object -Unique | Sort-Object
    }
    else {
        $allTypes = $ObjectTypes | Sort-Object
    }

    $results = [System.Collections.ArrayList]::new()

    foreach ($type in $allTypes) {
        $sourceCount = if ($SourceCounts.ContainsKey($type)) { [int]$SourceCounts[$type] } else { 0 }
        $extractedCount = if ($ExtractedCounts.ContainsKey($type)) { [int]$ExtractedCounts[$type] } else { 0 }
        $delta = $sourceCount - $extractedCount
        $absDelta = [math]::Abs($delta)

        $status = "PASS"
        if ($absDelta -gt $Tolerance) {
            if ($sourceCount -eq 0 -and $extractedCount -eq 0) {
                $status = "PASS"
            }
            elseif ($extractedCount -gt $sourceCount) {
                # Extracted more than source -- could be system-generated objects
                $status = "WARN"
            }
            else {
                $status = "FAIL"
            }
        }

        [void]$results.Add([PSCustomObject]@{
            ObjectType     = $type
            SourceCount    = $sourceCount
            ExtractedCount = $extractedCount
            Delta          = $delta
            Status         = $status
        })
    }

    return $results
}

function Export-ValidationReport {
    <#
    .SYNOPSIS
        Writes validation comparison results to JSON and/or CSV report files.

    .DESCRIPTION
        Generates timestamped validation reports in the specified formats.
        Outputs a color-coded summary table to the console. The JSON report
        includes metadata (timestamp, server, database, overall pass/fail),
        source counts, extracted counts, and detailed comparison results.

    .PARAMETER ComparisonResults
        ArrayList of comparison result objects from Compare-ObjectCounts.

    .PARAMETER SourceCounts
        Original source catalog counts hashtable.

    .PARAMETER ExtractedCounts
        DACPAC extracted counts hashtable.

    .PARAMETER OutputPath
        Directory to write report files to.

    .PARAMETER DatabaseName
        Database name for report metadata.

    .PARAMETER ServerEndpoint
        Server endpoint for report metadata.

    .PARAMETER ReportFormats
        Array of formats to export: "json", "csv", or both.

    .OUTPUTS
        System.Collections.ArrayList - Paths of generated report files.

    .EXAMPLE
        $files = Export-ValidationReport -ComparisonResults $results -SourceCounts $src `
            -ExtractedCounts $ext -OutputPath "./output" -DatabaseName "mydb" `
            -ServerEndpoint "myws.sql.azuresynapse.net" -ReportFormats @("json","csv")
    #>
    [CmdletBinding()]
    [OutputType([System.Collections.ArrayList])]
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.ArrayList]$ComparisonResults,

        [Parameter(Mandatory = $true)]
        [hashtable]$SourceCounts,

        [Parameter(Mandatory = $true)]
        [hashtable]$ExtractedCounts,

        [Parameter(Mandatory = $true)]
        [string]$OutputPath,

        [Parameter(Mandatory = $true)]
        [string]$DatabaseName,

        [Parameter(Mandatory = $true)]
        [string]$ServerEndpoint,

        [Parameter(Mandatory = $false)]
        [string[]]$ReportFormats = @("json", "csv")
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $dateTimeIso = Get-Date -Format "o"
    $generatedFiles = [System.Collections.ArrayList]::new()

    # Determine overall status
    $failCount = ($ComparisonResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $warnCount = ($ComparisonResults | Where-Object { $_.Status -eq "WARN" }).Count
    $passCount = ($ComparisonResults | Where-Object { $_.Status -eq "PASS" }).Count
    $overallStatus = if ($failCount -gt 0) { "FAIL" } elseif ($warnCount -gt 0) { "WARN" } else { "PASS" }

    # Console summary
    Write-Host ""
    Write-Host "  ===== Verification Summary =====" -ForegroundColor White
    Write-Host ""
    Write-Host ("  {0,-25} {1,>8} {2,>10} {3,>7} {4,>8}" -f "Object Type", "Source", "Extracted", "Delta", "Status")
    Write-Host ("  {0}" -f ("-" * 62))

    foreach ($result in $ComparisonResults) {
        $statusColor = switch ($result.Status) {
            "PASS" { "Green" }
            "WARN" { "Yellow" }
            "FAIL" { "Red" }
            default { "White" }
        }

        $line = "  {0,-25} {1,8} {2,10} {3,7} " -f $result.ObjectType, $result.SourceCount, $result.ExtractedCount, $result.Delta
        Write-Host $line -NoNewline
        Write-Host $result.Status -ForegroundColor $statusColor
    }

    Write-Host ("  {0}" -f ("-" * 62))
    $overallColor = switch ($overallStatus) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
    }
    Write-Host "  Overall: " -NoNewline
    Write-Host $overallStatus -ForegroundColor $overallColor -NoNewline
    Write-Host " (Pass: $passCount, Warn: $warnCount, Fail: $failCount)"
    Write-Host ""

    # Ensure output directory exists
    if (-not (Test-Path -Path $OutputPath -PathType Container)) {
        New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
    }

    # JSON report
    if ("json" -in $ReportFormats) {
        $jsonFileName = "validation_report_$timestamp.json"
        $jsonFilePath = Join-Path $OutputPath $jsonFileName

        $comparisonArray = @()
        foreach ($result in $ComparisonResults) {
            $comparisonArray += @{
                objectType     = $result.ObjectType
                sourceCount    = $result.SourceCount
                extractedCount = $result.ExtractedCount
                delta          = $result.Delta
                status         = $result.Status
            }
        }

        $sourceCountsClean = @{}
        foreach ($key in $SourceCounts.Keys) {
            $sourceCountsClean[$key] = $SourceCounts[$key]
        }

        $extractedCountsClean = @{}
        foreach ($key in $ExtractedCounts.Keys) {
            $extractedCountsClean[$key] = $ExtractedCounts[$key]
        }

        $reportObject = [ordered]@{
            metadata = [ordered]@{
                generatedAt    = $dateTimeIso
                toolVersion    = "1.0.0"
                serverEndpoint = $ServerEndpoint
                databaseName   = $DatabaseName
                overallStatus  = $overallStatus
                summary        = [ordered]@{
                    totalTypes = $ComparisonResults.Count
                    passed     = $passCount
                    warnings   = $warnCount
                    failures   = $failCount
                }
            }
            sourceCounts    = $sourceCountsClean
            extractedCounts = $extractedCountsClean
            comparison      = $comparisonArray
        }

        $jsonContent = $reportObject | ConvertTo-Json -Depth 10
        Set-Content -Path $jsonFilePath -Value $jsonContent -Encoding UTF8

        Write-Host "  JSON report: $jsonFilePath" -ForegroundColor Cyan
        [void]$generatedFiles.Add($jsonFilePath)
    }

    # CSV report
    if ("csv" -in $ReportFormats) {
        $csvFileName = "validation_report_$timestamp.csv"
        $csvFilePath = Join-Path $OutputPath $csvFileName

        $csvLines = [System.Collections.ArrayList]::new()
        [void]$csvLines.Add("ObjectType,SourceCount,ExtractedCount,Delta,Status")

        foreach ($result in $ComparisonResults) {
            [void]$csvLines.Add("$($result.ObjectType),$($result.SourceCount),$($result.ExtractedCount),$($result.Delta),$($result.Status)")
        }

        Set-Content -Path $csvFilePath -Value ($csvLines -join "`n") -Encoding UTF8

        Write-Host "  CSV report:  $csvFilePath" -ForegroundColor Cyan
        [void]$generatedFiles.Add($csvFilePath)
    }

    return $generatedFiles
}

Export-ModuleMember -Function Get-SourceObjectCounts, Read-DacpacObjectCounts, Compare-ObjectCounts, Export-ValidationReport
