$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ModelPaths = @(
    $Root.Path,
    (Join-Path $Root.Path "artifacts\models\external"),
    (Join-Path $Root.Path "artifacts\models\external\audio"),
    (Join-Path $Root.Path "artifacts\models\external\photo"),
    (Join-Path $Root.Path "artifacts\models\external\video"),
    (Join-Path $Root.Path "artifacts\models\external\text"),
    (Join-Path $Root.Path "artifacts\models\external\photo\clip_synthetic"),
    (Join-Path $Root.Path "artifacts\models\external\photo\cnnspot"),
    (Join-Path $Root.Path "artifacts\models\external\photo\fatformer"),
    (Join-Path $Root.Path "artifacts\models\external\photo\safe"),
    (Join-Path $Root.Path "artifacts\models\external\photo\dm_image_detection"),
    (Join-Path $Root.Path "artifacts\models\external\photo\zed"),
    (Join-Path $Root.Path "artifacts\models\external\photo\mantranet_pytorch"),
    (Join-Path $Root.Path "artifacts\models\external\audio\jabberjay"),
    (Join-Path $Root.Path "artifacts\models\external\audio\deepfake_voice_detection_public")
)

$Existing = [Environment]::GetEnvironmentVariable("PYTHONPATH", "User")
$Parts = @()
if ($Existing) {
    $Parts += $Existing -split [IO.Path]::PathSeparator
}

foreach ($Path in $ModelPaths) {
    if ((Test-Path -LiteralPath $Path) -and ($Parts -notcontains $Path)) {
        $Parts += $Path
    }
}

$NewValue = ($Parts | Where-Object { $_ }) -join [IO.Path]::PathSeparator
[Environment]::SetEnvironmentVariable("PYTHONPATH", $NewValue, "User")
$env:PYTHONPATH = $NewValue

Write-Host "User PYTHONPATH updated for Xabarnavis models:"
$Parts | Where-Object { $_ -like "*Xabarnavis*" } | ForEach-Object { Write-Host " - $_" }





