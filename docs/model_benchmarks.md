# Model Benchmarks

This file is the human-readable companion to `models_registry.json`. Keep raw weights and run folders outside Git; keep model identity, task, dataset notes, and validation metrics here.

## Image Models

| Model | Task | Dataset note | Accuracy | F1 AI | AUC | Artifact path |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `image_ai_real_effnet_b0_balanced` | AI-generated vs real | Large balanced local split | 0.9685 | 0.9682 | 0.9967 | `artifacts/runs/legacy/ai_real_effnet_b0_balanced/best.pt` |
| `image_ai_real_v2_hf` | AI-generated vs real | Large local split | 0.9418 | 0.9416 | 0.9863 | `artifacts/runs/legacy/ai_real_v2_hf/best.pt` |
| `image_ai_real_xabarnavis_ready_gpu` | AI-generated vs real | 2803 ready images plus raw dataset | 0.6650 | 0.6359 | 0.7129 | `artifacts/runs/legacy/ai_real_xabarnavis_ready_gpu/best.pt` |

## Audio And Video Models

| Model | Status | Input | Notes |
| --- | --- | --- | --- |
| `audio_04_wav2vec2` | Experimental | Audio | Add exported metrics after the next evaluation run. |
| `video_naman712_spectra_ensemble` | Adapter-integrated | Video | Uses local adapters and external model weights kept outside Git. |

## Validation Rules

- Do not present local split metrics as final forensic accuracy.
- Keep an unseen-generator test set for every public benchmark claim.
- Include social-media-compressed samples in final validation.
- Track the exact dataset manifest used for every trained model.
- Store heavy artifacts in DVC, Hugging Face, Google Drive, or a private model registry.



