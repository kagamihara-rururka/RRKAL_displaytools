param(
    [switch]$ContractOnly
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$RepoRoot = Split-Path -Parent $PSScriptRoot

function Write-JsonObject {
    param([object]$Value)
    $Value | ConvertTo-Json -Depth 40
}

if ($ContractOnly) {
    Write-JsonObject ([ordered]@{
        schema = "rrkal_displaytools.cross_machine_review_readiness_check.v1"
        output_schema = "rrkal_displaytools.cross_machine_review_readiness_check_result.v1"
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_cross_machine_review_readiness.ps1"
        writes = @()
        launches_gui = $false
        requires_taichi = $false
        checks = @(
            "launch_packet_cross_machine_ready",
            "repo_public_main",
            "setup_smoke_handoff_commands_present",
            "review_packet_ready",
            "uiux_readiness_pass",
            "pre_decoupling_readiness_contract_available",
            "qt_first_boundary",
            "rrkal_boundary_preserved"
        )
        boundary = @(
            "read-only no-GUI readiness check",
            "does not launch Qt or Taichi",
            "does not perform RRKAL discovery/download/import/cache governance",
            "safe before the formal 07:00 decoupling gate"
        )
    })
    exit 0
}

Push-Location $RepoRoot
try {
    function Invoke-JsonPowerShell {
        param(
            [Parameter(Mandatory = $true)][string]$ScriptPath,
            [string[]]$Arguments = @()
        )

        $lastOutput = ""
        $lastError = $null
        for ($attempt = 1; $attempt -le 4; $attempt += 1) {
            try {
                $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @Arguments
                $lastOutput = ($output | Out-String).Trim()
                if ($LASTEXITCODE -ne 0) {
                    throw "exit code $LASTEXITCODE"
                }
                return $lastOutput | ConvertFrom-Json
            } catch {
                $lastError = $_
                Start-Sleep -Milliseconds (150 * $attempt)
            }
        }
        throw "Unable to read JSON from $ScriptPath $($Arguments -join ' '): $lastError`n$lastOutput"
    }

    function Invoke-JsonPython {
        param([string[]]$Arguments)

        $lastOutput = ""
        $lastError = $null
        for ($attempt = 1; $attempt -le 4; $attempt += 1) {
            try {
                $output = & py -3 @Arguments
                $lastOutput = ($output | Out-String).Trim()
                if ($LASTEXITCODE -ne 0) {
                    throw "exit code $LASTEXITCODE"
                }
                return $lastOutput | ConvertFrom-Json
            } catch {
                $lastError = $_
                Start-Sleep -Milliseconds (150 * $attempt)
            }
        }
        throw "Unable to read JSON from py -3 $($Arguments -join ' '): $lastError`n$lastOutput"
    }

    function Add-ReadinessCheck {
        param(
            [Parameter(Mandatory = $true)][string]$Id,
            [Parameter(Mandatory = $true)][bool]$Passed,
            [Parameter(Mandatory = $true)][object]$Evidence
        )

        $script:checks += [ordered]@{
            id = $Id
            status = $(if ($Passed) { "pass" } else { "fail" })
            evidence = $Evidence
        }
    }

    function To-JsonText {
        param([object]$Value)
        if ($null -eq $Value) {
            return ""
        }
        return ($Value | ConvertTo-Json -Depth 30 -Compress)
    }

    $launchPacket = Invoke-JsonPython @("scripts\export_launch_packet.py", "--template", "fast_synthetic")
    $reviewPacket = Invoke-JsonPowerShell (Join-Path $RepoRoot "scripts\export_visual_contract_review_packet.ps1")
    $uiuxReadiness = Invoke-JsonPowerShell (Join-Path $RepoRoot "scripts\check_uiux_closure_readiness.ps1")
    $preDecouplingContract = Invoke-JsonPowerShell (Join-Path $RepoRoot "scripts\check_pre_decoupling_readiness.ps1") @("-ContractOnly")

    $crossMachine = $launchPacket.cross_machine_clone_readiness
    $profileReadiness = $launchPacket.profile_launch_readiness
    $profileUi = $launchPacket.profile_launch_readiness_ui
    $firstRunText = To-JsonText $crossMachine.first_run_order
    $requiredCommandText = To-JsonText $crossMachine.required_commands
    $reviewText = To-JsonText $reviewPacket

    $script:checks = @()

    Add-ReadinessCheck "launch_packet_cross_machine_ready" (
        $crossMachine.schema -eq "rrkal_displaytools.cross_machine_clone_readiness.v1" -and
        $crossMachine.status -eq "ready" -and
        $profileReadiness.readiness -eq "ready" -and
        [int]$profileReadiness.ready_check_count -eq [int]$profileReadiness.check_count -and
        $profileUi.cross_machine_commands_visible -eq $true
    ) ([ordered]@{
        clone_schema = $crossMachine.schema
        clone_status = $crossMachine.status
        profile_readiness = $profileReadiness.readiness
        profile_ready_check_count = $profileReadiness.ready_check_count
        profile_check_count = $profileReadiness.check_count
        cross_machine_commands_visible = $profileUi.cross_machine_commands_visible
    })

    Add-ReadinessCheck "repo_public_main" (
        $crossMachine.repo_url -eq "https://github.com/Kagamihara-Ruruka/RRKAL_displaytools.git" -and
        $crossMachine.repo_visibility -eq "public" -and
        $crossMachine.default_branch -eq "main"
    ) ([ordered]@{
        repo_url = $crossMachine.repo_url
        repo_visibility = $crossMachine.repo_visibility
        default_branch = $crossMachine.default_branch
    })

    Add-ReadinessCheck "setup_smoke_handoff_commands_present" (
        $requiredCommandText -match "scripts/setup_windows.ps1" -and
        $requiredCommandText -match "scripts/smoke.ps1" -and
        $requiredCommandText -match "scripts/run_qt_panel.ps1" -and
        $requiredCommandText -match "scripts/inspect_handoff.ps1" -and
        $firstRunText -match "setup" -and
        $firstRunText -match "smoke" -and
        $firstRunText -match "inspect_handoff" -and
        $firstRunText -match "run_qt_panel" -and
        $crossMachine.first_run_smoke_command -match "scripts[/\\]smoke.ps1" -and
        $crossMachine.first_run_handoff_command -match "scripts[/\\]inspect_handoff.ps1"
    ) ([ordered]@{
        required_commands = $crossMachine.required_commands
        first_run_order = $crossMachine.first_run_order
        first_run_smoke_command = $crossMachine.first_run_smoke_command
        first_run_handoff_command = $crossMachine.first_run_handoff_command
    })

    $reviewPacketPortable = $true
    if ($reviewPacket.PSObject.Properties.Name -contains "portable") {
        $reviewPacketPortable = ($reviewPacket.portable -eq $true)
    }

    Add-ReadinessCheck "review_packet_ready" (
        $reviewPacket.schema -eq "rrkal_displaytools.visual_contract_review_packet.v1" -and
        $reviewPacket.inspector_index_schema -eq "rrkal_displaytools.visual_contract_inspector_index.v1" -and
        $reviewPacketPortable -and
        $reviewText -match "check_uiux_closure_readiness.ps1" -and
        $reviewText -match "check_pre_decoupling_readiness.ps1"
    ) ([ordered]@{
        schema = $reviewPacket.schema
        inspector_index_schema = $reviewPacket.inspector_index_schema
        portable = $reviewPacketPortable
        no_gui_export_command = $reviewPacket.no_gui_export_command
    })

    Add-ReadinessCheck "uiux_readiness_pass" (
        $uiuxReadiness.schema -eq "rrkal_displaytools.uiux_closure_readiness_check_result.v1" -and
        $uiuxReadiness.status -eq "pass"
    ) ([ordered]@{
        schema = $uiuxReadiness.schema
        status = $uiuxReadiness.status
        ready_for_backend_closure = $uiuxReadiness.ready_for_backend_closure
    })

    Add-ReadinessCheck "pre_decoupling_readiness_contract_available" (
        $preDecouplingContract.schema -eq "rrkal_displaytools.pre_decoupling_readiness_check.v1" -and
        $preDecouplingContract.output_schema -eq "rrkal_displaytools.pre_decoupling_readiness_check_result.v1" -and
        $preDecouplingContract.command -match "check_pre_decoupling_readiness.ps1"
    ) ([ordered]@{
        schema = $preDecouplingContract.schema
        output_schema = $preDecouplingContract.output_schema
        command = $preDecouplingContract.command
    })

    Add-ReadinessCheck "qt_first_boundary" (
        $crossMachine.qt_first -eq $true -and
        $crossMachine.tk_primary_ui_allowed -eq $false
    ) ([ordered]@{
        qt_first = $crossMachine.qt_first
        tk_primary_ui_allowed = $crossMachine.tk_primary_ui_allowed
    })

    Add-ReadinessCheck "rrkal_boundary_preserved" (
        $reviewText -match "discovery" -and
        $reviewText -match "download" -and
        $reviewText -match "import" -and
        $reviewText -match "cache"
    ) ([ordered]@{
        displaytools_role = "visualization and reviewer readiness only"
        rrkal_governance = "discovery/download/import/cache remains outside displaytools"
    })

    $failed = @($script:checks | Where-Object { $_.status -ne "pass" } | ForEach-Object { $_.id })
    $status = $(if ($failed.Count -eq 0) { "pass" } else { "fail" })

    $result = [ordered]@{
        schema = "rrkal_displaytools.cross_machine_review_readiness_check_result.v1"
        status = $status
        ready_for_clone_review = ($status -eq "pass")
        repo_url = $crossMachine.repo_url
        default_branch = $crossMachine.default_branch
        first_run_order = $crossMachine.first_run_order
        next_commands = @(
            "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_windows.ps1",
            "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1",
            "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\inspect_handoff.ps1",
            "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_qt_panel.ps1"
        )
        checks = $script:checks
        failed_checks = $failed
    }

    Write-JsonObject $result
    if ($status -ne "pass") {
        exit 1
    }
} finally {
    Pop-Location
}
