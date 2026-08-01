from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from app.services.fusion import FusionResult
from app.services.metadata import MetadataSignals
from app.services.signal_analysis import ImageSignalScores


MODEL_ID = "nvidia/cosmos3-nano-reasoner"
MINICPM_MODEL_ID = "openbmb/MiniCPM-V-2_6-int4"

SIGN_TRANSLATIONS = {
    "camera model metadata is present": "Kamera modeli metadatada bor, bu real kamera manbasi ehtimolini oshiradi.",
    "missing EXIF metadata": "EXIF metadata yo'q; bu ijtimoiy tarmoq siqishi, tahrirlash yoki generatsiya jarayoni bilan bog'liq bo'lishi mumkin.",
    "abnormal frequency-domain artifacts": "Chastota spektrida odatiy bo'lmagan artefaktlar topildi.",
    "unusually uniform texture statistics": "Tekstura statistikasi haddan tashqari bir xil ko'rinadi.",
    "localized noise inconsistency": "Rasmning ayrim joylarida shovqin darajasi bir-biriga mos kelmaydi.",
    "edge and compression inconsistency": "Qirralar va siqilish izlarida nomuvofiqlik bor.",
    "strong JPEG block-boundary artifacts": "JPEG blok chegaralari kuchli ko'rinadi.",
    "elevated error-level-analysis residuals": "ELA qoldiqlari yuqori; bu tahrirlangan joylar bo'lishi mumkinligini ko'rsatadi.",
    "combined indicators lean toward AI generation": "Umumiy indikatorlar AI generatsiya ehtimoliga og'adi.",
    "combined indicators lean toward image editing": "Umumiy indikatorlar rasm tahrirlangan bo'lishi ehtimoliga og'adi.",
    "combined indicators are consistent with a real camera photo": "Umumiy indikatorlar real kamera fotosiga mos keladi.",
    "no strong forensic indicator exceeded the MVP threshold": "MVP chegarasidan yuqori kuchli forensic indikator topilmadi.",
    "Xabarnavis 0.5 is the primary AI-vs-human model in final fusion": "Yakuniy fusionda Xabarnavis 0.5 asosiy AI-vs-human modeli sifatida ishlatildi.",
    "Final decision is based only on Xabarnavis 0.5 (Ateeqq/ai-vs-human-image-detector)": "Yakuniy qaror faqat Xabarnavis 0.5 modeli natijasiga tayangan.",
    "Manipulation and forensic signals are reported as supporting evidence only": "Manipulyatsiya va forensic signallar yordamchi dalil sifatida berilgan.",
}


def build_image_reasoning_uz(
    *,
    metadata: MetadataSignals,
    signals: ImageSignalScores,
    fusion: FusionResult,
    model_results: list[dict[str, Any]] | None,
    evidence_image_path: Path | None,
    image_description: str | None,
) -> dict[str, Any]:
    translated_signs = [translate_sign(reason) for reason in fusion.reasons]
    score_lines = _score_lines(fusion)
    model_lines = _model_lines(model_results or [])
    local_reasoning = [
        f"Yakuniy xulosa: {translate_verdict(fusion.final_verdict)}. Ishonch darajasi: {translate_confidence(fusion.confidence)}.",
        *score_lines,
        _metadata_reason(metadata),
        _signal_reason(signals),
        *model_lines,
        "Bu xulosa mustaqil sud hukmi emas; inson eksperti rasm konteksti, manba tarixi va asl faylni ham tekshirishi kerak.",
    ]
    cosmos = run_cosmos_reasoning(evidence_image_path, image_description)
    minicpm = run_minicpm_reasoning(evidence_image_path, image_description, fusion, metadata, signals, model_results or [])
    return {
        "language": "uz",
        "summary_uz": " ".join(item for item in local_reasoning if item),
        "reasoning_steps_uz": [item for item in local_reasoning if item],
        "detected_signs_uz": translated_signs,
        "cosmos3_nano_reasoner": cosmos,
        "minicpm_v_2_6_int4": minicpm,
    }


