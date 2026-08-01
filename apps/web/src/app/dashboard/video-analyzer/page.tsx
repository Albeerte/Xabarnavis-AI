"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, CheckCircle, Clock, FileVideo, Layers, Loader2, Shield, Upload, Video, X } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_XABARNAVIS_API_URL || "http://127.0.0.1:8000";

const STEPS = [
  "Video fayl qabul qilindi",
  "SHA-256 dalil hash hisoblanmoqda",
  "Xabarnavis Video 0.1 GenConViT modeli tekshiruvga tayyorlanmoqda",
  "Xabarnavis Video 0.2 ResNext50 + LSTM modeli statusi tekshirilmoqda",
  "DeepfakeBench, M2F2-Det, DFDC va FaceForensics resurslari reportga biriktirilmoqda",
  "Kadr, yuz va temporal deepfake signallari baholanmoqda",
  "Legal hisobot bazaga saqlanmoqda",
];

type VideoResult = {
  case_id: number;
  final_verdict: string;
  confidence: string;
  scores: Record<string, number>;
};

export default function VideoAnalyzerPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [step, setStep] = useState(-1);
  const [error, setError] = useState("");
  const [result, setResult] = useState<VideoResult | null>(null);

  function chooseFile(nextFile: File) {
    if (!nextFile.type.startsWith("video/")) {
      setError("Faqat video fayl yuklang: MP4, MOV, AVI yoki WEBM.");
      return;
    }
    if (nextFile.size > 300 * 1024 * 1024) {
      setError("Video fayl 300 MBdan katta. Iltimos, qisqaroq video yuklang.");
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
        await new Promise((resolve) => setTimeout(resolve, 600));
      }
    })();

    try {
      const form = new FormData();
      form.set("file", file);
      const response = await fetch(`${API_BASE_URL}/api/analyze/video`, {
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
      setError(exc instanceof Error ? exc.message : "Video tahlil vaqtida xatolik yuz berdi.");
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
        <p className="mb-1 text-[10px] font-bold uppercase tracking-widest text-purple-500">Dashboard / Video tahlili</p>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-black tracking-tight theme-text-primary sm:text-3xl">Video Tahlili</h1>
          <span className="rounded-md border border-purple-400/30 bg-purple-400/10 px-2 py-1 text-[9px] font-black tracking-widest text-purple-400">
            JONLI
          </span>
        </div>
        <p className="mt-2 max-w-3xl text-sm font-semibold theme-text-secondary">
          Video deepfake, kadr forensic, yuz izchilligi va vaqt bo'yicha manipulyatsiya signallarini tekshirish.
        </p>
      </div>

      <div className="rounded-3xl border border-purple-300/30 bg-[radial-gradient(circle_at_0%_0%,rgba(168,85,247,0.18),transparent_18rem),var(--bg-card)] p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="grid h-14 w-14 place-items-center rounded-2xl border border-purple-400/30 bg-purple-400/10 text-purple-400">
              <Video className="h-7 w-7" />
            </div>
            <div>
              <p className="text-[11px] font-black uppercase tracking-[0.22em] text-purple-500">Asosiy video modeli</p>
              <h2 className="mt-1 text-3xl font-black tracking-tight theme-text-primary sm:text-4xl">Xabarnavis Video 0.1</h2>
            </div>
          </div>
          <div className="rounded-2xl border theme-border bg-white/[0.04] px-4 py-3 text-sm font-bold theme-text-secondary">
            GenConViT deepfake video detector
          </div>
        </div>
        <p className="mt-4 text-sm font-semibold leading-6 theme-text-secondary">
          GenConViT ConvNeXt, Swin Transformer, Autoencoder va VAE signallarini birlashtiradi. Xabarnavis Video 0.2 esa Naman712 ResNext50 + LSTM modeli orqali temporal deepfake signalini tekshiradi. DeepfakeBench, M2F2-Det, DFDC Challenge va FaceForensics++ research resurslari ham hisobotga status va setup guide sifatida qo'shiladi.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
        <section className="card overflow-hidden">
          {!file ? (
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="drop-zone flex min-h-[380px] w-full flex-col items-center justify-center p-10 text-center"
            >
              <div className="mb-6 grid h-20 w-20 place-items-center rounded-3xl border border-purple-400/30 bg-purple-400/10">
                <Upload className="h-10 w-10 text-purple-400" />
              </div>
              <h3 className="text-lg font-black theme-text-primary">Video faylni yuklang</h3>
              <p className="mt-3 max-w-sm text-sm leading-6 theme-text-secondary">
                MP4, MOV, AVI, WEBM formatlari. Tahlil tugagach video hisobot sahifasiga avtomatik o'tadi.
              </p>
              <input
                ref={inputRef}
                hidden
                type="file"
                accept="video/*"
                onChange={(event) => event.target.files?.[0] && chooseFile(event.target.files[0])}
              />
            </button>
          ) : (
            <div>
              <div className="flex min-h-[280px] flex-col items-center justify-center gap-5 bg-[var(--bg-secondary)] p-6">
                <div className="grid h-16 w-16 place-items-center rounded-2xl border border-purple-400/30 bg-purple-400/10">
                  <FileVideo className="h-8 w-8 text-purple-400" />
                </div>
                <video controls src={previewUrl} className="max-h-[340px] w-full max-w-2xl rounded-2xl border theme-border bg-black" />
              </div>
              <div className="flex flex-col gap-4 border-t theme-border p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <p className="truncate text-sm font-black theme-text-primary">{file.name}</p>
                  <p className="mt-1 text-xs theme-text-muted">{(file.size / 1024 / 1024).toFixed(2)} MB | {file.type || "video"}</p>
                </div>
                <div className="flex gap-2">
                  <button type="button" className="rounded-xl border theme-border p-3 theme-text-secondary hover:text-red-400" onClick={reset} disabled={busy}>
                    <X className="h-4 w-4" />
                  </button>
                  <button type="button" className="btn-primary" onClick={analyze} disabled={busy}>
                    {busy ? "Tekshirilmoqda..." : "Video tahlilni boshlash"}
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
                  <p className="text-[10px] font-black uppercase tracking-[0.18em] text-purple-400">Xabarnavis Video 0.1 ishlamoqda</p>
                  <h3 className="mt-1 text-xl font-black theme-text-primary">GenConViT tekshiruvi</h3>
                </div>
                <Loader2 className="h-5 w-5 animate-spin text-purple-400" />
              </div>
              <div className="space-y-3">
                {STEPS.map((item, index) => (
                  <div key={item} className={`flex items-center gap-3 text-xs font-bold ${index <= step ? "theme-text-primary" : "theme-text-muted opacity-50"}`}>
                    {index < step ? <CheckCircle className="h-4 w-4 text-purple-500" /> : <span className="h-4 w-4 rounded-full border theme-border" />}
                    {item}
                  </div>
                ))}
              </div>
            </div>
          )}

          {error && <div className="rounded-2xl border border-red-400/25 bg-red-500/10 p-4 text-sm font-semibold text-red-500">{error}</div>}

          {result && (
            <div className="card p-5">
              <p className="text-xs font-black uppercase tracking-widest theme-text-muted">Natija</p>
              <h3 className="mt-2 text-xl font-black theme-text-primary">{result.final_verdict}</h3>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Score label="Real video" value={result.scores.video_real_score} />
                <Score label="Deepfake" value={result.scores.video_fake_score} />
              </div>
            </div>
          )}

          <div className="grid gap-3">
            {[
              { icon: Layers, label: "Kadr tahlili", desc: "Tanlangan kadrlar deepfake artefaktlari uchun tekshiriladi" },
              { icon: Activity, label: "Yuz izchilligi", desc: "Yuz landmarklari va mimika uzilishlari baholanadi" },
              { icon: Clock, label: "Vaqt tahlili", desc: "Shubhali bo'laklar vaqt kesimida hujjatlashtiriladi" },
              { icon: Shield, label: "Legal report", desc: "Natija user hisobiga bog'lanib bazaga saqlanadi" },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                <item.icon className="mb-3 h-5 w-5 text-purple-400" />
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
  } catch {
    // Plain text server/proxy errors are handled below.
  }
  if (response.status === 413) return "Video fayl server limiti uchun juda katta.";
  if (response.status >= 500) return "Server video faylni tahlil qilishda xatolik qaytardi. Fayl formati yoki codec o'qilmasligi mumkin.";
  return text || "Video tahlil vaqtida xatolik yuz berdi.";
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




