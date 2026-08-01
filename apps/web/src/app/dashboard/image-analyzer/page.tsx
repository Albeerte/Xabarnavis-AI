"use client";

import { useState, useRef, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ImageIcon, X, CheckCircle, Shield, AlertTriangle, FileText } from "lucide-react";

const STEPS = [
  "Fayl qabul qilindi",
  "Metadata o'qilmoqda",
  "Xabarnavis 0.5 modeli AI/Real qarorni tekshirmoqda",
  "Manipulation izlari qidirilmoqda",
  "EXIF va qurilma ma'lumotlari tekshirilmoqda",
  "Heatmap yaratilmoqda",
  "Hisobot tayyorlanmoqda",
];

interface Result {
  aiP: number; realP: number; manip: number;
  risk: string; result: string; reportId: string;
  modelResults: Array<{
    model_id: string;
    name: string;
    status: string;
    verdict: string;
    ai_score?: number | null;
    real_score?: number | null;
    manipulated_score?: number | null;
    confidence?: string | null;
    error?: string | null;
  }>;
}

export default function ImageAnalyzerPage() {
  const router = useRouter();
  const [over, setOver]       = useState(false);
  const [file, setFile]       = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [step, setStep]       = useState(-1);
  const [busy, setBusy]       = useState(false);
  const [result, setResult]   = useState<Result | null>(null);
  const [deepScan, setDeepScan] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith("image/")) return;
    setFile(f); setResult(null);
    const reader = new FileReader();
    reader.onload = e => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const analyze = async () => {
    if (!file) return;
    setBusy(true); setResult(null);
    const progress = (async () => {
      for (let i = 0; i < STEPS.length; i++) {
        setStep(i);
        await new Promise(r => setTimeout(r, 450));
      }
    })();

    try {
      const form = new FormData();
      form.set("file", file);
      form.set("image_description", "");
      form.set("deep_scan", deepScan ? "true" : "false");
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: form,
        credentials: "include",
      });
      await progress;
      if (!response.ok) {
        throw new Error(await response.text());
      }
      const data = await response.json();
      const aiP = Math.round((data.scores?.ai_score ?? 0) * 100);
      const realP = Math.round((data.scores?.real_score ?? 0) * 100);
      const manip = Math.round((data.scores?.manipulated_score ?? 0) * 100);
      setResult({
        aiP,
        realP,
        manip,
        risk: data.confidence === "High" ? "Juda yuqori" : data.confidence === "Medium" ? "O'rtacha" : "Past",
        result: data.final_verdict || "Tahlil yakunlandi",
        reportId: String(data.case_id),
        modelResults: data.model_results || [],
      });
      router.push(`/dashboard/reports/${data.case_id}`);
    } catch {
      await progress;
      setResult({
        aiP: 0,
        realP: 0,
        manip: 0,
        risk: "Past",
        result: "Tahlil vaqtida xatolik yuz berdi",
        reportId: "",
        modelResults: [],
      });
    } finally {
      setStep(-1); setBusy(false);
    }
  };

  const reset = () => { setFile(null); setPreview(null); setResult(null); setStep(-1); setBusy(false); };

  const riskColor = (r: string) => ({
    "Juda yuqori": "text-red-500", Yuqori: "text-orange-500",
    "O'rtacha": "text-amber-500", Past: "text-green-500",
  }[r] ?? "theme-text-secondary");

  return (
    <div className="p-4 lg:p-6 lg:max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <p className="text-[10px] font-bold uppercase tracking-widest text-cyan-400 mb-1">Dashboard / Rasm tahlili</p>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl sm:text-3xl font-black theme-text-primary tracking-tight">Rasm Tahlili</h1>
          <span className="text-[9px] font-black px-2 py-1 rounded-md tracking-widest text-green-400 border border-green-400/30 bg-green-400/10">
            JONLI
          </span>
        </div>
        <div className="primary-model-card mt-5 rounded-3xl p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="primary-model-icon grid h-14 w-14 place-items-center rounded-2xl">
                <Shield className="h-7 w-7" />
              </div>
              <div>
                <p className="primary-model-kicker text-[11px] font-black uppercase tracking-[0.22em]">Asosiy tekshiruv modeli</p>
                <h2 className="primary-model-title mt-1 text-3xl font-black tracking-tight sm:text-4xl">
                  Xabarnavis 0.5
                </h2>
              </div>
            </div>
            <div className="primary-model-badge rounded-2xl px-4 py-3 text-sm font-bold">
              Yakuniy qaror faqat shu model natijasidan olinadi
            </div>
          </div>
          <p className="primary-model-description mt-4 text-sm font-semibold leading-6">
            Ateeqq/ai-vs-human-image-detector modeli AI rasm va real rasm ehtimolini hisoblaydi. Boshqa forensic modellar faqat qo'shimcha izoh va dalil uchun ishlatiladi.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Upload + Progress */}
        <div className="flex flex-col gap-4">
          {!file ? (
            <div
              className={`drop-zone flex flex-col items-center justify-center p-12 text-center h-[400px] ${over ? "dragover" : ""}`}
              onDragOver={e => { e.preventDefault(); setOver(true); }}
              onDragLeave={() => setOver(false)}
              onDrop={onDrop}
              onClick={() => inputRef.current?.click()}
            >
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mb-6">
                <ImageIcon className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-base font-bold theme-text-primary mb-2">Faylni yuklang yoki tortib olib keling</h3>
              <p className="text-sm theme-text-muted max-w-[250px]">
                JPEG, PNG, WEBP (Maks: 20MB). Qaror Xabarnavis 0.5 modeli bilan chiqariladi.
              </p>
              <input type="file" ref={inputRef} hidden accept="image/*" onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />
            </div>
          ) : (
            <div className="card overflow-hidden">
              <div className="relative h-64 bg-[var(--bg-secondary)] flex items-center justify-center p-4">
                <img src={preview!} alt="preview" className="max-h-full max-w-full object-contain rounded-lg shadow-lg" />
                <button
                  className="absolute top-4 right-4 w-8 h-8 rounded-lg bg-black/50 backdrop-blur-md border border-white/10 text-white flex items-center justify-center hover:bg-red-500/80 transition-colors"
                  onClick={reset} disabled={busy}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="p-4 border-t theme-border flex items-center justify-between bg-white/5">
                <div className="min-w-0">
                  <p className="text-sm font-bold theme-text-primary truncate">{file.name}</p>
                  <p className="text-xs theme-text-muted mt-0.5">{(file.size / 1024 / 1024).toFixed(2)} MB â€¢ {file.type}</p>
                </div>
                {!busy && !result && (
                  <button className="btn-primary" onClick={analyze}>
                    Tahlilni boshlash
                  </button>
                )}
              </div>
            </div>
          )}

          {file && !busy && !result && (
            <label className="card flex cursor-pointer items-start gap-3 p-4 transition hover:border-cyan-400/30">
              <input
                type="checkbox"
                checked={deepScan}
                onChange={(event) => setDeepScan(event.target.checked)}
                className="mt-1 h-4 w-4 accent-cyan-400"
              />
              <span>
                <span className="block text-sm font-black theme-text-primary">Deep scan: qo'shimcha forensic modellarni ham ishlatish</span>
                <span className="mt-1 block text-xs leading-5 theme-text-secondary">
                  Yakuniy qaror baribir faqat Xabarnavis 0.5 modelidan olinadi. Xabarnavis 0.3 o'chirilgan; faqat barqaror modellar qo'shimcha dalil sifatida ko'rsatiladi.
                </span>
              </span>
            </label>
          )}

          {/* Progress */}
          {busy && (
            <div className="card p-6 fade-in space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-black uppercase tracking-[0.18em] text-cyan-400">Asosiy model ishlamoqda</p>
                  <h3 className="mt-1 text-2xl font-black theme-text-primary">Xabarnavis 0.5</h3>
                </div>
                <span className="text-sm font-bold text-cyan-400">{Math.round((step / (STEPS.length - 1)) * 100)}%</span>
              </div>
              <div className="rounded-xl border border-cyan-200 bg-cyan-50 p-3 text-xs font-semibold leading-5 text-slate-700 dark:border-cyan-400/20 dark:bg-cyan-400/10 dark:text-cyan-200">
                Qaror Xabarnavis 0.5 modeli natijasidan olinadi. Tahlil tugashi bilan siz avtomatik to'liq hisobot sahifasiga o'tasiz.
              </div>
              <div className="progress-bar">
                <div className="progress-fill bg-cyan-500 shadow-[0_0_10px_rgba(0,229,255,0.5)]" style={{ width: `${(step / (STEPS.length - 1)) * 100}%` }} />
              </div>
              <div className="space-y-3 mt-6">
                {STEPS.map((s, i) => (
                  <div key={i} className={`flex items-center gap-3 text-xs font-medium transition-all duration-300 ${i <= step ? "theme-text-primary" : "theme-text-muted opacity-40"}`}>
                    {i < step ? (
                      <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />
                    ) : i === step ? (
                      <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-[var(--border)] shrink-0" />
                    )}
                    {s}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Results */}
        {result ? (
          <div className="flex flex-col gap-4 fade-in">
            {/* Score Hero */}
            <div className="card p-6 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--accent-cyan)]/5 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none" />
              <div className="flex items-start justify-between mb-8">
                <div>
                  <p className="text-xs font-bold theme-text-muted uppercase tracking-wider mb-2">Umumiy Natija</p>
                  <div className="flex items-center gap-2">
                    <Shield className={`w-5 h-5 ${riskColor(result.risk)}`} />
                    <h2 className="text-2xl font-black theme-text-primary">{result.result}</h2>
                  </div>
                </div>
                <div className={`px-3 py-1.5 rounded-lg border text-xs font-bold ${result.aiP > 50 ? 'badge-ai' : 'badge-real'}`}>
                  Risk: {result.risk}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 text-center divide-x theme-border">
                <div>
                  <p className="text-[10px] uppercase tracking-wider theme-text-muted mb-1">AI Ehtimoli</p>
                  <p className={`text-2xl font-black ${result.aiP > 50 ? 'text-red-500' : 'theme-text-primary'}`}>{result.aiP}%</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider theme-text-muted mb-1">Haqiqiy</p>
                  <p className="text-2xl font-black text-green-500">{result.realP}%</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider theme-text-muted mb-1">Manipulyatsiya</p>
                  <p className="text-2xl font-black text-amber-500">{result.manip}%</p>
                </div>
              </div>
            </div>

            {/* Modules Check */}
            <div className="card p-6">
              <h3 className="text-sm font-bold theme-text-primary mb-4">Detektor Xulosalari</h3>
              <div className="space-y-3">
                {[
                  {
                    name: "Xabarnavis fused forensic score",
                    status: "ready",
                    verdict: result.result,
                    ai_score: result.aiP / 100,
                  },
                  ...result.modelResults,
                ].map((m, i) => {
                  const ready = m.status === "ready";
                  const score = typeof m.ai_score === "number" ? `${Math.round(m.ai_score * 100)}%` : m.status;
                  return (
                  <div key={`${m.name}-${i}`} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-xl bg-white/5 border theme-border gap-2">
                    <div className="flex items-center gap-3">
                      {!ready ? <AlertTriangle className="w-4 h-4 text-amber-500" /> : <CheckCircle className="w-4 h-4 text-green-500" />}
                      <span className="text-xs font-bold theme-text-primary">{m.name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="theme-text-secondary">{m.verdict}</span>
                      <span className={`font-mono font-bold ${ready ? "theme-text-primary" : "text-amber-500"}`}>{score}</span>
                    </div>
                  </div>
                )})}
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <Link href={`/dashboard/reports/${result.reportId || "latest"}`} className="btn-primary w-full flex items-center justify-center gap-2">
                <FileText className="w-4 h-4" /> To'liq hisobotni ochish
              </Link>
            </div>
          </div>
        ) : (
          <div className="hidden lg:flex flex-col items-center justify-center h-full min-h-[400px] border-2 border-dashed theme-border rounded-2xl bg-white/5 opacity-50">
            <ImageIcon className="w-12 h-12 theme-text-muted mb-4 opacity-50" />
            <p className="text-sm font-bold theme-text-muted">Natijalar bu yerda ko'rinadi</p>
          </div>
        )}
      </div>
    </div>
  );
}