def translate_sign(reason: str) -> str:
    if reason in SIGN_TRANSLATIONS:
        return SIGN_TRANSLATIONS[reason]
    if reason.startswith("software metadata detected:"):
        software = reason.split(":", 1)[1].strip()
        return f"Metadata ichida dastur izi topildi: {software}."
    return reason


def translate_verdict(verdict: str) -> str:
    mapping = {
        "Likely real camera photo": "ehtimol real kamera fotosi",
        "Highly likely AI-generated": "AI orqali yaratilgan bo'lish ehtimoli yuqori",
        "Possibly AI-generated": "AI orqali yaratilgan bo'lishi mumkin",
        "Likely manipulated or edited": "tahrirlangan yoki manipulyatsiya qilingan bo'lishi mumkin",
    }
    return mapping.get(verdict, verdict)


def translate_confidence(confidence: str) -> str:
    return {"High": "yuqori", "Medium": "o'rta", "Low": "past"}.get(confidence, confidence)


def _score_lines(fusion: FusionResult) -> list[str]:
    scores = fusion.scores
    return [
        (
            "Scorelar: real "
            f"{_percent(scores.get('real_score'))}, AI {_percent(scores.get('ai_score'))}, "
            f"tahrirlash/manipulyatsiya {_percent(scores.get('manipulated_score'))}."
        )
    ]


def _metadata_reason(metadata: MetadataSignals) -> str:
    if metadata.has_camera_model:
        return "Kamera modeli borligi rasm real kamera qurilmasidan chiqqan bo'lishi mumkinligini qo'llab-quvvatlaydi."
    if metadata.software_tag:
        return f"Software metadata ({metadata.software_tag}) tahrirlash yoki eksport jarayonidan dalolat berishi mumkin."
    if not metadata.has_exif:
        return "EXIF yo'qligi yolg'iz o'zi fake dalil emas, lekin manba va platforma tarixini tekshirish zarurligini bildiradi."
    return "Metadata bo'yicha keskin nomuvofiqlik ko'rinmadi."


def _signal_reason(signals: ImageSignalScores) -> str:
    strongest = max(
        [
            ("chastota anomaliyasi", signals.frequency_anomaly_score),
            ("tekstura bir xilligi", signals.texture_uniformity_score),
            ("shovqin nomuvofiqligi", signals.noise_inconsistency_score),
            ("qirra/siqilish nomuvofiqligi", signals.edge_inconsistency_score),
            ("JPEG blok izlari", signals.jpeg_blocking_score),
            ("ELA qoldiqlari", signals.ela_anomaly_score),
        ],
        key=lambda item: item[1],
    )
    return f"Signal tahlilida eng kuchli indikator: {strongest[0]} ({_percent(strongest[1])})."


def _model_lines(model_results: list[dict[str, Any]]) -> list[str]:
    ready = [item for item in model_results if item.get("status") == "ready"]
    if not ready:
        return ["Tayyor tashqi model natijasi yo'q; xulosa metadata va signal tahliliga ko'proq tayangan."]
    best = max(
        ready,
        key=lambda item: max(
            float(item.get("real_score") or 0),
            float(item.get("ai_score") or 0),
            float(item.get("manipulated_score") or 0),
        ),
    )
    return [
        (
            f"Eng aniq model signali: {best.get('name') or best.get('model_id')} -> "
            f"{best.get('verdict') or 'natija bor'}, AI {_percent(best.get('ai_score'))}, "
            f"real {_percent(best.get('real_score'))}."
        )
    ]


def run_cosmos_reasoning(evidence_image_path: Path | None, image_description: str | None) -> dict[str, Any]:
    base_url = os.getenv("XABARNAVIS_COSMOS_REASONER_URL", "").strip().rstrip("/")
    if not base_url:
        return {
            "status": "not_configured",
            "model": MODEL_ID,
            "note_uz": "Cosmos3 Nano Reasoner ulanmagan. Yoqish uchun XABARNAVIS_COSMOS_REASONER_URL=http://127.0.0.1:8000/v1 sozlang.",
        }


