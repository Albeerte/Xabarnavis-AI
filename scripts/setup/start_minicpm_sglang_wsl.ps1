param(
    [int]$Port = 30000
)

$ErrorActionPreference = "Stop"

Write-Host "Starting MiniCPM-V-2_6-int4 in WSL via SGLang on port $Port..."
Write-Host "If WSL is not installed, run this first in Administrator PowerShell:"
Write-Host "  wsl --install -d Ubuntu"
Write-Host ""

wsl bash -lc @"
set -e
if [ ! -d "\$HOME/minicpm-v26" ]; then
  echo "Missing ~/minicpm-v26 environment."
  echo "Follow docs/minicpm_reasoner_setup.md to create it first."
  exit 1
fi
source "\$HOME/minicpm-v26/bin/activate"
python -m sglang.launch_server \
  --model-path openbmb/MiniCPM-V-2_6-int4 \
  --host 0.0.0.0 \
  --port $Port \
  --trust-remote-code
"@




