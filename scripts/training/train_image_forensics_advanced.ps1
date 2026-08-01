param(
    [int]$Epochs = 30,
    [int]$BatchSize = 8,
    [int]$AccumulationSteps = 4,
    [int]$ImageSize = 384,
    [ValidateSet("binary", "three_class")]
    [string]$Task = "three_class",
    [string]$MetadataDir = "metadata_3class_clean",
    [string]$OutputDir = "artifacts\runs\image\rgb-spectral-v1",
    [string]$Resume = ""
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $Root
try {
    $Arguments = @(
        "scripts\training\train_image_forensics_advanced.py",
        "--device", "cuda",
        "--epochs", $Epochs,
        "--batch-size", $BatchSize,
        "--accumulation-steps", $AccumulationSteps,
        "--image-size", $ImageSize,
        "--task", $Task,
        "--train-csv", (Join-Path "data\raw\xabarnavis_datasets" (Join-Path $MetadataDir "train.csv")),
        "--val-csv", (Join-Path "data\raw\xabarnavis_datasets" (Join-Path $MetadataDir "val.csv")),
        "--test-csv", (Join-Path "data\raw\xabarnavis_datasets" (Join-Path $MetadataDir "test.csv")),
        "--output-dir", $OutputDir
    )
    if (-not [string]::IsNullOrWhiteSpace($Resume)) {
        $Arguments += @("--resume", $Resume)
    }
    python @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Advanced training failed." }
} finally {
    Pop-Location
}
