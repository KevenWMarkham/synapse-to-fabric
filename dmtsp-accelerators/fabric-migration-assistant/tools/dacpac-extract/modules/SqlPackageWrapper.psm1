<#
.SYNOPSIS
    SqlPackage CLI wrapper module for DACPAC extraction from Synapse Dedicated SQL Pools.

.DESCRIPTION
    Provides functions to locate the SqlPackage executable, build extraction arguments
    for various authentication methods, and invoke the extraction process with retry logic.

.NOTES
    Module: SqlPackageWrapper
    Version: 1.0.0
    Required: PowerShell 5.1+ or PowerShell 7+
#>

Set-StrictMode -Version Latest

function Find-SqlPackage {
    <#
    .SYNOPSIS
        Locates the SqlPackage CLI executable on the local system.

    .DESCRIPTION
        Searches for SqlPackage.exe in the following order:
        1. User-supplied override path from configuration
        2. System PATH environment variable
        3. .NET global tool installation
        4. Visual Studio installation directories
        5. SQL Server Data Tools (SSDT) directories
        6. Azure Data Studio extensions

    .PARAMETER ConfigPath
        Optional path override from configuration. If set to "auto" or empty,
        the function performs automatic discovery.

    .OUTPUTS
        System.String - Full path to SqlPackage.exe

    .EXAMPLE
        $sqlPackagePath = Find-SqlPackage
        $sqlPackagePath = Find-SqlPackage -ConfigPath "C:\tools\SqlPackage\SqlPackage.exe"
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$ConfigPath = "auto"
    )

    # If a specific path is provided (not "auto" or empty), validate and return it
    if ($ConfigPath -and $ConfigPath -ne "auto") {
        if (Test-Path -Path $ConfigPath -PathType Leaf) {
            Write-Verbose "Using configured SqlPackage path: $ConfigPath"
            return $ConfigPath
        }
        else {
            Write-Warning "Configured SqlPackage path not found: $ConfigPath. Falling back to auto-discovery."
        }
    }

    Write-Verbose "Starting automatic SqlPackage discovery..."

    # 1. Check PATH
    $pathResult = Get-Command -Name "SqlPackage" -ErrorAction SilentlyContinue
    if ($pathResult) {
        $resolvedPath = $pathResult.Source
        Write-Verbose "Found SqlPackage on PATH: $resolvedPath"
        return $resolvedPath
    }

    # 2. Check .NET global tool installation
    $dotnetToolPaths = @(
        (Join-Path $env:USERPROFILE ".dotnet\tools\SqlPackage.exe"),
        (Join-Path $env:USERPROFILE ".dotnet\tools\sqlpackage.exe")
    )
    foreach ($toolPath in $dotnetToolPaths) {
        if (Test-Path -Path $toolPath -PathType Leaf) {
            Write-Verbose "Found SqlPackage as .NET global tool: $toolPath"
            return $toolPath
        }
    }

    # 3. Check Visual Studio installation directories
    $vsBasePaths = @(
        "${env:ProgramFiles}\Microsoft Visual Studio",
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio"
    )
    $vsYears = @("2022", "2019", "2017")
    $vsEditions = @("Enterprise", "Professional", "Community", "BuildTools")
    $vsDacSubPath = "Common7\IDE\Extensions\Microsoft\SQLDB\DAC"

    foreach ($vsBase in $vsBasePaths) {
        foreach ($year in $vsYears) {
            foreach ($edition in $vsEditions) {
                $dacRoot = Join-Path $vsBase "$year\$edition\$vsDacSubPath"
                if (Test-Path -Path $dacRoot -PathType Container) {
                    $versionDirs = Get-ChildItem -Path $dacRoot -Directory -ErrorAction SilentlyContinue |
                        Sort-Object Name -Descending
                    foreach ($vDir in $versionDirs) {
                        $candidate = Join-Path $vDir.FullName "SqlPackage.exe"
                        if (Test-Path -Path $candidate -PathType Leaf) {
                            Write-Verbose "Found SqlPackage in Visual Studio ($year $edition): $candidate"
                            return $candidate
                        }
                    }
                }
            }
        }
    }

    # 4. Check SQL Server Data Tools (SSDT) standalone installations
    $ssdtPaths = @(
        "${env:ProgramFiles}\Microsoft SQL Server\160\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles}\Microsoft SQL Server\150\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles}\Microsoft SQL Server\140\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles}\Microsoft SQL Server\130\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles(x86)}\Microsoft SQL Server\160\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles(x86)}\Microsoft SQL Server\150\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles(x86)}\Microsoft SQL Server\140\DAC\bin\SqlPackage.exe",
        "${env:ProgramFiles(x86)}\Microsoft SQL Server\130\DAC\bin\SqlPackage.exe"
    )
    foreach ($ssdtPath in $ssdtPaths) {
        if (Test-Path -Path $ssdtPath -PathType Leaf) {
            Write-Verbose "Found SqlPackage in SSDT: $ssdtPath"
            return $ssdtPath
        }
    }

    # 5. Check Azure Data Studio extensions
    $adsExtBase = Join-Path $env:USERPROFILE ".azuredatastudio\extensions"
    if (Test-Path -Path $adsExtBase -PathType Container) {
        $dacpacExtDirs = Get-ChildItem -Path $adsExtBase -Directory -Filter "microsoft.dacpac*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending
        foreach ($extDir in $dacpacExtDirs) {
            $candidate = Get-ChildItem -Path $extDir.FullName -Recurse -Filter "SqlPackage.exe" -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($candidate) {
                Write-Verbose "Found SqlPackage in Azure Data Studio: $($candidate.FullName)"
                return $candidate.FullName
            }
        }
    }

    # 6. Check NuGet package cache
    $nugetPaths = @(
        (Join-Path $env:USERPROFILE ".nuget\packages\microsoft.sqlpackage"),
        (Join-Path $env:USERPROFILE ".nuget\packages\Microsoft.SqlPackage")
    )
    foreach ($nugetBase in $nugetPaths) {
        if (Test-Path -Path $nugetBase -PathType Container) {
            $versionDirs = Get-ChildItem -Path $nugetBase -Directory -ErrorAction SilentlyContinue |
                Sort-Object Name -Descending
            foreach ($vDir in $versionDirs) {
                $candidate = Get-ChildItem -Path $vDir.FullName -Recurse -Filter "SqlPackage.exe" -ErrorAction SilentlyContinue |
                    Select-Object -First 1
                if ($candidate) {
                    Write-Verbose "Found SqlPackage in NuGet cache: $($candidate.FullName)"
                    return $candidate.FullName
                }
            }
        }
    }

    throw "SqlPackage.exe could not be found. Install it via: dotnet tool install -g microsoft.sqlpackage"
}

