"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { BarChart3, CheckCircle, FileAudio, Loader2, Mic, Shield, Speaker, Upload, Waves, X } from "lucide-react";

const STEPS = [
  "Audio fayl qabul qilindi",
  "SHA-256 dalil hash hisoblanmoqda",
  "Xabarnavis Audio 0.5 modeli AI ovoz izlarini tekshirmoqda",
  "Spectra-AASIST3, RawGAT-ST, Jabberjay va Audio 0.2 qo'shimcha forensic signal bermoqda",
  "Spoof / bonafide score chiqarilmoqda",
  "Hisobot bazaga saqlanmoqda",
];

const API_BASE_URL = process.env.NEXT_PUBLIC_XABARNAVIS_API_URL || "http://127.0.0.1:8000";

type AudioResult = {
  case_id: number;
  final_verdict: string;
  confidence: string;
  scores: Record<string, number>;
};

export default function AudioAnalyzerPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(-1);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AudioResult | null>(null);

  function chooseFile(nextFile: File) {
    if (!nextFile.type.startsWith("audio/")) {
      setError("Faqat audio fayl yuklang: WAV, FLAC, MP3, M4A yoki OGG.");
      return;
    }
    if (nextFile.size > 100 * 1024 * 1024) {
      setError("Audio fayl 100 MBdan katta. Iltimos, faylni qisqartirib yoki siqib qayta yuklang.");
      return;
    }
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(nextFile);
    setPreviewUrl(URL.createObjectURL(nextFile));
    setResult(null);
    setError("");
  }

  async function analyze() {
    if (!file) return;
    setBusy(true);
    setError("");
    setResult(null);

    const progress = (async () => {
      for (let i = 0; i < STEPS.length; i++) {
        setStep(i);
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    })();

    try {
      const form = new FormData();
      form.set("file", file);
      const response = await fetch(`${API_BASE_URL}/api/analyze/audio`, {
        method: "POST",
        body: form,
        credentials: "include",
      });
      await progress;
      if (!response.ok) throw new Error(await readErrorMessage(response));
      const data = await response.json();
      setResult(data);
      router.push(`/dashboard/reports/${data.case_id}`);
    } catch (exc) {
      await progress;
      setError(exc instanceof Error ? exc.message : "Audio tahlil vaqtida xatolik yuz berdi.");
    } finally {
      setStep(-1);
      setBusy(false);
    }
  }

  function reset() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(null);
    setPreviewUrl("");
    setResult(null);
    setError("");
    setStep(-1);
    setBusy(false);
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 lg:p-6">
      <div>
        <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-green-500">Dashboard / Audio tahlili</p>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-black tracking-tight theme-text-primary sm:text-3xl">Audio Tahlili</h1>
          <span className="rounded-md border border-green-400/30 bg-green-400/10 px-2 py-1 text-[9px] font-black tracking-widest text-green-400">
            JONLI
          </span>
        </div>
      </div>

      <div className="rounded-3xl border border-green-300/30 bg-[radial-gradient(circle_at_0%_0%,rgba(34,197,94,0.16),transparent_18rem),var(--bg-card)] p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="grid h-14 w-14 place-items-center rounded-2xl border border-green-400/30 bg-green-400/10 text-green-400">
              <Mic className="h-7 w-7" />
            </div>
            <div>
              <p className="text-[11px] font-black uppercase tracking-[0.22em] text-green-500">Asosiy audio modeli</p>
              <h2 className="mt-1 text-3xl font-black tracking-tight theme-text-primary sm:text-4xl">Xabarnavis Audio 0.5</h2>
            </div>
          </div>
          <div className="rounded-2xl border theme-border bg-white/[0.04] px-4 py-3 text-sm font-bold theme-text-secondary">
            Hemgg wav2vec2 AI voice detector
          </div>
        </div>
        <p className="mt-4 text-sm font-semibold leading-6 theme-text-secondary">
          Xabarnavis Audio 0.5 Hemgg/Deepfake-audio-detection modeli orqali AI ovoz va human voice ehtimolini hisoblaydi. Spectra-AASIST3, RawGAT-ST, Jabberjay va Audio 0.2 natijalari qo'shimcha segment, spektral va spoof dalil sifatida hisobotga qo'shiladi.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <section className="card overflow-hidden">
          {!file ? (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="drop-zone flex min-h-[360px] w-full flex-col items-center justify-center p-10 text-center"
            >
              <div className="mb-6 grid h-20 w-20 place-items-center rounded-3xl border border-green-400/30 bg-green-400/10">
                <Upload className="h-10 w-10 text-green-400" />
              </div>
              <h3 className="text-lg font-black theme-text-primary">Audio faylni yuklang</h3>
              <p className="mt-3 max-w-sm text-sm leading-6 theme-text-secondary">
                WAV, FLAC, MP3, M4A, OGG formatlari. Xabarnavis Audio 0.5 audio faylni 16 kHz signalga moslab AI voice izlarini tekshiradi.
              </p>
              <input
                ref={inputRef}
                hidden
                type="file"
                accept="audio/*"
                onChange={(event) => event.target.files?.[0] && chooseFile(event.target.files[0])}
              />
            </button>
          ) : (
            <div>
              <div className="flex min-h-[260px] flex-col items-center justify-center gap-5 bg-[var(--bg-secondary)] p-6">
                <div className="grid h-20 w-20 place-items-center rounded-3xl border border-green-400/30 bg-green-400/10">
                  <FileAudio className="h-10 w-10 text-green-400" />
                </div>
                <audio controls src={previewUrl} className="w-full max-w-xl" />
              </div>
              <div className="flex flex-col gap-4 border-t theme-border p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <p className="truncate text-sm font-black theme-text-primary">{file.name}</p>
                  <p className="mt-1 text-xs theme-text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB | {file.type || "audio"}</p>
                </div>
                <div className="flex gap-2">
                  <button type="button" className="rounded-xl border theme-border p-3 theme-text-secondary hover:text-red-400" onClick={reset} disabled={busy}>
                    <X className="h-4 w-4" />
                  </button>
                  <button type="button" className="btn-primary" onClick={analyze} disabled={busy}>
                    {busy ? "Tekshirilmoqda..." : "Audio tahlilni boshlash"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>

        <aside className="space-y-4">
          {busy && (
            <div className="card space-y-4 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-[0.18em] text-green-400">Xabarnavis Audio 0.5 ishlamoqda</p>
                  <h3 className="mt-1 text-xl font-black theme-text-primary">Audio spoof tekshiruvi</h3>
                </div>
                <Loader2 className="h-5 w-5 animate-spin text-green-400" />
              </div>
              <div className="space-y-3">
                {STEPS.map((item, index) => (
                  <div key={item} className={`flex items-center gap-3 text-xs font-bold ${index <= step ? "theme-text-primary" : "theme-text-muted opacity-50"}`}>
                    {index < step ? <CheckCircle className="h-4 w-4 text-green-500" /> : <span className="h-4 w-4 rounded-full border theme-border" />}
                    {item}
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-2xl border border-red-400/25 bg-red-500/10 p-4 text-sm font-semibold text-red-500">
              {error}
            </div>
          )}

          {result && (
            <div className="card p-5">
              <p className="text-xs font-black uppercase tracking-widest theme-text-muted">Natija</p>
              <h3 className="mt-2 text-xl font-black theme-text-primary">{result.final_verdict}</h3>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Score label="Real ovoz" value={result.scores.real_voice_score} />
                <Score label="AI/Spoof" value={result.scores.ai_voice_score} />
              </div>
            </div>
          )}

          <div className="grid gap-3">
            {[
              { icon: Waves, label: "Spektral tahlil", desc: "Frekans anomaliyalari" },
              { icon: Shield, label: "Spoof detection", desc: "Bonafide yoki spoof qarori" },
              { icon: BarChart3, label: "Score breakdown", desc: "Model confidence va label score" },
              { icon: Speaker, label: "Report", desc: "Bazaga yozilgan legal hisobot" },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                <item.icon className="mb-3 h-5 w-5 text-green-400" />
                <p className="text-sm font-black theme-text-primary">{item.label}</p>
                <p className="mt-1 text-xs theme-text-secondary">{item.desc}</p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}

async function readErrorMessage(response: Response) {
  const text = await response.text();
  try {
    const data = JSON.parse(text);
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((item: { msg?: string; message?: string } | string) => {
        if (typeof item === "string") return item;
        return item.msg || item.message || String(item);
      }).join("; ");
    }
  } catch {
    // Proxy and server errors may arrive as plain text.
  }
  if (response.status === 413) return "Audio fayl server limiti uchun juda katta. Hozirgi limit 100 MB.";
  if (response.status >= 500) return "Server audio faylni tahlil qilishda xatolik qaytardi. Fayl formati yoki codec o'qilmasligi mumkin.";
  return text || "Audio tahlil vaqtida xatolik yuz berdi.";
}

function Score({ label, value }: { label: string; value?: number }) {
  const percent = Math.round((value || 0) * 100);
  return (
    <div className="rounded-xl border theme-border bg-white/[0.03] p-3">
      <p className="text-[10px] font-bold uppercase tracking-wider theme-text-muted">{label}</p>
      <p className="mt-1 text-2xl font-black theme-text-primary">{percent}%</p>
    </div>
  );
}




