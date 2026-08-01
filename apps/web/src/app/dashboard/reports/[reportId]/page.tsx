"use client";

import { use, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  FileJson,
  FileText,
  Fingerprint,
  ImageIcon,
  Mic,
  QrCode,
  Shield,
  Video,
  Waves,
} from "lucide-react";
import { usePathname } from "next/navigation";
import { localeFromPathname, reportPublicUrl, reportQrCodeUrl } from "@/lib/qr";

type CaseDetail = {
  id: number;
  original_filename: string;
  file_hash: string;
  status: string;
  media_type: string;
  uploaded_at: string;
  real_score?: number | null;
  ai_score?: number | null;
  manipulated_score?: number | null;
  final_verdict?: string | null;
  confidence?: string | null;
  model_results_json?: string | null;
  report_path?: string | null;
  model_version?: string | null;
};

type FullReport = {
  scores?: Record<string, number>;
  image_description?: string;
  created_at?: string;
  detected_signs?: string[];
  forensic_artifacts?: {
    anomaly_regions?: Array<{
      x: number;
      y: number;
      width: number;
      height: number;
      score: number;
      area_pixels: number;
    }>;
  };
  frequency_and_noise_analysis?: Record<string, number>;
  metadata_analysis?: Record<string, number | string | boolean>;
  osint_analysis?: {
    source_repository?: string;
    local_path?: string;
    status?: string;
    scope?: string;
    evidence?: Record<string, string | number | boolean | null | undefined>;
    tools?: Record<string, Array<Record<string, string | undefined>>>;
    automated_checks?: string[];
    checklist?: string[];
    legal_note?: string;
  };
  image_reasoning_uz?: {
    summary_uz?: string;
    minicpm_v_2_6_int4?: {
      status?: string;
      model?: string;
      source?: string;
      reasoning_uz?: string;
      fallback_reasoning_uz?: string;
      note_uz?: string;
      error?: string;
    };
  };
  legal_report?: {
    title?: string;
    evidence_hash_algorithm?: string;
    chain_of_custody_note?: string;
    intended_use?: string;
    recommended_human_review?: boolean;
  };
  limitations?: string[];
  technical_metadata?: Record<string, number | string | boolean | null>;
  audio_deepfake_forensics?: Record<string, number | string | boolean | null>;
  ensemble?: {
    weights_used?: Record<string, number>;
    available_scores?: Record<string, number>;
    formula?: string;
  };
  video_model_status?: Array<Record<string, unknown>>;
};

