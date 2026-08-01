"use client";
import { FileText, Search, Shield, Globe } from "lucide-react";

export default function TextAnalyzerPage() {
  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div>
        <p className="text-xs theme-text-muted mb-1">Dashboard / Matn tahlili</p>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold theme-text-primary">Matn Tahlili</h1>
          <span className="text-[10px] font-bold px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">TEZDA</span>
        </div>
        <p className="text-sm theme-text-muted mt-1">AI-yozilgan matn, soxta xabar risk, manba ishonchliligi tekshiruvi</p>
      </div>

      <div className="card p-12 flex flex-col items-center justify-center text-center border-amber-500/20">
        <div className="flex h-24 w-24 items-center justify-center rounded-2xl bg-amber-500/10 border border-amber-500/20 mb-6">
          <FileText className="h-12 w-12 text-amber-400 opacity-60" />
        </div>
        <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 mb-4">Tayyorlanmoqda</span>
        <h2 className="text-xl font-bold theme-text-primary mb-3">Matn Tahlil moduli</h2>
        <p className="text-sm theme-text-muted max-w-md leading-relaxed">
          Ushbu modul hozir tayyorlanmoqda. Dizayn va report strukturasi tayyor, backend modeli keyingi bosqichda ulanadi.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: FileText, label: "AI yozim ehtimoli", desc: "ChatGPT, Claude, Gemini kabi modellar belgilari" },
          { icon: Shield, label: "Soxta xabar risk", desc: "Fake news va dezinformatsiya tahlili" },
          { icon: Globe, label: "Manba ishonchliligi", desc: "Manbaning haqiqiyligi va obro'si" },
          { icon: Search, label: "Jumlalar tahlili", desc: "Shubhali jumlalarni ajratib ko'rsatish" },
        ].map((f) => (
          <div key={f.label} className="card p-5 opacity-60">
            <f.icon className="h-7 w-7 text-amber-400 mb-3" />
            <h3 className="text-sm font-semibold theme-text-primary mb-1">{f.label}</h3>
            <p className="text-xs theme-text-muted leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}



