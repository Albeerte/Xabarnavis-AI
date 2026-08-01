param(
    [ValidateSet("community_forensics", "community_forensics_eval", "hf_ai_mix", "all")]
    [string]$Dataset = "community_forensics",
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$DataRoot = Join-Path $Root "data\raw\xabarnavis_datasets\_incoming"

$Registry = @{
    community_forensics = @{
        Repo = "OwensLab/CommunityForensics"
        Target = "community_forensics"
        Note = "2.7M generated images from 4,803 generators. Verify every component license."
    }
    community_forensics_eval = @{
        Repo = "OwensLab/CommunityForensics-Eval"
        Target = "community_forensics_eval"
        Note = "Evaluation only; official page states non-commercial research/education use."
    }
    hf_ai_mix = @{
        Repo = "julienlucas/midjourney-dalle-sd-nanobananapro-dataset"
        Target = "hf_midjourney_dalle_sd_nano_new"
        Note = "AI/real mix. Audit label schema and license before organization."
    }
}

$Selected = if ($Dataset -eq "all") { @("community_forensics", "community_forensics_eval", "hf_ai_mix") } else { @($Dataset) }
New-Item -ItemType Directory -Force -Path $DataRoot | Out-Null

foreach ($Key in $Selected) {
    $Spec = $Registry[$Key]
    $Target = Join-Path $DataRoot $Spec.Target
    Write-Host ""
    Write-Host "Dataset: $Key"
    Write-Host "Repository: $($Spec.Repo)"
    Write-Host "Target: $Target"
    Write-Host "License note: $($Spec.Note)"

    if (-not $Execute) {
        Write-Host "DRY RUN - no files will be downloaded."
        hf download "hf://datasets/$($Spec.Repo)" --dry-run
        if ($LASTEXITCODE -ne 0) { throw "Hugging Face dry-run failed for $Key" }
        continue
    }

    Write-Host "DOWNLOAD ENABLED"
    hf download "hf://datasets/$($Spec.Repo)" --local-dir $Target
    if ($LASTEXITCODE -ne 0) { throw "Hugging Face download failed for $Key" }
    Write-Host "Downloaded: $Target"
}

if (-not $Execute) {
    Write-Host ""
    Write-Host "Review size and license, then repeat with -Execute to download."
}