function Build-SqlPackageArguments {
    <#
    .SYNOPSIS
        Assembles SqlPackage CLI arguments for DACPAC extraction.

    .DESCRIPTION
        Constructs the argument list for SqlPackage.exe based on the target server,
        database, authentication method, output path, and extraction properties.

    .PARAMETER ServerEndpoint
        The Synapse SQL endpoint (e.g., myworkspace.sql.azuresynapse.net).

    .PARAMETER DatabaseName
        The name of the dedicated SQL pool database.

    .PARAMETER AuthMethod
        Authentication method: SqlAuth, AzureADInteractive, ServicePrincipal, or ManagedIdentity.

    .PARAMETER OutputFile
        Full path for the output .dacpac file.

    .PARAMETER SqlAuthCredentials
        Hashtable with 'username' and 'password' keys for SQL authentication.

    .PARAMETER ServicePrincipalCredentials
        Hashtable with 'tenantId', 'clientId', and 'clientSecret' keys.

    .PARAMETER ExtractionProperties
        Hashtable of additional extraction properties to pass to SqlPackage.

    .OUTPUTS
        System.String[] - Array of arguments for SqlPackage.exe

    .EXAMPLE
        $args = Build-SqlPackageArguments -ServerEndpoint "myws.sql.azuresynapse.net" `
            -DatabaseName "mydb" -AuthMethod "AzureADInteractive" -OutputFile "./output/mydb.dacpac"
    #>
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ServerEndpoint,

        [Parameter(Mandatory = $true)]
        [string]$DatabaseName,

        [Parameter(Mandatory = $true)]
        [ValidateSet('SqlAuth', 'AzureADInteractive', 'ServicePrincipal', 'ManagedIdentity')]
        [string]$AuthMethod,

        [Parameter(Mandatory = $true)]
        [string]$OutputFile,

        [Parameter(Mandatory = $false)]
        [hashtable]$SqlAuthCredentials,

        [Parameter(Mandatory = $false)]
        [hashtable]$ServicePrincipalCredentials,

        [Parameter(Mandatory = $false)]
        [hashtable]$ExtractionProperties
    )

    $arguments = [System.Collections.ArrayList]::new()

    # Core extraction arguments
    [void]$arguments.Add("/Action:Extract")
    [void]$arguments.Add("/TargetFile:`"$OutputFile`"")
    [void]$arguments.Add("/SourceServerName:`"tcp:$ServerEndpoint,1433`"")
    [void]$arguments.Add("/SourceDatabaseName:`"$DatabaseName`"")

    # Authentication-specific arguments
    switch ($AuthMethod) {
        'SqlAuth' {
            if (-not $SqlAuthCredentials -or -not $SqlAuthCredentials.username -or -not $SqlAuthCredentials.password) {
                throw "SQL Authentication requires username and password in SqlAuthCredentials."
            }
            [void]$arguments.Add("/SourceUser:`"$($SqlAuthCredentials.username)`"")
            [void]$arguments.Add("/SourcePassword:`"$($SqlAuthCredentials.password)`"")
            [void]$arguments.Add("/SourceEncryptConnection:True")
            [void]$arguments.Add("/SourceTrustServerCertificate:False")
        }
        'AzureADInteractive' {
            [void]$arguments.Add("/UniversalAuthentication:True")
            [void]$arguments.Add("/SourceEncryptConnection:True")
            [void]$arguments.Add("/SourceTrustServerCertificate:False")
        }
        'ServicePrincipal' {
            if (-not $ServicePrincipalCredentials -or
                -not $ServicePrincipalCredentials.tenantId -or
                -not $ServicePrincipalCredentials.clientId -or
                -not $ServicePrincipalCredentials.clientSecret) {
                throw "Service Principal authentication requires tenantId, clientId, and clientSecret."
            }
            $accessToken = Get-ServicePrincipalToken -TenantId $ServicePrincipalCredentials.tenantId `
                -ClientId $ServicePrincipalCredentials.clientId `
                -ClientSecret $ServicePrincipalCredentials.clientSecret
            [void]$arguments.Add("/SourceConnectionString:`"Server=tcp:$ServerEndpoint,1433;Initial Catalog=$DatabaseName;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30`"")
            [void]$arguments.Add("/at:`"$accessToken`"")
        }
        'ManagedIdentity' {
            $accessToken = Get-ManagedIdentityToken
            [void]$arguments.Add("/SourceConnectionString:`"Server=tcp:$ServerEndpoint,1433;Initial Catalog=$DatabaseName;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30`"")
            [void]$arguments.Add("/at:`"$accessToken`"")
        }
    }

    # Additional extraction properties
    if ($ExtractionProperties) {
        foreach ($key in $ExtractionProperties.Keys) {
            $value = $ExtractionProperties[$key]
            if ($value -is [bool]) {
                $value = if ($value) { "True" } else { "False" }
            }
            [void]$arguments.Add("/p:$key=$value")
        }
    }

    return $arguments.ToArray()
}

function Get-ServicePrincipalToken {
    <#
    .SYNOPSIS
        Acquires an Azure AD access token using service principal credentials via MSAL.

    .DESCRIPTION
        Uses the MSAL.PS module or direct REST call to the Azure AD token endpoint
        to obtain a bearer token for Azure SQL Database access.

    .PARAMETER TenantId
        Azure AD tenant ID.

    .PARAMETER ClientId
        Application (client) ID of the service principal.

    .PARAMETER ClientSecret
        Client secret for the service principal.

    .OUTPUTS
        System.String - Bearer access token for Azure SQL Database.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$TenantId,

        [Parameter(Mandatory = $true)]
        [string]$ClientId,

        [Parameter(Mandatory = $true)]
        [string]$ClientSecret
    )

    $tokenEndpoint = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
    $resource = "https://database.windows.net/.default"

    $body = @{
        grant_type    = "client_credentials"
        client_id     = $ClientId
        client_secret = $ClientSecret
        scope         = $resource
    }

    try {
        Write-Verbose "Requesting access token from Azure AD for tenant: $TenantId"
        $response = Invoke-RestMethod -Method Post -Uri $tokenEndpoint -Body $body -ContentType "application/x-www-form-urlencoded" -ErrorAction Stop

        if (-not $response.access_token) {
            throw "Token response did not contain an access_token field."
        }

        Write-Verbose "Successfully acquired access token. Expires in $($response.expires_in) seconds."
        return $response.access_token
    }
    catch {
        $errorMessage = "Failed to acquire access token for service principal (ClientId: $ClientId). "
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $errorMessage += "HTTP $statusCode. "
        }
        $errorMessage += $_.Exception.Message
        throw $errorMessage
    }
}

function Get-ManagedIdentityToken {
    <#
    .SYNOPSIS
        Acquires an Azure AD access token using the Azure Instance Metadata Service (IMDS).

    .DESCRIPTION
        Calls the IMDS endpoint available on Azure VMs and other managed-identity-enabled
        compute to obtain a bearer token for Azure SQL Database access.

    .OUTPUTS
        System.String - Bearer access token for Azure SQL Database.
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param()

    $imdsEndpoint = "http://169.254.169.254/metadata/identity/oauth2/token"
    $resource = "https://database.windows.net/"
    $apiVersion = "2019-08-01"

    $uri = "${imdsEndpoint}?api-version=${apiVersion}&resource=${resource}"

    try {
        Write-Verbose "Requesting access token from Azure IMDS endpoint..."
        $response = Invoke-RestMethod -Method Get -Uri $uri -Headers @{ "Metadata" = "true" } -ErrorAction Stop

        if (-not $response.access_token) {
            throw "IMDS response did not contain an access_token field."
        }

        Write-Verbose "Successfully acquired managed identity access token. Expires on $($response.expires_on)."
        return $response.access_token
    }
    catch {
        $errorMessage = "Failed to acquire managed identity token from IMDS. "
        $errorMessage += "Ensure this script is running on an Azure resource with managed identity enabled. "
        $errorMessage += $_.Exception.Message
        throw $errorMessage
    }
}

function Invoke-SqlPackageExtract {
    <#
    .SYNOPSIS
        Executes SqlPackage.exe to extract a DACPAC with retry logic.

    .DESCRIPTION
        Invokes the SqlPackage CLI with the provided arguments. On transient failures,
        implements exponential backoff retry up to the configured maximum attempts.
        Captures both stdout and stderr for logging and diagnostics.

    .PARAMETER SqlPackagePath
        Full path to SqlPackage.exe.

    .PARAMETER Arguments
        Array of arguments to pass to SqlPackage.exe.

    .PARAMETER MaxAttempts
        Maximum number of extraction attempts (default: 3).

    .PARAMETER DelaySeconds
        Initial delay in seconds between retries (default: 10).

    .PARAMETER BackoffMultiplier
        Multiplier applied to delay after each failed attempt (default: 2).

    .OUTPUTS
        PSCustomObject with properties:
            Success    [bool]   - Whether extraction succeeded
            OutputFile [string] - Path to the generated DACPAC file
            Duration   [string] - Total elapsed time
            Attempts   [int]    - Number of attempts made
            Log        [string] - Combined stdout/stderr output from the final attempt

    .EXAMPLE
        $result = Invoke-SqlPackageExtract -SqlPackagePath "C:\tools\SqlPackage.exe" `
            -Arguments @("/Action:Extract", "/TargetFile:out.dacpac", ...) -MaxAttempts 3
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$SqlPackagePath,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [Parameter(Mandatory = $false)]
        [int]$MaxAttempts = 3,

        [Parameter(Mandatory = $false)]
        [int]$DelaySeconds = 10,

        [Parameter(Mandatory = $false)]
        [double]$BackoffMultiplier = 2.0
    )

    $overallStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $attempt = 0
    $currentDelay = $DelaySeconds
    $lastOutput = ""
    $lastExitCode = -1

    while ($attempt -lt $MaxAttempts) {
        $attempt++
        Write-Host "`n  Attempt $attempt of $MaxAttempts..." -ForegroundColor Cyan

        $stdoutFile = [System.IO.Path]::GetTempFileName()
        $stderrFile = [System.IO.Path]::GetTempFileName()

        try {
            $argumentString = $Arguments -join " "
            Write-Verbose "Executing: `"$SqlPackagePath`" $argumentString"

            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = $SqlPackagePath
            $processInfo.Arguments = $argumentString
            $processInfo.RedirectStandardOutput = $true
            $processInfo.RedirectStandardError = $true
            $processInfo.UseShellExecute = $false
            $processInfo.CreateNoWindow = $true

            $process = New-Object System.Diagnostics.Process
            $process.StartInfo = $processInfo

            $stdoutBuilder = [System.Text.StringBuilder]::new()
            $stderrBuilder = [System.Text.StringBuilder]::new()

            $stdoutHandler = {
                if (-not [string]::IsNullOrEmpty($EventArgs.Data)) {
                    [void]$Event.MessageData.AppendLine($EventArgs.Data)
                }
            }
            $stderrHandler = {
                if (-not [string]::IsNullOrEmpty($EventArgs.Data)) {
                    [void]$Event.MessageData.AppendLine($EventArgs.Data)
                }
            }

            $stdoutEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action $stdoutHandler -MessageData $stdoutBuilder
            $stderrEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action $stderrHandler -MessageData $stderrBuilder

            [void]$process.Start()
            $process.BeginOutputReadLine()
            $process.BeginErrorReadLine()
            $process.WaitForExit()

            $lastExitCode = $process.ExitCode

            Unregister-Event -SourceIdentifier $stdoutEvent.Name -ErrorAction SilentlyContinue
            Unregister-Event -SourceIdentifier $stderrEvent.Name -ErrorAction SilentlyContinue
            Remove-Job -Id $stdoutEvent.Id -Force -ErrorAction SilentlyContinue
            Remove-Job -Id $stderrEvent.Id -Force -ErrorAction SilentlyContinue

            $stdoutText = $stdoutBuilder.ToString()
            $stderrText = $stderrBuilder.ToString()
            $lastOutput = $stdoutText
            if ($stderrText) {
                $lastOutput += "`n--- STDERR ---`n$stderrText"
            }

            if ($lastExitCode -eq 0) {
                $overallStopwatch.Stop()
                Write-Host "  Extraction succeeded on attempt $attempt." -ForegroundColor Green

                return [PSCustomObject]@{
                    Success    = $true
                    OutputFile = ($Arguments | Where-Object { $_ -match '/TargetFile:"?([^"]+)"?' } | ForEach-Object {
                        if ($_ -match '/TargetFile:"?([^"]+)"?') { $Matches[1] }
                    }) | Select-Object -First 1
                    Duration   = $overallStopwatch.Elapsed.ToString("hh\:mm\:ss")
                    Attempts   = $attempt
                    Log        = $lastOutput
                }
            }

            Write-Warning "  Attempt $attempt failed with exit code $lastExitCode."
            if ($stderrText) {
                Write-Verbose "  STDERR: $stderrText"
            }
        }
        catch {
            Write-Warning "  Attempt $attempt encountered an exception: $($_.Exception.Message)"
            $lastOutput = $_.Exception.Message
        }
        finally {
            Remove-Item -Path $stdoutFile -Force -ErrorAction SilentlyContinue
            Remove-Item -Path $stderrFile -Force -ErrorAction SilentlyContinue
        }

        if ($attempt -lt $MaxAttempts) {
            Write-Host "  Waiting $currentDelay seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds $currentDelay
            $currentDelay = [math]::Ceiling($currentDelay * $BackoffMultiplier)
        }
    }

    $overallStopwatch.Stop()

    Write-Host "  All $MaxAttempts attempts exhausted. Extraction failed." -ForegroundColor Red

    return [PSCustomObject]@{
        Success    = $false
        OutputFile = $null
        Duration   = $overallStopwatch.Elapsed.ToString("hh\:mm\:ss")
        Attempts   = $attempt
        Log        = $lastOutput
    }
}

Export-ModuleMember -Function Find-SqlPackage, Build-SqlPackageArguments, Invoke-SqlPackageExtract