def run_minicpm_reasoning(
    evidence_image_path: Path | None,
    image_description: str | None,
    fusion: FusionResult,
    metadata: MetadataSignals,
    signals: ImageSignalScores,
    model_results: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = _minicpm_prompt(image_description, fusion, metadata, signals, model_results)
    server_result = _run_minicpm_server(evidence_image_path, prompt)
    if server_result is not None:
        return server_result

    if os.getenv("XABARNAVIS_ENABLE_MINICPM_LOCAL", "").lower() in {"1", "true", "yes"}:
        return _run_minicpm_local(evidence_image_path, prompt)

    return {
        "status": "not_configured",
        "model": MINICPM_MODEL_ID,
        "source": "https://huggingface.co/openbmb/MiniCPM-V-2_6-int4",
        "note_uz": (
            "MiniCPM-V-2_6-int4 reasoner hali ulanmagan. Haqiqiy natijani olish uchun "
            "XABARNAVIS_MINICPM_REASONER_URL=http://127.0.0.1:30000/v1 kabi OpenAI-compatible "
            "server sozlang yoki XABARNAVIS_ENABLE_MINICPM_LOCAL=1 bilan lokal yuklashni yoqing."
        ),
        "fallback_reasoning_uz": " ".join(
            [
                f"Yakuniy xulosa: {translate_verdict(fusion.final_verdict)}.",
                _score_lines(fusion)[0],
                _metadata_reason(metadata),
                _signal_reason(signals),
            ]
        ),
    }


def _run_minicpm_server(evidence_image_path: Path | None, prompt: str) -> dict[str, Any] | None:
    base_url = os.getenv("XABARNAVIS_MINICPM_REASONER_URL", "").strip().rstrip("/")
    if not base_url:
        return None
    if evidence_image_path is None or not evidence_image_path.is_file():
        return {"status": "skipped", "model": MINICPM_MODEL_ID, "note_uz": "Rasm fayli topilmadi."}

    try:
        image_url = _image_data_url(evidence_image_path)
        model_id = os.getenv("XABARNAVIS_MINICPM_MODEL_ID", MINICPM_MODEL_ID)
        body = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_tokens": int(os.getenv("XABARNAVIS_MINICPM_MAX_TOKENS", "900")),
            "stream": False,
        }
        request = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.getenv('XABARNAVIS_MINICPM_API_KEY', 'not-used')}"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=float(os.getenv("XABARNAVIS_MINICPM_TIMEOUT", "90"))) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "status": "ready",
            "model": model_id,
            "source": "openai_compatible_server",
            "reasoning_uz": text,
            "raw": payload,
        }
    except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
        return {
            "status": "error",
            "model": MINICPM_MODEL_ID,
            "source": "openai_compatible_server",
            "error": str(exc),
            "note_uz": "MiniCPM serveriga ulanish yoki javobni o'qish vaqtida xatolik bo'ldi.",
        }


