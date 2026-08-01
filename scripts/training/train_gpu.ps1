param(
    [string]$OutputDir = "",
    [string]$MediaType = "photo",
    [string]$DatasetOrigin = "milliy",
    [string]$ModelName = "xabarnavis_image_0.1",
    [string]$Backbone = "efficientnet_b0",
    [int]$Epochs = 10,
    [int]$BatchSize = 32,
    [int]$NumWorkers = 2,
    [switch]$Pretrained,
    [switch]$FreezeBackbone,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$SchemaScript = Join-Path $Root "scripts\datasets\init_media_schema.py"
if (Test-Path $SchemaScript) {
    python $SchemaScript
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path "artifacts\runs" (Join-Path $MediaType (Join-Path $DatasetOrigin (Join-Path $ModelName "ai_real_gpu")))
}

$SetupModelPaths = Join-Path $Root "scripts\setup\setup_model_paths.ps1"
if (Test-Path $SetupModelPaths) {
    powershell -ExecutionPolicy Bypass -File $SetupModelPaths
}

$ArgsList = @(
    "scripts\training\train_ai_real.py",
    "--output-dir", $OutputDir,
    "--backbone", $Backbone,
    "--epochs", $Epochs,
    "--batch-size", $BatchSize,
    "--num-workers", $NumWorkers,
    "--device", "cuda",
    "--media-type", $MediaType,
    "--dataset-origin", $DatasetOrigin,
    "--model-name", $ModelName,
    "--model-version", "0.1"
)

if ($Pretrained) {
    $ArgsList += "--pretrained"
}

if ($FreezeBackbone) {
    $ArgsList += "--freeze-backbone"
}

if ($ExtraArgs) {
    $ArgsList += $ExtraArgs
}

Push-Location $Root
try {
    python @ArgsList
} finally {
    Pop-Location
}