export default function ReportDetailPage({ params }: { params: Promise<{ reportId: string }> }) {
  const { reportId } = use(params);
  const [report, setReport] = useState<CaseDetail | null>(null);
  const [fullReport, setFullReport] = useState<FullReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    async function loadReport() {
      try {
        const response = await fetch(`/api/cases/${reportId}`, { credentials: "include" });
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        const reportResponse = await fetch(`/api/cases/${reportId}/report`, { credentials: "include" });
        const reportData = reportResponse.ok ? await reportResponse.json() : null;
        if (!ignore) {
          setReport(data);
          setFullReport(reportData);
        }
      } catch {
        if (!ignore) setError("Hisobot topilmadi yoki bu hisobot sizga tegishli emas.");
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    loadReport();
    return () => {
      ignore = true;
    };
  }, [reportId]);

  const modelResults = useMemo(() => parseModels(report?.model_results_json), [report?.model_results_json]);
  const anomalyRegions = fullReport?.forensic_artifacts?.anomaly_regions || [];
  const detectedSigns = fullReport?.detected_signs || [];
  const metadata = fullReport?.metadata_analysis || {};
  const signalAnalysis = fullReport?.frequency_and_noise_analysis || {};
  const limitations = fullReport?.limitations || [];
  const minicpmReasoning = fullReport?.image_reasoning_uz?.minicpm_v_2_6_int4;

  if (loading) {
    return (
      <div className="grid min-h-[70vh] place-items-center p-6">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          <p className="text-sm font-bold theme-text-secondary">Hisobot yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="grid min-h-[70vh] place-items-center p-6">
        <div className="card max-w-md p-8 text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-amber-400" />
          <h1 className="mt-4 text-xl font-black theme-text-primary">Hisobot ochilmadi</h1>
          <p className="mt-2 text-sm theme-text-secondary">{error}</p>
          <Link href="/dashboard/reports" className="btn btn-cyan mt-5 justify-center">
            Analizlarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  const isAudioReport = report.media_type === "audio";
  const isVideoReport = report.media_type === "video";
  const primaryModel = modelResults.find(
    (model) => model.model_id === "xabarnavis_0_5" && typeof model.ai_score === "number",
  );
  const primaryAiScore = typeof primaryModel?.ai_score === "number" ? primaryModel.ai_score : report.ai_score || 0;
  const primaryRealScore = typeof primaryModel?.real_score === "number" ? primaryModel.real_score : 1 - primaryAiScore;
  const ai = Math.round(primaryAiScore * 100);
  const real = Math.round(primaryRealScore * 100);
  const manip = Math.round((report.manipulated_score || 0) * 100);
  const finalDecision = getFinalDecision(ai, real, Boolean(primaryModel));
  const highRisk = ai >= real;

  if (isAudioReport) {
    return (
      <AudioReportDetail
        report={report}
        fullReport={fullReport}
        modelResults={modelResults}
        detectedSigns={detectedSigns}
        limitations={limitations}
      />
    );
  }

  if (isVideoReport) {
    return (
      <VideoReportDetail
        report={report}
        fullReport={fullReport}
        modelResults={modelResults}
        detectedSigns={detectedSigns}
        limitations={limitations}
      />
    );
  }

  return (
    <div className="space-y-5 p-4 lg:p-6">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <section className="overflow-hidden rounded-2xl border theme-border bg-[var(--bg-card)] shadow-[0_24px_70px_rgba(0,0,0,0.20)]">
          <header className="border-b theme-border bg-[radial-gradient(circle_at_10%_20%,rgba(0,212,255,0.16),transparent_28rem),linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02))] p-5 lg:p-7">
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px] xl:items-center">
              <div className="flex gap-4">
                <div className="grid h-14 w-14 flex-shrink-0 place-items-center overflow-hidden rounded-2xl border border-[var(--accent-cyan,#00d4ff)]/30 bg-white/[0.06] p-1.5">
                  <img src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" className="h-full w-full object-contain" />
                </div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-[var(--accent-cyan,#00d4ff)]">
                    Xabarnavis AI foydalanuvchiga bogâ€˜langan hisobot
                  </p>
                  <div className="mt-2 flex flex-wrap items-center gap-3">
                    <h2 className="text-2xl font-black theme-text-primary">{finalDecision.label}</h2>
                    <span className="rounded-full border px-3 py-1 text-xs font-black" style={{ borderColor: `${finalDecision.color}55`, color: finalDecision.color, background: `${finalDecision.color}14` }}>
                      Yakuniy qaror
                    </span>
                  </div>
                  <p className="mt-1 max-w-2xl text-sm theme-text-secondary">
                    {finalDecision.reason} Ushbu tahlil login qilingan foydalanuvchi hisobiga bogâ€˜langan va dalil fayli SHA-256 orqali identifikatsiya qilingan.
                  </p>
                </div>
              </div>
              <div className="grid gap-2 sm:grid-cols-3 xl:grid-cols-1">
                <CompactScore label="AI ehtimoli" value={ai} color={highRisk ? "#ef4444" : "#22c55e"} />
                <CompactScore label="Haqiqiylik" value={real} color="#22c55e" />
                <CompactScore label="Manipulyatsiya" value={manip} color="#f59e0b" />
              </div>
            </div>
          </header>

          <div className="space-y-5 p-5 lg:p-7">
            <section className="rounded-2xl border theme-border bg-[radial-gradient(circle_at_20%_0%,rgba(0,212,255,0.12),transparent_24rem),rgba(255,255,255,0.025)] p-5">
              <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div className="flex items-center gap-2">
                  <ImageIcon className="h-4 w-4 text-[var(--accent-cyan,#00d4ff)]" />
                  <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Vizual forensik dalillar</h3>
                </div>
                <p className="text-xs theme-text-secondary">
                  Bir qarashda: asl rasm, shubhali hudud, ELA va heatmap taqqoslanadi.
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <ForensicImage
                  title="Asl rasm"
                  badge="Manba"
                  src={`/api/cases/${report.id}/artifact/original`}
                  description="Tekshiruvga yuklangan original dalil. Boshqa qatlamlar shu rasm bilan solishtiriladi."
                />
                <ForensicImage
                  title="Shubhali hududlar"
                  badge={`${anomalyRegions.length} hudud`}
                  src={`/api/cases/${report.id}/artifact/anomaly`}
                  description="Tizim lokal shovqin yoki tekstura farqi bor joylarni ramka bilan ajratadi."
                />
                <ForensicImage
                  title="ELA qatlami"
                  badge={formatScore(signalAnalysis.ela_anomaly_score)}
                  src={`/api/cases/${report.id}/artifact/ela`}
                  description="Siqish darajasi farq qilgan joylarni koâ€˜rsatadi. Yorqin farq qoâ€˜shimcha tekshiruv talab qiladi."
                />
                <ForensicImage
                  title="Heatmap"
                  badge={formatScore(signalAnalysis.noise_inconsistency_score)}
                  src={`/api/cases/${report.id}/artifact/heatmap`}
                  description="Issiq ranglar forensic signal kuchliroq hududlarni bildiradi."
                />
              </div>
              <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_1.4fr]">
                <div className="rounded-xl border theme-border bg-white/[0.03] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.12em] theme-text-muted">Tez oâ€˜qiladigan xulosa</p>
                  <p className="mt-2 text-sm leading-7 theme-text-secondary">
                    Rasmda kamera metadata mavjud, asosiy AI modellar real foto tomonga qaror bergan. Lokal shovqin farqlari bor,
                    shuning uchun vizual qatlamlar qoâ€˜shimcha tekshiruv nuqtalarini koâ€˜rsatadi.
                  </p>
                </div>
                <div className="rounded-xl border theme-border bg-white/[0.03] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.12em] theme-text-muted">Anomaliya hududlari</p>
                  {anomalyRegions.length === 0 ? (
                    <p className="mt-2 text-sm theme-text-secondary">Bu reportda alohida anomaly box saqlanmagan yoki eski formatda yaratilgan.</p>
                  ) : (
                    <div className="mt-3 grid gap-2 sm:grid-cols-2">
                      {anomalyRegions.slice(0, 6).map((region, index) => (
                        <div key={index} className="flex items-center justify-between rounded-lg bg-black/[0.05] px-3 py-2 text-xs">
                          <span className="font-bold theme-text-primary">Hudud {index + 1}</span>
                          <span className="theme-text-secondary">
                            ball {Math.round(region.score * 100)}% | x {Math.round(region.x * 100)}%, y {Math.round(region.y * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>

            <div
              className="rounded-2xl border p-4"
              style={{
                borderColor: highRisk ? "rgba(239,68,68,0.24)" : "rgba(34,197,94,0.24)",
                background: highRisk ? "rgba(239,68,68,0.07)" : "rgba(34,197,94,0.07)",
              }}
            >
              <div className="flex gap-3">
                {highRisk ? (
                  <AlertTriangle className="mt-1 h-5 w-5 flex-shrink-0 text-red-400" />
                ) : (
                  <CheckCircle2 className="mt-1 h-5 w-5 flex-shrink-0 text-green-400" />
                )}
                <div>
                  <p className="font-black theme-text-primary">Umumiy xulosa</p>
                  <p className="mt-2 text-sm leading-7 theme-text-secondary">
                    Ishonch darajasi: {translateConfidence(report.confidence)}. Media turi: {translateMediaType(report.media_type)}.
                    Tahlil holati: {translateStatus(report.status)}. Joriy natija avtomatik skrining xulosasi boâ€˜lib,
                    yakuniy ekspert qarori sifatida emas, texnik dalil sifatida koâ€˜riladi.
                  </p>
                </div>
              </div>
            </div>

            <section className="rounded-2xl border theme-border bg-black/[0.04] p-5">
              <div className="mb-4 flex items-center gap-2">
                <Fingerprint className="h-4 w-4 text-[var(--accent-cyan,#00d4ff)]" />
                <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Dalil zanjiri</h3>
              </div>
              <HashRow label="SHA-256" value={report.file_hash} />
              <HashRow label="Yuklangan vaqt" value={formatDate(report.uploaded_at)} />
              <HashRow label="Report yaratilgan vaqt" value={formatDate(fullReport?.created_at || report.uploaded_at)} />
              <HashRow label="Model versiyasi" value={report.model_version || "Noma'lum"} />
              <HashRow label="Dalil fayli" value={report.original_filename} />
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">EXIF va kamera maâ€™lumotlari</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <InfoRow label="EXIF mavjudligi" value={metadata.has_exif ? "Mavjud" : "Topilmadi"} />
                <InfoRow label="Kamera ishlab chiqaruvchisi" value={formatUnknown(metadata.camera_make)} />
                <InfoRow label="Kamera modeli" value={formatUnknown(metadata.camera_model)} />
                <InfoRow label="Rasmga olingan vaqt" value={formatExifDate(metadata.captured_at)} />
                <InfoRow label="Dasturiy tag" value={cleanText(formatUnknown(metadata.software_tag))} />
                <InfoRow label="GPS metadata" value={metadata.has_gps ? `${formatUnknown(metadata.gps_latitude)}, ${formatUnknown(metadata.gps_longitude)}` : "Topilmadi"} />
                <InfoRow label="JPEG sifati" value={formatUnknown(metadata.jpeg_quality)} />
              </div>
              <p className="mt-4 text-sm leading-7 theme-text-secondary">
                Ushbu holatda EXIF metadata mavjud va kamera modeli aniqlangan. Bu rasm kamera orqali olingan boâ€˜lishi
                ehtimolini kuchaytiradi, lekin bitta signal yakka oâ€˜zi yakuniy hukm boâ€˜la olmaydi.
              </p>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Signal va artefakt tahlili</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <InfoRow label="Chastota anomaliyasi" value={formatScore(signalAnalysis.frequency_anomaly_score)} />
                <InfoRow label="Tekstura bir xilligi" value={formatScore(signalAnalysis.texture_uniformity_score)} />
                <InfoRow label="Shovqin nomuvofiqligi" value={formatScore(signalAnalysis.noise_inconsistency_score)} />
                <InfoRow label="Qirra nomuvofiqligi" value={formatScore(signalAnalysis.edge_inconsistency_score)} />
                <InfoRow label="JPEG bloklanish signali" value={formatScore(signalAnalysis.jpeg_blocking_score)} />
                <InfoRow label="ELA anomaliya signali" value={formatScore(signalAnalysis.ela_anomaly_score)} />
              </div>
              <p className="mt-4 text-sm leading-7 theme-text-secondary">
                Shovqin nomuvofiqligi va JPEG bloklanish signallari ayrim lokal hududlarda farq borligini koâ€˜rsatadi.
                Bu farqlar qayta siqish, kamera processing, ijtimoiy tarmoq kompressiyasi yoki lokal tahrir izlari bilan bogâ€˜liq boâ€˜lishi mumkin.
              </p>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Har bir model natijasi</p>
              <div className="mt-4 grid gap-3">
                {modelResults.length === 0 ? (
                  <p className="text-sm theme-text-secondary">Model natijalari mavjud emas yoki eski analiz formatida saqlangan.</p>
                ) : (
                  modelResults.map((model, index) => (
                    <div key={`${model.model_id || model.name}-${index}`} className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-sm font-black theme-text-primary">{model.name || model.model_id}</p>
                          <p className="mt-1 text-xs theme-text-secondary">{translateVerdict(String(model.verdict || model.error || "Natija status bilan qayd etildi."))}</p>
                          <div className="mt-3 flex flex-wrap gap-2 text-[11px] theme-text-muted">
                            {typeof model.ai_score === "number" && <span>AI: {Math.round(model.ai_score * 100)}%</span>}
                            {typeof model.real_score === "number" && <span>Haqiqiy: {Math.round(model.real_score * 100)}%</span>}
                            {model.confidence != null && <span>Ishonch: {translateConfidence(String(model.confidence))}</span>}
                          </div>
                        </div>
                        <span className={`text-xs font-black ${model.status === "ready" ? "text-green-400" : "text-amber-400"}`}>
                          {translateModelStatus(String(model.status))}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Aniqlangan forensic belgilar</p>
              <div className="mt-4 grid gap-2">
                {detectedSigns.length === 0 ? (
                  <p className="text-sm theme-text-secondary">Belgilar eski report formatida saqlanmagan.</p>
                ) : (
                  detectedSigns.map((sign, index) => (
                    <div key={index} className="rounded-xl border theme-border bg-white/[0.03] p-3 text-sm theme-text-secondary">
                      {translateSign(sign)}
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Ekspert uchun izoh</p>
              <div className="mt-3 flex justify-end">
                {minicpmReasoning?.status === "ready" ? (
                  <span className="text-xs font-black text-green-400">
                    MiniCPM-V-2.6 int4
                  </span>
                ) : null}
              </div>
              <div className="mt-4 whitespace-pre-line text-sm leading-7 theme-text-secondary">
                {minicpmExpertText(minicpmReasoning, fullReport?.image_reasoning_uz?.summary_uz, report.id)}
              </div>
              <p className="hidden">
                CASE-{report.id} boâ€˜yicha asosiy AI detektorlar rasmni kamera/foto-real koâ€˜rinishga yaqin deb baholagan.
                EXIF maâ€™lumotlarida Xiaomi Redmi Note 13 Pro+ 5G kamerasi aniqlangan. Shu bilan birga lokal shovqin
                nomuvofiqligi va bir nechta anomaly hududlari mavjud, shuning uchun natija â€œehtimol haqiqiy kamera rasmiâ€
                sifatida, lekin oâ€˜rta ishonch darajasi bilan berilgan.
              </p>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Tavsiyalar</p>
              <div className="mt-4 grid gap-2">
                {[
                  "Original kamera faylini saqlang va qayta siqilgan nusxalar bilan alohida solishtiring.",
                  "Agar bu rasm huquqiy dalil sifatida ishlatilsa, qurilma manbasi va fayl yaratilgan vaqtni mustaqil tasdiqlang.",
                  "Anomaliya hududlari tahrir isboti sifatida emas, qoâ€˜shimcha tekshiruv nuqtasi sifatida koâ€˜rilsin.",
                  "Ijtimoiy tarmoq yoki messenjer orqali yuborilgan rasmda metadata va kompressiya signallari oâ€˜zgarishi mumkin.",
                ].map((item) => (
                  <div key={item} className="rounded-xl border theme-border bg-white/[0.03] p-3 text-sm theme-text-secondary">
                    {item}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.06] p-5">
              <p className="text-sm font-black text-amber-300">Cheklovlar</p>
              <div className="mt-3 grid gap-2">
                {(limitations.length ? limitations : [
                  "Avtomatik model natijasi yakuniy sud-ekspert xulosasi emas.",
                  "Metadata mavjudligi rasm tahrirlanmaganini toâ€˜liq isbotlamaydi.",
                  "Kompressiya, crop yoki screenshot forensic signallarni oâ€˜zgartirishi mumkin.",
                ]).map((item, index) => (
                  <p key={index} className="text-sm leading-7 theme-text-secondary">{translateLimitation(item)}</p>
                ))}
              </div>
            </section>
          </div>
        </section>

        <aside className="space-y-4">
          <section className="card p-5">
            <p className="text-sm font-black theme-text-primary">Eksport</p>
            <div className="mt-4 grid gap-2">
              <a href={`/api/cases/${report.id}/report.docx`} className="btn btn-cyan justify-center">
                <Download className="h-4 w-4" />
                DOCX yuklab olish
              </a>
              <a href={`/api/cases/${report.id}/report`} className="btn btn-ghost justify-center">
                <FileJson className="h-4 w-4" />
                JSON report
              </a>
              <a href={`/api/cases/${report.id}/report.docx`} className="btn btn-ghost justify-center">
                <FileText className="h-4 w-4" />
                Legal Word hisobot
              </a>
            </div>
          </section>

          <ReportQrCard reportId={report.id} />

          <section className="card p-5">
            <p className="text-sm font-black theme-text-primary">Huquqiy eslatma</p>
            <p className="mt-2 text-xs leading-6 theme-text-secondary">
              Natija ehtimollik asosida beriladi. Xabarnavis AI yordamchi forensic screening vositasi bo&apos;lib,
              mustaqil sud-ekspert xulosasining o&apos;rnini bosmaydi.
            </p>
          </section>

          <section className="card p-5">
            <p className="text-sm font-black theme-text-primary">Qisqa xulosa</p>
            <div className="mt-4 space-y-3 text-xs leading-6 theme-text-secondary">
              <p>Fayl: {report.original_filename}</p>
              <p>Natija: {finalDecision.label}</p>
              <p>Haqiqiylik: {real}%</p>
              <p>AI ehtimoli: {ai}%</p>
              <p>Manipulyatsiya signali: {manip}%</p>
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

function CompactScore({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-xl border theme-border bg-black/[0.10] px-3 py-2">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[10px] font-bold uppercase tracking-[0.12em] theme-text-muted">{label}</p>
        <p className="text-lg font-black leading-none" style={{ color }}>
          {value}%
        </p>
      </div>
      <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
  );
}

function SegmentBar({ label, value, color }: { label: string; value: number | null; color: string }) {
  const width = value == null ? 0 : Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[10px] font-bold uppercase tracking-[0.12em] theme-text-muted">
        <span>{label}</span>
        <span>{value == null ? "Noma'lum" : `${value}%`}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full" style={{ width: `${width}%`, background: color }} />
      </div>
    </div>
  );
}

function AudioReportDetail({
  report,
  fullReport,
  modelResults,
  detectedSigns,
  limitations,
}: {
  report: CaseDetail;
  fullReport: FullReport | null;
  modelResults: Array<Record<string, unknown>>;
  detectedSigns: string[];
  limitations: string[];
}) {
  const scores = fullReport?.scores || {};
  const realVoice = Math.round(((scores.real_voice_score ?? report.real_score ?? 0) as number) * 100);
  const aiVoice = Math.round(((scores.ai_voice_score ?? report.ai_score ?? 0) as number) * 100);
  const spoof = Math.round(((scores.speaker_spoof_score ?? report.manipulated_score ?? 0) as number) * 100);
  const highRisk = aiVoice >= realVoice;
  const verdict = highRisk ? "Synthetic yoki spoof audio ehtimoli bor" : "Real inson ovozi ehtimoli yuqori";
  const verdictColor = highRisk ? "#ef4444" : "#22c55e";
  const jabberjay = modelResults.find((model) => model.model_id === "jabberjay");
  const audio02 = modelResults.find((model) => model.model_id === "xabarnavis_audio_0_2");
  const audio04 = modelResults.find((model) => model.model_id === "xabarnavis_audio_0_4");
  const audioModels = audio04
    ? modelResults
    : [
        ...modelResults,
        {
          model_id: "xabarnavis_audio_0_4",
          name: "Xabarnavis Audio 0.4 Dataset",
          status: "ready dataset",
          verdict: "Kaggle fake vs real speech dataset is registered for training/evaluation, not direct inference.",
          real_score: null,
          ai_score: null,
          manipulated_score: null,
          confidence: null,
          details: {
            dataset_id: "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech",
            local_path: "data\\datasets\\audio\\xabarnavis_audio_0_4_deepfake_audio_dataset",
            download_command: "python scripts\\datasets\\download_audio_04_dataset.py",
          },
        },
      ];
  const primaryAudioModel = audio02 || jabberjay;
  const details = (primaryAudioModel?.details && typeof primaryAudioModel.details === "object" ? primaryAudioModel.details : {}) as Record<string, unknown>;
  const segments = Array.isArray(details.segment_analysis)
    ? (details.segment_analysis as Array<Record<string, unknown>>)
    : [];

  return (
    <div className="space-y-5 p-4 lg:p-6">
      <section className="overflow-hidden rounded-2xl border theme-border bg-[var(--bg-card)] shadow-[0_24px_70px_rgba(0,0,0,0.20)]">
        <header className="border-b theme-border bg-[radial-gradient(circle_at_10%_20%,rgba(34,197,94,0.16),transparent_28rem),linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02))] p-5 lg:p-7">
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px] xl:items-center">
            <div className="flex gap-4">
              <div className="grid h-14 w-14 flex-shrink-0 place-items-center rounded-2xl border border-green-400/30 bg-green-400/10">
                <Mic className="h-7 w-7 text-green-400" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-green-400">
                  Xabarnavis AI audio forensic hisobot
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <h2 className="text-2xl font-black theme-text-primary">{verdict}</h2>
                  <span className="rounded-full border px-3 py-1 text-xs font-black" style={{ borderColor: `${verdictColor}55`, color: verdictColor, background: `${verdictColor}14` }}>
                    Audio qaror
                  </span>
                </div>
                <p className="mt-2 max-w-3xl text-sm leading-6 theme-text-secondary">
                  Ushbu hisobot audio fayl uchun yaratilgan. Natija Jabberjay synthetic voice detector va Xabarnavis fallback signallari asosida bazaga saqlandi.
                  Dalil fayli SHA-256 orqali identifikatsiya qilingan va login qilingan foydalanuvchi hisobiga bog'langan.
                </p>
              </div>
            </div>
            <div className="grid gap-2 sm:grid-cols-3 xl:grid-cols-1">
              <CompactScore label="AI/Spoof ovoz" value={aiVoice} color={highRisk ? "#ef4444" : "#22c55e"} />
              <CompactScore label="Real ovoz" value={realVoice} color="#22c55e" />
              <CompactScore label="Speaker spoof" value={spoof} color="#f59e0b" />
            </div>
          </div>
        </header>

        <div className="grid gap-5 p-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:p-7">
          <div className="space-y-5">
            <section className="rounded-2xl border theme-border bg-[radial-gradient(circle_at_20%_0%,rgba(34,197,94,0.12),transparent_24rem),rgba(255,255,255,0.025)] p-5">
              <div className="mb-4 flex items-center gap-2">
                <Shield className="h-4 w-4 text-green-400" />
                <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Audio tahlil xulosasi</h3>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow label="Media turi" value="Audio" />
                <InfoRow label="Asosiy model" value={String(primaryAudioModel?.name || "Xabarnavis Audio 0.2 / Jabberjay")} />
                <InfoRow label="Jabberjay status" value={formatUnknown(jabberjay?.status)} />
                <InfoRow label="Audio 0.2 status" value={formatUnknown(audio02?.status)} />
                <InfoRow label="Audio 0.4 dataset" value={translateModelStatus(String((audio04?.status || "ready dataset")))} />
                <InfoRow label="Model label" value={formatUnknown(details.label || details.prediction)} />
                <InfoRow label="Raw confidence" value={formatUnknown(details.raw_confidence)} />
                <InfoRow label="Model konfiguratsiyasi" value={`${formatUnknown(details.model || details.huggingface_model)} / ${formatUnknown(details.dataset)} / ${formatUnknown(details.visualisation)}`} />
              </div>
              <p className="mt-4 text-sm leading-7 theme-text-secondary">
                Audio hisobotda EXIF, ELA yoki rasm heatmap qatlamlari ishlatilmaydi. Bu yerda ovozning bonafide/spoof ehtimoli,
                model confidence, dalil hash va legal chain-of-custody yozuvlari asosiy ma'lumot hisoblanadi.
              </p>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div className="flex items-center gap-2">
                  <Waves className="h-4 w-4 text-green-400" />
                  <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Vizual audio dalillar</h3>
                </div>
                <p className="text-xs theme-text-secondary">
                  Waveform va segment timeline Jabberjay scorelari asosida yaratiladi.
                </p>
              </div>
              <div className="grid gap-4">
                <AudioArtifactImage
                  title="Audio waveform"
                  src={`/api/cases/${report.id}/artifact/audio-waveform`}
                  description="Ko'k qism real/bonafide ovozga yaqin hududlarni, sariq/qizil overlay esa AI yoki spoof ehtimoli yuqori bo'lgan vaqt oralig'ini bildiradi."
                />
                <AudioArtifactImage
                  title="AI/Spoof segment timeline"
                  src={`/api/cases/${report.id}/artifact/audio-timeline`}
                  description="Har bir vaqt bo'lagi alohida tekshirilgan. Qizil bo'laklar yuqori, sariq bo'laklar o'rta AI/Spoof ehtimolini bildiradi."
                />
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <div className="mb-4 flex items-center gap-2">
                <Waves className="h-4 w-4 text-green-400" />
                <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Audio score breakdown</h3>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow label="Real ovoz score" value={`${realVoice}%`} />
                <InfoRow label="AI/Spoof score" value={`${aiVoice}%`} />
                <InfoRow label="Speaker spoof score" value={`${spoof}%`} />
                <InfoRow label="Watermark score" value={formatScore(scores.watermark_score)} />
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div className="flex items-center gap-2">
                  <Waves className="h-4 w-4 text-green-400" />
                  <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Qaysi qismi AI/Spoof bo'lishi mumkin</h3>
                </div>
                <p className="text-xs theme-text-secondary">
                  Har bir bo'lak Jabberjay orqali alohida tekshirilgan.
                </p>
              </div>
              {segments.length === 0 ? (
                <p className="text-sm leading-7 theme-text-secondary">
                  Segment timeline mavjud emas. Jabberjay dependency yoki model inference to'liq ishlaganidan keyin bu yerda vaqt bo'yicha bo'laklar ko'rinadi.
                </p>
              ) : (
                <div className="space-y-3">
                  {segments.map((segment, index) => {
                    const aiScore = typeof segment.ai_score === "number" ? Math.round(segment.ai_score * 100) : null;
                    const realScore = typeof segment.real_score === "number" ? Math.round(segment.real_score * 100) : null;
                    const risk = String(segment.risk || "unknown");
                    const color = risk === "high" ? "#ef4444" : risk === "medium" ? "#f59e0b" : "#22c55e";
                    return (
                      <div key={`${segment.index || index}`} className="rounded-xl border theme-border bg-white/[0.03] p-3">
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="text-sm font-black theme-text-primary">
                              {formatTime(Number(segment.start_seconds || 0))} - {formatTime(Number(segment.end_seconds || 0))}
                            </p>
                            <p className="mt-1 text-xs theme-text-secondary">
                              Label: {formatUnknown(segment.label)} | Confidence: {formatUnknown(segment.confidence)}
                            </p>
                          </div>
                          <div className="text-sm font-black" style={{ color }}>
                            {aiScore == null ? "Noma'lum" : `${aiScore}% AI/Spoof`}
                          </div>
                        </div>
                        <div className="mt-3 grid gap-2 sm:grid-cols-2">
                          <SegmentBar label="AI/Spoof" value={aiScore} color={color} />
                          <SegmentBar label="Real ovoz" value={realScore} color="#22c55e" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Har bir audio model natijasi</p>
              <div className="mt-4 grid gap-3">
                {audioModels.length === 0 ? (
                  <p className="text-sm theme-text-secondary">Audio model natijalari saqlanmagan.</p>
                ) : (
                  audioModels.map((model, index) => (
                    <div key={`${String(model.model_id || model.name)}-${index}`} className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-sm font-black theme-text-primary">{String(model.name || model.model_id)}</p>
                          <p className="mt-1 text-xs theme-text-secondary">{translateVerdict(String(model.verdict || model.error || "Natija qayd etildi."))}</p>
                          <div className="mt-3 flex flex-wrap gap-2 text-[11px] theme-text-muted">
                            {typeof model.ai_score === "number" && <span>AI/Spoof: {Math.round(model.ai_score * 100)}%</span>}
                            {typeof model.real_score === "number" && <span>Real: {Math.round(model.real_score * 100)}%</span>}
                            {model.confidence != null && <span>Ishonch: {translateConfidence(String(model.confidence))}</span>}
                          </div>
                        </div>
                        <span className={`text-xs font-black ${isReadyStatus(String(model.status)) ? "text-green-400" : "text-amber-400"}`}>
                          {translateModelStatus(String(model.status))}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Aniqlangan audio belgilar</p>
              <div className="mt-4 grid gap-2">
                {detectedSigns.map((sign, index) => (
                  <div key={index} className="rounded-xl border theme-border bg-white/[0.03] p-3 text-sm theme-text-secondary">
                    {translateSign(sign)}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.06] p-5">
              <p className="text-sm font-black text-amber-300">Audio cheklovlar</p>
              <div className="mt-3 grid gap-2">
                {(limitations.length ? limitations : [
                  "Audio model natijasi avtomatik skrining signali, yakuniy sud-ekspert xulosasi emas.",
                  "Past sifat, shovqin, qayta siqish yoki qisqa audio confidence qiymatiga ta'sir qilishi mumkin.",
                  "Muhim huquqiy holatda original audio manbasi va yozib olingan qurilma mustaqil tekshirilsin.",
                ]).map((item, index) => (
                  <p key={index} className="text-sm leading-7 theme-text-secondary">{translateLimitation(item)}</p>
                ))}
              </div>
            </section>
          </div>

          <aside className="space-y-4">
            <section className="card p-5">
              <p className="text-sm font-black theme-text-primary">Eksport</p>
              <div className="mt-4 grid gap-2">
                <a href={`/api/cases/${report.id}/report.docx`} className="btn btn-cyan justify-center">
                  <Download className="h-4 w-4" />
                  Audio DOCX hisobot
                </a>
                <a href={`/api/cases/${report.id}/report`} className="btn btn-ghost justify-center">
                  <FileJson className="h-4 w-4" />
                  JSON report
                </a>
              </div>
            </section>

            <ReportQrCard reportId={report.id} />

            <section className="card p-5">
              <div className="mb-4 flex items-center gap-2">
                <Fingerprint className="h-4 w-4 text-green-400" />
                <p className="text-sm font-black theme-text-primary">Dalil zanjiri</p>
              </div>
              <HashRow label="SHA-256" value={report.file_hash} />
              <HashRow label="Yuklangan vaqt" value={formatDate(report.uploaded_at)} />
              <HashRow label="Report yaratilgan vaqt" value={formatDate(fullReport?.created_at || report.uploaded_at)} />
              <HashRow label="Model versiyasi" value={report.model_version || "Noma'lum"} />
              <HashRow label="Dalil fayli" value={report.original_filename} />
            </section>

            <section className="card p-5">
              <p className="text-sm font-black theme-text-primary">Qisqa audio xulosa</p>
              <div className="mt-4 space-y-3 text-xs leading-6 theme-text-secondary">
                <p>Fayl: {report.original_filename}</p>
                <p>Natija: {verdict}</p>
                <p>Real ovoz: {realVoice}%</p>
                <p>AI/Spoof ovoz: {aiVoice}%</p>
                <p>Speaker spoof: {spoof}%</p>
              </div>
            </section>
          </aside>
        </div>
      </section>
    </div>
  );
}

function VideoReportDetail({
  report,
  fullReport,
  modelResults,
  detectedSigns,
  limitations,
}: {
  report: CaseDetail;
  fullReport: FullReport | null;
  modelResults: Array<Record<string, unknown>>;
  detectedSigns: string[];
  limitations: string[];
}) {
  const scores = fullReport?.scores || {};
  const realVideo = Math.round(((scores.video_real_score ?? report.real_score ?? 0) as number) * 100);
  const fakeVideo = Math.round(((scores.video_fake_score ?? report.ai_score ?? 0) as number) * 100);
  const faceRisk = Math.round(((scores.face_manipulation_score ?? report.manipulated_score ?? 0) as number) * 100);
  const temporalRisk = Math.round(((scores.temporal_artifact_score ?? 0) as number) * 100);
  const highRisk = fakeVideo >= realVideo;
  const verdict = highRisk ? "Deepfake yoki manipulyatsiya ehtimoli bor" : "Real video ehtimoli yuqori";
  const verdictColor = highRisk ? "#ef4444" : "#22c55e";
  const genconvit = modelResults.find((model) => model.model_id === "xabarnavis_video_0_1");
  const naman = modelResults.find((model) => model.model_id === "xabarnavis_video_0_2");
  const spectraTrack = modelResults.find((model) => model.model_id === "xabarnavis_audio_0_7_video_track");
  const audioForensics = fullReport?.audio_deepfake_forensics || {};
  const technicalMetadata = fullReport?.technical_metadata || {};
  const ensemble = fullReport?.ensemble || {};
  const videoModels = modelResults.length ? modelResults : [
    {
      model_id: "xabarnavis_video_0_1",
      name: "Xabarnavis Video 0.1 GenConViT",
      status: "installed needs dependencies",
      verdict: "GenConViT registered but dependencies or weights are not ready.",
    },
    {
      model_id: "xabarnavis_video_0_2",
      name: "Xabarnavis Video 0.2 Naman712",
      status: "requires huggingface access",
      verdict: "Naman712 gated Hugging Face model requires access token.",
    },
  ];
  const guideRows = videoModels
    .map((model) => {
      const details = (model.details && typeof model.details === "object" ? model.details : {}) as Record<string, unknown>;
      const commands = [
        details.download_command,
        details.install_command,
      ].filter(Boolean).map(String);
      return {
        name: String(model.name || model.model_id || "Video model"),
        status: String(model.status || "unknown"),
        error: String(model.error || ""),
        commands,
        note: String(details.model_access || details.architecture || details.task || ""),
      };
    })
    .filter((item) => !isReadyStatus(item.status) || item.commands.length || item.note);

  return (
    <div className="space-y-5 p-4 lg:p-6">
      <section className="overflow-hidden rounded-2xl border theme-border bg-[var(--bg-card)] shadow-[0_24px_70px_rgba(0,0,0,0.20)]">
        <header className="border-b theme-border bg-[radial-gradient(circle_at_10%_20%,rgba(168,85,247,0.18),transparent_28rem),linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02))] p-5 lg:p-7">
          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px] xl:items-center">
            <div className="flex gap-4">
              <div className="grid h-14 w-14 flex-shrink-0 place-items-center rounded-2xl border border-purple-400/30 bg-purple-400/10">
                <Video className="h-7 w-7 text-purple-400" />
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-purple-400">
                  Xabarnavis AI video forensic hisobot
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-3">
                  <h2 className="text-2xl font-black theme-text-primary">{verdict}</h2>
                  <span className="rounded-full border px-3 py-1 text-xs font-black" style={{ borderColor: `${verdictColor}55`, color: verdictColor, background: `${verdictColor}14` }}>
                    Video qaror
                  </span>
                </div>
                <p className="mt-2 max-w-3xl text-sm leading-6 theme-text-secondary">
                  Ushbu hisobot video fayl uchun yaratilgan. Natija GenConViT, Naman712 ResNext50 + LSTM va fallback video signallari orqali bazaga saqlandi.
                  Dalil SHA-256 orqali identifikatsiya qilingan va login qilingan foydalanuvchi hisobiga bog'langan.
                </p>
              </div>
            </div>
            <div className="grid gap-2 sm:grid-cols-3 xl:grid-cols-1">
              <CompactScore label="Deepfake ehtimoli" value={fakeVideo} color={highRisk ? "#ef4444" : "#22c55e"} />
              <CompactScore label="Real video" value={realVideo} color="#22c55e" />
              <CompactScore label="Yuz manipulyatsiyasi" value={faceRisk} color="#f59e0b" />
            </div>
          </div>
        </header>

        <div className="grid gap-5 p-5 lg:grid-cols-[minmax(0,1fr)_360px] lg:p-7">
          <div className="space-y-5">
            <section className="rounded-2xl border theme-border bg-[radial-gradient(circle_at_20%_0%,rgba(168,85,247,0.12),transparent_24rem),rgba(255,255,255,0.025)] p-5">
              <div className="mb-4 flex items-center gap-2">
                <Shield className="h-4 w-4 text-purple-400" />
                <h3 className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Video tahlil xulosasi</h3>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <InfoRow label="Media turi" value="Video" />
                <InfoRow label="Asosiy model 0.1" value={String(genconvit?.name || "Xabarnavis Video 0.1 GenConViT")} />
                <InfoRow label="GenConViT status" value={translateModelStatus(String(genconvit?.status || "not registered"))} />
                <InfoRow label="Naman712 status" value={translateModelStatus(String(naman?.status || "not registered"))} />
                <InfoRow label="Spectra audio status" value={translateModelStatus(String(spectraTrack?.status || audioForensics.status || "not available"))} />
                <InfoRow label="Deepfake score" value={`${fakeVideo}%`} />
                <InfoRow label="Real video score" value={`${realVideo}%`} />
                <InfoRow label="Temporal artefakt" value={`${temporalRisk}%`} />
                <InfoRow label="Ishonch darajasi" value={translateConfidence(report.confidence || "Noma'lum")} />
              </div>
              <p className="mt-4 text-sm leading-7 theme-text-secondary">
                Video hisobot EXIF/ELA rasm qatlamlarini ishlatmaydi. Bu yerda kadrlar, yuz izchilligi, temporal o'zgarishlar,
                model statuslari va deepfake ehtimoli asosiy forensic dalil sifatida ko'rsatiladi.
              </p>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Audio Deepfake Forensics</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <InfoRow label="Audio ajratildi" value={audioForensics.audio_extracted ? "Ha" : "Yo'q / mavjud emas"} />
                <InfoRow label="Sample rate" value={audioForensics.sample_rate_hz ? `${audioForensics.sample_rate_hz} Hz` : "Mavjud emas"} />
                <InfoRow label="Kanallar" value={audioForensics.channels ? String(audioForensics.channels) : "Mavjud emas"} />
                <InfoRow label="Spectra fake score" value={typeof audioForensics.spectra_fake_score === "number" ? `${Math.round(audioForensics.spectra_fake_score * 100)}%` : "Not available"} />
                <InfoRow label="Spectra real score" value={typeof audioForensics.spectra_real_score === "number" ? `${Math.round(audioForensics.spectra_real_score * 100)}%` : "Not available"} />
                <InfoRow label="Audio verdict" value={translateVerdict(String(audioForensics.audio_verdict || "not available"))} />
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Technical Metadata</p>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <InfoRow label="Duration" value={technicalMetadata.duration_seconds != null ? `${technicalMetadata.duration_seconds} sec` : "Mavjud emas"} />
                <InfoRow label="FPS" value={technicalMetadata.fps != null ? String(technicalMetadata.fps) : "Mavjud emas"} />
                <InfoRow label="Resolution" value={technicalMetadata.resolution != null ? String(technicalMetadata.resolution) : "Mavjud emas"} />
                <InfoRow label="Codec" value={technicalMetadata.codec != null ? String(technicalMetadata.codec) : "Mavjud emas"} />
                <InfoRow label="Bitrate" value={technicalMetadata.bitrate != null ? String(technicalMetadata.bitrate) : "Mavjud emas"} />
                <InfoRow label="Audio stream" value={technicalMetadata.has_audio === true ? "Bor" : technicalMetadata.has_audio === false ? "Yo'q" : "Noma'lum"} />
              </div>
              {ensemble.formula && (
                <p className="mt-4 rounded-xl border theme-border bg-white/[0.03] p-3 text-xs leading-6 theme-text-secondary">
                  Ensemble: {ensemble.formula}
                </p>
              )}
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Har bir video model natijasi</p>
              <div className="mt-4 grid gap-3">
                {videoModels.map((model, index) => {
                  const details = (model.details && typeof model.details === "object" ? model.details : {}) as Record<string, unknown>;
                  return (
                    <div key={`${String(model.model_id || model.name)}-${index}`} className="rounded-2xl border theme-border bg-white/[0.03] p-4">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <p className="text-sm font-black theme-text-primary">{String(model.name || model.model_id)}</p>
                          <p className="mt-1 text-xs theme-text-secondary">{translateVerdict(String(model.verdict || model.error || "Natija qayd etildi."))}</p>
                          <div className="mt-3 flex flex-wrap gap-2 text-[11px] theme-text-muted">
                            {typeof model.ai_score === "number" && <span>Deepfake: {Math.round(model.ai_score * 100)}%</span>}
                            {typeof model.real_score === "number" && <span>Real: {Math.round(model.real_score * 100)}%</span>}
                            {model.confidence != null && <span>Ishonch: {translateConfidence(String(model.confidence))}</span>}
                          </div>
                          {model.error != null && <p className="mt-2 text-xs font-semibold text-amber-400">{String(model.error)}</p>}
                          {details.architecture != null && <p className="mt-2 text-xs theme-text-secondary">Arxitektura: {String(details.architecture)}</p>}
                        </div>
                        <span className={`text-xs font-black ${isReadyStatus(String(model.status)) ? "text-green-400" : "text-amber-400"}`}>
                          {translateModelStatus(String(model.status))}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Modelni ishga tayyorlash yo'riqnomasi</p>
              <div className="mt-4 grid gap-3">
                {guideRows.map((item, index) => (
                  <div key={`${item.name}-${index}`} className="rounded-xl border theme-border bg-black/[0.04] p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-sm font-black theme-text-primary">{item.name}</p>
                      <span className={`text-xs font-black ${isReadyStatus(item.status) ? "text-green-400" : "text-amber-400"}`}>
                        {translateModelStatus(item.status)}
                      </span>
                    </div>
                    {item.note && <p className="mt-2 text-xs leading-6 theme-text-secondary">{item.note}</p>}
                    {item.error && <p className="mt-2 text-xs font-semibold text-amber-400">{item.error}</p>}
                    {item.commands.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {item.commands.map((command) => (
                          <code key={command} className="block overflow-x-auto rounded-lg border theme-border bg-black/20 px-3 py-2 text-xs theme-text-primary">
                            {command}
                          </code>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border theme-border p-5">
              <p className="text-sm font-black uppercase tracking-[0.12em] theme-text-muted">Aniqlangan video belgilar</p>
              <div className="mt-4 grid gap-2">
                {detectedSigns.map((sign, index) => (
                  <div key={index} className="rounded-xl border theme-border bg-white/[0.03] p-3 text-sm theme-text-secondary">
                    {translateSign(sign)}
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-amber-400/20 bg-amber-400/[0.06] p-5">
              <p className="text-sm font-black text-amber-300">Video cheklovlar</p>
              <div className="mt-3 grid gap-2">
                {(limitations.length ? limitations : [
                  "Video model natijasi avtomatik skrining signali, yakuniy sud-ekspert xulosasi emas.",
                  "Past sifat, kuchli kompressiya, yuz ko'rinmasligi yoki kesilgan video confidence qiymatiga ta'sir qilishi mumkin.",
                  "Muhim huquqiy holatda original video, platforma metadatasi va alohida ekspert ko'rigi bilan solishtiring.",
                ]).map((item, index) => (
                  <p key={index} className="text-sm leading-7 theme-text-secondary">{translateLimitation(item)}</p>
                ))}
              </div>
            </section>
          </div>

          <aside className="space-y-4">
            <section className="card p-5">
              <p className="text-sm font-black theme-text-primary">Eksport</p>
              <div className="mt-4 grid gap-2">
                <a href={`/api/cases/${report.id}/report.docx`} className="btn btn-cyan justify-center">
                  <Download className="h-4 w-4" />
                  Video DOCX hisobot
                </a>
                <a href={`/api/cases/${report.id}/report`} className="btn btn-ghost justify-center">
                  <FileJson className="h-4 w-4" />
                  JSON report
                </a>
              </div>
            </section>

            <ReportQrCard reportId={report.id} />

            <section className="card p-5">
              <div className="mb-4 flex items-center gap-2">
                <Fingerprint className="h-4 w-4 text-purple-400" />
                <p className="text-sm font-black theme-text-primary">Dalil zanjiri</p>
              </div>
              <HashRow label="SHA-256" value={report.file_hash} />
              <HashRow label="Yuklangan vaqt" value={formatDate(report.uploaded_at)} />
              <HashRow label="Report yaratilgan vaqt" value={formatDate(fullReport?.created_at || report.uploaded_at)} />
              <HashRow label="Model versiyasi" value={report.model_version || "Noma'lum"} />
              <HashRow label="Dalil fayli" value={report.original_filename} />
            </section>

            <section className="card p-5">
              <p className="text-sm font-black theme-text-primary">Qisqa video xulosa</p>
              <div className="mt-4 space-y-3 text-xs leading-6 theme-text-secondary">
                <p>Fayl: {report.original_filename}</p>
                <p>Natija: {verdict}</p>
                <p>Real video: {realVideo}%</p>
                <p>Deepfake ehtimoli: {fakeVideo}%</p>
                <p>Yuz manipulyatsiyasi: {faceRisk}%</p>
              </div>
            </section>
          </aside>
        </div>
      </section>
    </div>
  );
}

function getFinalDecision(ai: number, real: number, hasPrimaryModel: boolean) {
  const source = hasPrimaryModel
    ? "Yakuniy qaror faqat Xabarnavis 0.5 modeli natijasidan olindi."
    : "Bu eski hisobotda Xabarnavis 0.5 natijasi topilmadi, shuning uchun saqlangan AI/real score ishlatildi.";
  if (ai >= real) {
    return {
      label: "AI rasm",
      color: "#ef4444",
      reason: `${source} AI ehtimoli ${ai}%, real ehtimoli ${real}%.`,
    };
  }
  return {
    label: "Real rasm",
    color: "#22c55e",
    reason: `${source} Real ehtimoli ${real}%, AI ehtimoli ${ai}%.`,
  };
}

function getLegacyFinalDecision(ai: number, real: number, manip: number) {
  if (ai >= 55 && manip >= 45) {
    return {
      label: "Manipulyatsiya qilingan AI rasm",
      color: "#ef4444",
      reason: `AI ehtimoli ${ai}% va manipulyatsiya signali ${manip}% boâ€˜lgani uchun rasm AI hamda tahrir belgilariga ega deb baholandi.`,
    };
  }
  if (manip >= ai && manip >= real) {
    return {
      label: "Manipulyatsiya qilingan rasm",
      color: "#f59e0b",
      reason: `Eng kuchli signal manipulyatsiya (${manip}%). Shu sababli asosiy qaror tahrir/manipulyatsiya ehtimoli tomonga berildi.`,
    };
  }
  if (ai >= real && ai >= manip) {
    return {
      label: "AI rasm",
      color: "#ef4444",
      reason: `Eng kuchli signal AI ehtimoli (${ai}%). Shu sababli rasm AI orqali yaratilgan boâ€˜lishi mumkin deb baholandi.`,
    };
  }
  return {
    label: "Real rasm",
    color: "#22c55e",
    reason: `Eng kuchli signal haqiqiylik (${real}%). Shu sababli rasm real kamera/foto manbasiga yaqin deb baholandi.`,
  };
}

function minicpmExpertText(
  reasoning: FullReport["image_reasoning_uz"] extends infer T
    ? T extends { minicpm_v_2_6_int4?: infer R }
      ? R
      : undefined
    : undefined,
  fallbackSummary: string | undefined,
  reportId: number,
) {
  if (reasoning?.reasoning_uz) {
    return reasoning.reasoning_uz;
  }
  if (reasoning?.fallback_reasoning_uz) {
    return reasoning.fallback_reasoning_uz;
  }
  if (fallbackSummary) {
    return fallbackSummary;
  }
  return `CASE-${reportId} bo'yicha reasoning natijasi hali mavjud emas.`;
}

function HashRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="mb-3 last:mb-0">
      <p className="text-xs font-bold theme-text-muted">{label}</p>
      <p className="mt-1 break-all font-mono text-xs theme-text-primary">{value}</p>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border theme-border bg-white/[0.03] p-3">
      <p className="text-[11px] font-bold uppercase tracking-[0.12em] theme-text-muted">{label}</p>
      <p className="mt-2 break-words text-sm font-semibold theme-text-primary">{value}</p>
    </div>
  );
}

function ForensicImage({ title, src, description, badge }: { title: string; src: string; description: string; badge: string }) {
  return (
    <figure className="overflow-hidden rounded-xl border theme-border bg-black/[0.08]">
      <div className="aspect-[4/3] bg-black/20">
        <img src={src} alt={title} className="h-full w-full object-contain" />
      </div>
      <figcaption className="border-t theme-border p-3">
        <div className="flex items-start justify-between gap-2">
          <p className="text-xs font-black uppercase tracking-[0.1em] theme-text-primary">{title}</p>
          <span className="rounded-full border border-cyan-400/25 bg-cyan-400/10 px-2 py-0.5 text-[10px] font-black text-cyan-300">
            {badge}
          </span>
        </div>
        <p className="mt-2 text-xs leading-5 theme-text-secondary">{description}</p>
      </figcaption>
    </figure>
  );
}

function ReportQrCard({ reportId }: { reportId: number }) {
  const pathname = usePathname();
  const locale = localeFromPathname(pathname);
  const publicUrl = reportPublicUrl(reportId, locale);
  const qrUrl = reportQrCodeUrl(reportId, locale, 190);

  return (
    <section className="card p-5">
      <div className="flex items-center gap-2">
        <QrCode className="h-4 w-4 text-[var(--accent-cyan,#00d4ff)]" />
        <p className="text-sm font-black theme-text-primary">Individual QR code</p>
      </div>
      <div className="mt-4 rounded-2xl border theme-border bg-white p-3">
        <img src={qrUrl} alt={`CASE-${reportId} QR code`} className="mx-auto h-44 w-44" />
      </div>
      <p className="mt-3 break-all rounded-xl border theme-border bg-white/[0.03] p-3 font-mono text-[11px] theme-text-secondary">
        {publicUrl}
      </p>
      <a href={qrUrl} download={`xabarnavis-case-${reportId}-qr.png`} className="btn btn-ghost mt-3 justify-center text-xs">
        QR yuklab olish
      </a>
    </section>
  );
}

function AudioArtifactImage({ title, src, description }: { title: string; src: string; description: string }) {
  const [failed, setFailed] = useState(false);
  return (
    <figure className="overflow-hidden rounded-xl border theme-border bg-black/[0.08]">
      <div className="min-h-[180px] bg-black/20">
        {failed ? (
          <div className="grid min-h-[180px] place-items-center p-6 text-center">
            <div>
              <Waves className="mx-auto h-8 w-8 text-green-400/60" />
              <p className="mt-3 text-sm font-bold theme-text-secondary">Vizual artifact yangi audio analizdan keyin yaratiladi.</p>
            </div>
          </div>
        ) : (
          <img src={src} alt={title} className="h-full w-full object-contain" onError={() => setFailed(true)} />
        )}
      </div>
      <figcaption className="border-t theme-border p-3">
        <p className="text-xs font-black uppercase tracking-[0.1em] theme-text-primary">{title}</p>
        <p className="mt-2 text-xs leading-5 theme-text-secondary">{description}</p>
      </figcaption>
    </figure>
  );
}

function parseModels(value?: string | null): Array<Record<string, string | number | null>> {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("uz-UZ");
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) return "0:00";
  const safeSeconds = Math.max(0, Math.round(seconds));
  const minutes = Math.floor(safeSeconds / 60);
  const remaining = safeSeconds % 60;
  return `${minutes}:${String(remaining).padStart(2, "0")}`;
}

function formatExifDate(value: unknown) {
  if (typeof value !== "string" || !value) return "Noma'lum";
  const normalized = value.replace(/^(\d{4}):(\d{2}):(\d{2})/, "$1-$2-$3");
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? cleanText(value) : date.toLocaleString("uz-UZ");
}

function formatUnknown(value: unknown) {
  if (value === undefined || value === null || value === "") return "Noma'lum";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
  if (typeof value === "boolean") return value ? "Ha" : "Yo'q";
  return String(value);
}

function formatScore(value: unknown) {
  if (typeof value !== "number") return "Noma'lum";
  return `${Math.round(value * 100)}%`;
}

function cleanText(value: string) {
  return value.replace(/\0/g, "").trim() || "Noma'lum";
}

function translateConfidence(value?: string | null) {
  if (!value) return "Noma'lum";
  const map: Record<string, string> = {
    High: "Yuqori",
    Medium: "O'rtacha",
    Low: "Past",
  };
  return map[value] || value;
}

function translateMediaType(value?: string | null) {
  const map: Record<string, string> = {
    image: "Rasm",
    video: "Video",
    audio: "Audio",
    text: "Matn",
  };
  return value ? map[value] || value : "Noma'lum";
}

function translateStatus(value?: string | null) {
  const map: Record<string, string> = {
    uploaded: "Yuklangan",
    analyzed: "Tahlil qilingan",
    error: "Xatolik",
  };
  return value ? map[value] || value : "Noma'lum";
}

function translateModelStatus(value: string) {
  const map: Record<string, string> = {
    ready: "tayyor",
    "ready dataset": "dataset tayyor",
    "dataset folder ready": "dataset papkasi tayyor",
    "ready local": "local model tayyor",
    "ready downloads on first use": "birinchi ishlatishda yuklaydi",
    error: "xatolik",
    unavailable: "mavjud emas",
    "installed needs dependencies": "dependency kerak",
    not_installed: "o'rnatilmagan",
    installed_no_adapter: "adapter ulanmagan",
    installed_needs_adapter: "adapter kerak",
    unknown: "noma'lum",
  };
  return map[value] || value;
}

function isReadyStatus(value: string) {
  return ["ready", "ready local", "ready dataset", "dataset folder ready"].includes(value);
}

function translateVerdict(value?: string | null) {
  if (!value) return "Tahlil yakunlanmagan";
  const lower = value.toLowerCase();
  if (lower.includes("likely real camera") || lower.includes("real camera/photo-like")) {
    return "Ehtimol haqiqiy kamera rasmi";
  }
  if (lower.includes("likely real human voice") || lower.includes("likely real voice")) {
    return "Ehtimol real inson ovozi";
  }
  if (lower.includes("likely ai-generated or deepfake voice")) {
    return "AI yaratilgan yoki deepfake ovoz ehtimoli bor";
  }
  if (lower.includes("synthetic or spoofed voice") || lower.includes("spoof audio") || lower.includes("spoofed voice")) {
    return "Synthetic yoki spoof audio ehtimoli bor";
  }
  if (lower.includes("fallback signal used")) {
    return "Jabberjay tayyor bo'lmagani uchun fallback audio signal ishlatilgan";
  }
  if (lower.includes("kaggle fake vs real speech dataset")) {
    return "Kaggle fake-vs-real speech dataset Xabarnavis Audio 0.4 uchun training/evaluation resurs sifatida qo'shilgan. Bu bevosita inference modeli emas.";
  }
  if (lower.includes("supporting heuristic signal")) {
    return "Qo'shimcha heuristic audio signal";
  }
  if (lower.includes("highly likely ai") || lower.includes("synthetic") || lower.includes("ai-generated")) {
    return "AI orqali yaratilgan boâ€˜lishi ehtimoli yuqori";
  }
  if (lower.includes("possibly ai")) {
    return "AI orqali yaratilgan boâ€˜lishi mumkin";
  }
  if (lower.includes("manipulated") || lower.includes("edited")) {
    return "Tahrirlangan yoki manipulyatsiya qilingan boâ€˜lishi mumkin";
  }
  if (lower.includes("failed during inference")) {
    return "Model ishga tushirish jarayonida xatolik berdi";
  }
  if (lower.includes("registered but not ready")) {
    return "Model roâ€˜yxatda bor, lekin inference uchun tayyor emas";
  }
  return value;
}

function translateSign(value: string) {
  const lower = value.toLowerCase();
  if (lower.includes("jabberjay synthetic voice detector adapter was executed")) return "Jabberjay synthetic voice detector adapteri ishga tushirildi.";
  if (lower.includes("jabberjay status")) return value.replace("Jabberjay status:", "Jabberjay holati:");
  if (lower.includes("xabarnavis audio 0.4 dataset status")) return value.replace("Xabarnavis Audio 0.4 dataset status:", "Xabarnavis Audio 0.4 dataset holati:");
  if (lower.includes("audio was hashed")) return "Audio dalil hash qilindi va foydalanuvchi report tarixiga saqlandi.";
  if (lower.includes("jabberjay note")) return value.replace("Jabberjay note:", "Jabberjay izohi:");
  if (lower.includes("camera model metadata is present")) return "Kamera modeli metadata ichida mavjud.";
  if (lower.includes("software metadata detected")) return `Dasturiy metadata aniqlangan: ${cleanText(value.split(":").slice(1).join(":"))}.`;
  if (lower.includes("localized noise inconsistency")) return "Rasmning ayrim lokal hududlarida shovqin nomuvofiqligi bor.";
  if (lower.includes("combined indicators are consistent with a real camera photo")) return "Birlashtirilgan indikatorlar haqiqiy kamera rasmi bilan mos keladi.";
  if (lower.includes("selected ai model scores were included")) return "Tanlangan AI model ballari yakuniy fusion qaroriga qoâ€˜shilgan.";
  return value;
}

function translateLimitation(value: string) {
  const lower = value.toLowerCase();
  if (lower.includes("heuristic signals")) return "MVP bosqichida ayrim signallar heuristic usulda baholanadi; yanada aniq natija uchun qoâ€˜shimcha oâ€˜qitilgan modellar ulanadi.";
  if (lower.includes("missing exif")) return "EXIF metadata yoâ€˜qligi yakka holda AI generatsiya yoki manipulyatsiya isboti emas.";
  if (lower.includes("social media compression")) return "Ijtimoiy tarmoq kompressiyasi provenance va forensic artefaktlarni oâ€˜zgartirishi mumkin.";
  return value;
}



