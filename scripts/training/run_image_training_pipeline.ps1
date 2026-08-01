param(
    [ValidateSet("fixture", "smoke", "full")]
    [string]$Stage = "smoke",
    [string]$DatasetRoot = "data\raw\xabarnavis_datasets",
    [string]$OutputDir = "artifacts\runs\image\effnet-b0-v1",
    [int]$Epochs = 20,
    [int]$BatchSize = 32,
    [ValidateSet("auto", "cpu", "cuda")]
    [string]$Device = "auto",
    [string[]]$HoldoutGenerators = @()
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Push-Location $Root
try {
    if ($Stage -eq "fixture") {
        python scripts\datasets\create_tiny_training_fixture.py
        if ($LASTEXITCODE -ne 0) { throw "Fixture creation failed." }
        $Epochs = 2
        $BatchSize = 16
        $OutputDir = "artifacts\runs\image\fixture-smoke"
    } else {
        $ManifestArgs = @(
            "scripts\datasets\build_ai_real_manifest.py",
            "--dataset-root", $DatasetRoot,
            "--balance"
        )
        if ($Stage -eq "smoke") {
            $ManifestArgs += @("--max-per-class", "1000")
            $Epochs = [Math]::Min($Epochs, 2)
        }
        if ($HoldoutGenerators.Count -gt 0) {
            $ManifestArgs += "--holdout-generators"
            $ManifestArgs += $HoldoutGenerators
        }
        python @ManifestArgs
        if ($LASTEXITCODE -ne 0) { throw "Manifest generation failed." }
    }

    $TrainArgs = @(
        "scripts\training\train_ai_real.py",
        "--dataset-root", $DatasetRoot,
        "--train-csv", (Join-Path $DatasetRoot "metadata\train.csv"),
        "--val-csv", (Join-Path $DatasetRoot "metadata\val.csv"),
        "--test-csv", (Join-Path $DatasetRoot "metadata\test.csv"),
        "--output-dir", $OutputDir,
        "--backbone", "efficientnet_b0",
        "--image-size", "224",
        "--batch-size", $BatchSize,
        "--epochs", $Epochs,
        "--lr", "0.0003",
        "--weight-decay", "0.0001",
        "--class-weights", "balanced",
        "--pretrained",
        "--device", $Device,
        "--model-name", "xabarnavis_image_0.1",
        "--model-version", "0.1",
        "--export-onnx"
    )
    python @TrainArgs
    if ($LASTEXITCODE -ne 0) { throw "Training failed." }
    Write-Host "Training complete: $OutputDir"
} finally {
    Pop-Location
}
