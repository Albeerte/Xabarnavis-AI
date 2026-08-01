"use client";
import { use } from "react";
import { mockReports } from "@/lib/mock-data";
import { AlertTriangle, CheckCircle, Globe } from "lucide-react";
import { usePathname } from "next/navigation";
import { localeFromPathname, qrCodeUrlFor } from "@/lib/qr";

export default function PublicReportPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = use(params);
  const pathname = usePathname();
  const locale = localeFromPathname(pathname);
  const report = mockReports.find(r => r.publicToken === token) ?? mockReports[0];
  const publicUrl = `${typeof window !== "undefined" ? window.location.origin : "http://127.0.0.1:3000"}/${locale}/r/public/${report.publicToken}`;
  const qrUrl = qrCodeUrlFor(publicUrl, 160);

  return (
    <main className="min-h-screen bg-[#07111f] p-4 flex items-center justify-center">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center overflow-hidden rounded-lg border border-cyan-400/30 bg-white/10 p-1">
              <img src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" className="h-full w-full object-contain" />
            </span>
            <span className="text-sm font-bold text-cyan-400">Xabarnavis AI</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400 bg-white/5 border border-white/10 rounded-full px-3 py-1">
            <Globe className="h-3 w-3" />Public Report
          </div>
        </div>

        {/* Report Document */}
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden text-slate-900">
          {/* Doc Header */}
          <div className="bg-slate-900 p-6 flex items-start justify-between">
            <div>
              <p className="text-[10px] text-cyan-400 font-bold uppercase tracking-widest mb-1">Xabarnavis AI â€” Rasmiy Forensic Hisobot</p>
              <h1 className="text-lg font-bold text-white mb-1">Tekshiruv natijasi</h1>
              <p className="text-xs text-slate-400 font-mono">{report.id}</p>
            </div>
            <div className="bg-white p-2 rounded-lg">
              <img src={qrUrl} alt={`QR for ${report.id}`} className="h-20 w-20" />
            </div>
          </div>

          <div className="p-6 space-y-5">
            {/* Result */}
            <div className={`rounded-xl p-4 border flex items-start gap-3 ${report.aiProbability > 60 ? "bg-red-50 border-red-200" : "bg-green-50 border-green-200"}`}>
              {report.aiProbability > 60
                ? <AlertTriangle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                : <CheckCircle className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />}
              <div>
                <p className={`text-sm font-bold ${report.aiProbability > 60 ? "text-red-700" : "text-green-700"}`}>{report.result}</p>
                <p className="text-xs text-slate-600 mt-0.5 leading-relaxed">{report.conclusionUz}</p>
              </div>
            </div>

            {/* Scores */}
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-center">
                <p className="text-2xl font-black text-red-600">{report.aiProbability}%</p>
                <p className="text-xs text-slate-500 mt-1">AI ehtimoli</p>
              </div>
              <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-center">
                <p className="text-2xl font-black text-green-600">{report.realProbability}%</p>
                <p className="text-xs text-slate-500 mt-1">Haqiqiylik darajasi</p>
              </div>
            </div>

            {/* Masked info */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tekshiruv ma'lumotlari</h3>
              {[
                ["Fayl turi", report.fileType],
                ["Tekshiruv sanasi", report.analyzedAt],
                ["Model versiyasi", `${report.modelName} ${report.modelVersion}`],
                ["Qurilma", "***"],
                ["IP manzil", report.maskedIp],
                ["Foydalanuvchi", "u***@example.com"],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-1.5 border-b border-slate-100 last:border-0 text-sm">
                  <span className="text-slate-500">{k}</span>
                  <span className="text-slate-800 font-medium">{v}</span>
                </div>
              ))}
            </div>

            {/* Disclaimer */}
            <div className="rounded-xl bg-slate-50 border border-slate-200 p-4 text-xs text-slate-500 leading-relaxed">
              <strong className="text-slate-700">Muhim eslatma:</strong>{" "}
              Xabarnavis AI natijasi avtomatlashtirilgan forensic tahlilga asoslangan. Yakuniy huquqiy yoki ekspert xulosasi sifatida qabul qilinmasligi kerak.
            </div>

            {/* Verification Badge */}
            <div className="flex items-center justify-center gap-2 py-3 border-t border-slate-200">
              <img src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" className="h-6 w-6 object-contain" />
              <span className="text-xs text-slate-500 font-medium">Bu hisobot Xabarnavis AI tomonidan yaratilgan va tasdiqlangan</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}