def _run_minicpm_local(evidence_image_path: Path | None, prompt: str) -> dict[str, Any]:
    if evidence_image_path is None or not evidence_image_path.is_file():
        return {"status": "skipped", "model": MINICPM_MODEL_ID, "note_uz": "Rasm fayli topilmadi."}
    try:
        _disable_torchaudio_for_image_only_transformers()
        import torch
        from PIL import Image
        from transformers import AutoModel, AutoTokenizer

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModel.from_pretrained(MINICPM_MODEL_ID, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(MINICPM_MODEL_ID, trust_remote_code=True)
        if device == "cuda":
            model = model.to(device)
        model.eval()
        with Image.open(evidence_image_path) as image:
            rgb_image = image.convert("RGB")
            msgs = [{"role": "user", "content": [rgb_image, prompt]}]
            text = model.chat(image=None, msgs=msgs, tokenizer=tokenizer)
        return {
            "status": "ready",
            "model": MINICPM_MODEL_ID,
            "source": "local_transformers",
            "device": device,
            "reasoning_uz": str(text),
        }
    except Exception as exc:
        return {
            "status": "error",
            "model": MINICPM_MODEL_ID,
            "source": "local_transformers",
            "error": str(exc),
            "note_uz": (
                "MiniCPM-V-2_6-int4 lokal ishga tushmadi. Model card bo'yicha int4 inference odatda "
                "NVIDIA GPU, bitsandbytes, sentencepiece va trust_remote_code talab qiladi."
            ),
        }


def _minicpm_prompt(
    image_description: str | None,
    fusion: FusionResult,
    metadata: MetadataSignals,
    signals: ImageSignalScores,
    model_results: list[dict[str, Any]],
) -> str:
    compact_models = []
    for item in model_results[:8]:
        compact_models.append(
            {
                "model": item.get("name") or item.get("model_id"),
                "status": item.get("status"),
                "verdict": item.get("verdict"),
                "ai_score": item.get("ai_score"),
                "real_score": item.get("real_score"),
            }
        )
    return (
        "Siz MiniCPM-V-2.6 int4 multimodal reasoner sifatida Xabarnavis reporti uchun o'zbek tilida ekspert izoh yozasiz. "
        "Rasmga qarab sahna, AI-generatsiya ehtimoli, real kamera belgisi, tahrir/manipulyatsiya ehtimoli va tekshirish tavsiyalarini qisqa, aniq yozing. "
        "Sud hukmi kabi qat'iy aytmang; ehtimollik va texnik dalillar sifatida ifodalang.\n\n"
        f"Tergovchi izohi: {image_description or 'berilmagan'}\n"
        f"Final verdict: {fusion.final_verdict}, confidence: {fusion.confidence}, scores: {fusion.scores}\n"
        f"Metadata: has_exif={metadata.has_exif}, camera={metadata.camera_make} {metadata.camera_model}, software={metadata.software_tag}, gps={metadata.has_gps}\n"
        f"Signal scores: {signals.to_dict()}\n"
        f"Model results: {json.dumps(compact_models, ensure_ascii=False)}\n\n"
        "Javob formati:\n"
        "1) MiniCPM-V reasoning xulosasi (2-4 gap)\n"
        "2) Muhim dalillar (3-5 bullet)\n"
        "3) Tavsiya (1-3 bullet)"
    )


def _disable_torchaudio_for_image_only_transformers() -> None:
    try:
        import transformers.utils as transformers_utils
        import transformers.utils.import_utils as import_utils

        transformers_utils.is_torchaudio_available = lambda: False
        import_utils.is_torchaudio_available = lambda: False
    except Exception:
        pass
    if evidence_image_path is None or not evidence_image_path.is_file():
        return {"status": "skipped", "model": MODEL_ID, "note_uz": "Rasm fayli topilmadi."}

    try:
        image_url = _image_data_url(evidence_image_path)
        prompt = (
            "Rasmni forensic nuqtai nazardan o'zbek tilida tahlil qiling. "
            "Sahnani qisqa tasvirlang, AI generatsiya yoki tahrirlash ehtimoliga oid belgilarni sanang, "
            "fizik/mantiqiy nomuvofiqliklarni ayting va yakunda ehtiyotkor xulosa bering. "
            f"Tergovchi izohi: {image_description or 'berilmagan'}"
        )
        body = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            "max_tokens": 1024,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": "Bearer not-used"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=float(os.getenv("XABARNAVIS_COSMOS_TIMEOUT", "45"))) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"status": "ready", "model": MODEL_ID, "reasoning_uz": text, "raw": payload}
    except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, ValueError) as exc:
        return {
            "status": "error",
            "model": MODEL_ID,
            "error": str(exc),
            "note_uz": "Cosmos3 serveriga ulanish yoki javobni o'qish vaqtida xatolik bo'ldi.",
        }


def _image_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _percent(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "n/a"





