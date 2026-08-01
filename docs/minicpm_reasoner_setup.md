# MiniCPM-V-2.6 Int4 Reasoner Setup

This guide connects `openbmb/MiniCPM-V-2_6-int4` to Xabarnavis as the image reasoning model shown in the report detail page under `Ekspert uchun izoh`.

## Current machine status

Checked on this Windows machine:

- GPU exists: NVIDIA GeForce RTX 5070, 12 GB VRAM.
- Current Python `torch` cannot use CUDA: `torch.cuda.is_available() == False`.
- Missing MiniCPM local dependencies: `bitsandbytes`, `sentencepiece`.
- WSL is not installed.

Because of that, do not install MiniCPM into the main Xabarnavis Python environment. Run MiniCPM as a separate OpenAI-compatible server, then point Xabarnavis to it.

## Recommended Setup: WSL2 + SGLang

Run these commands in PowerShell as Administrator:

```powershell
wsl --install -d Ubuntu
```

Restart Windows if WSL asks for it. Then open Ubuntu and run:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git

python3.11 -m venv ~/minicpm-v26
source ~/minicpm-v26/bin/activate
python -m pip install --upgrade pip

pip install "torch" "torchvision" --index-url https://download.pytorch.org/whl/cu128
pip install "sglang[all]" sentencepiece pillow accelerate transformers
```

Verify CUDA inside WSL:

```bash
python - <<'PY'
import torch
print("cuda:", torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "no cuda")
PY
```

Start MiniCPM server:

```bash
source ~/minicpm-v26/bin/activate
python -m sglang.launch_server \
  --model-path openbmb/MiniCPM-V-2_6-int4 \
  --host 0.0.0.0 \
  --port 30000 \
  --trust-remote-code
```

Keep this terminal open.

## Connect Xabarnavis

In a new PowerShell terminal, start/restart the backend with:

```powershell
cd "C:\Users\User2\Documents\Xabarnavis .01"
$env:XABARNAVIS_MINICPM_REASONER_URL="http://127.0.0.1:30000/v1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then create a new image analysis report. The JSON report should include:

```json
"image_reasoning_uz": {
  "minicpm_v_2_6_int4": {
    "status": "ready",
    "reasoning_uz": "..."
  }
}
```

The report page will show that text in `Ekspert uchun izoh`.

## Quick API Test

After the SGLang server is running, test it from PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:30000/v1/chat/completions" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{
    "model": "openbmb/MiniCPM-V-2_6-int4",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe this image in Uzbek."},
          {"type": "image_url", "image_url": {"url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"}}
        ]
      }
    ],
    "max_tokens": 300
  }'
```

## Alternative: Local Transformers

Xabarnavis also supports an experimental local mode:

```powershell
$env:XABARNAVIS_ENABLE_MINICPM_LOCAL="1"
```

This is not recommended on this current Windows Python environment because CUDA torch and `bitsandbytes` are not configured. Use the separate SGLang server instead.

## Notes

- The model card says this int4 model uses lower GPU memory, about 7 GB.
- Your RTX 5070 has enough VRAM in principle, but the active Python environment must have CUDA-enabled PyTorch.
- If the server fails with CUDA or quantization errors, install/run it inside WSL2 rather than native Windows.




