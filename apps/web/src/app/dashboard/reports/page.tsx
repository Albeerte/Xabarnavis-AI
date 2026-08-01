"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  Eye,
  FileBarChart2,
  FileText,
  Filter,
  ImageIcon,
  Mic,
  QrCode,
  Search,
  ShieldCheck,
  Video,
} from "lucide-react";
import { usePathname } from "next/navigation";
import { localeFromPathname, reportPublicUrl, reportQrCodeUrl } from "@/lib/qr";

type MediaType = "image" | "video" | "audio" | "text";

type CaseSummary = {
  id: number;
  original_filename: string;
  file_hash: string;
  status: string;
  media_type: MediaType;
  uploaded_at: string;
  real_score?: number | null;
  ai_score?: number | null;
  manipulated_score?: number | null;
  final_verdict?: string | null;
  confidence?: string | null;
  model_results_json?: string | null;
  model_version?: string | null;
};

const TYPE_META = {
  image: { label: "Rasm", icon: ImageIcon, color: "var(--accent-cyan, #00d4ff)" },
  video: { label: "Video", icon: Video, color: "#a78bfa" },
  audio: { label: "Audio", icon: Mic, color: "#22c55e" },
  text: { label: "Matn", icon: FileText, color: "#f59e0b" },
} satisfies Record<MediaType, { label: string; icon: typeof ImageIcon; color: string }>;

export default function ReportsPage() {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<"barchasi" | MediaType>("barchasi");
  const pathname = usePathname();
  const locale = localeFromPathname(pathname);

  useEffect(() => {
    let ignore = false;

    async function loadCases() {
      try {
        const response = await fetch("/api/cases?limit=200", { credentials: "include" });
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        if (!ignore) setCases(data.cases || []);
      } catch {
        if (!ignore) setError("Analizlar ro'yxatini olishda xatolik yuz berdi.");
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    loadCases();
    return () => {
      ignore = true;
    };
  }, []);

  const stats = useMemo(() => {
    const analyzed = cases.filter((item) => item.status === "analyzed");
    const risky = cases.filter((item) => Math.max(item.ai_score || 0, item.manipulated_score || 0) >= 0.6).length;
    const avgReal = Math.round((cases.reduce((sum, item) => sum + (item.real_score || 0), 0) / Math.max(cases.length, 1)) * 100);
    return [
      { label: "Jami analiz", value: cases.length, hint: "Faqat sizning hisobingiz", tone: "cyan" },
      { label: "Yakunlangan", value: analyzed.length, hint: "Bazaga saqlangan tahlillar", tone: "green" },
      { label: "Yuqori risk", value: risky, hint: "AI yoki manipulyatsiya signali", tone: "red" },
      { label: "O'rtacha real", value: `${avgReal}%`, hint: "Sizning analizlaringiz bo'yicha", tone: "amber" },
    ];
  }, [cases]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return cases.filter((item) => {
      const matchesSearch =
        !query ||
        item.original_filename.toLowerCase().includes(query) ||
        String(item.id).includes(query) ||
        (item.final_verdict || "").toLowerCase().includes(query);
      const matchesType = filterType === "barchasi" || item.media_type === filterType;
      return matchesSearch && matchesType;
    });
  }, [cases, filterType, search]);

  return (
    <div className="space-y-6 p-4 lg:p-6">
      <section className="overflow-hidden rounded-2xl border theme-border bg-[radial-gradient(circle_at_12%_18%,rgba(0,212,255,0.18),transparent_26rem),linear-gradient(135deg,rgba(255,255,255,0.075),rgba(255,255,255,0.025))] p-5 shadow-[0_24px_70px_rgba(0,0,0,0.22)] lg:p-7">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent-cyan,#00d4ff)]">
              Dashboard / Analizlar
            </p>
            <h1 className="mt-3 text-3xl font-black tracking-tight theme-text-primary lg:text-4xl">
              Mening analizlarim
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 theme-text-secondary">
              Har bir yuklangan fayl barcha mavjud Xabarnavis modullari bilan tekshiriladi va natija faqat sizning hisobingizga bog'lanib bazaga yoziladi.
            </p>
          </div>
          <Link href="/dashboard/image-analyzer" className="btn btn-cyan h-11 justify-center">
            <ShieldCheck className="h-4 w-4" />
            Yangi analiz
          </Link>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((item) => (
            <div key={item.label} className="rounded-2xl border theme-border bg-black/10 p-4 backdrop-blur">
              <p className="text-xs font-bold uppercase tracking-[0.12em] theme-text-muted">{item.label}</p>
              <p className={`mt-3 text-3xl font-black ${toneClass(item.tone)}`}>{item.value}</p>
              <p className="mt-1 text-xs theme-text-muted">{item.hint}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card p-4 lg:p-5">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="relative min-w-0 flex-1 xl:max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 theme-text-muted" />
            <input
              type="text"
              placeholder="Fayl nomi, case ID yoki natija bo'yicha qidirish..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="xinput h-11 pl-10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-2 rounded-full border theme-border px-3 py-2 text-xs font-bold theme-text-muted">
              <Filter className="h-3.5 w-3.5" />
              Filter
            </span>
            {(["barchasi", "image", "video", "audio", "text"] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`rounded-full border px-4 py-2 text-xs font-bold transition ${
                  filterType === type
                    ? "border-[var(--accent-cyan,#00d4ff)] bg-[var(--accent-cyan,#00d4ff)]/10 text-[var(--accent-cyan,#00d4ff)]"
                    : "theme-border theme-text-secondary hover:bg-white/5"
                }`}
              >
                {type === "barchasi" ? "Barchasi" : TYPE_META[type].label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {loading ? (
        <section className="card grid min-h-72 place-items-center p-8 text-center">
          <div>
            <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            <p className="text-sm font-bold theme-text-secondary">Analizlar yuklanmoqda...</p>
          </div>
        </section>
      ) : error ? (
        <section className="card grid min-h-72 place-items-center p-8 text-center">
          <p className="text-sm font-bold text-red-400">{error}</p>
        </section>
      ) : filtered.length === 0 ? (
        <section className="card grid min-h-80 place-items-center p-8 text-center">
          <div>
            <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl border theme-border bg-white/5">
              <FileBarChart2 className="h-8 w-8 theme-text-muted" />
            </div>
            <h2 className="mt-5 text-xl font-black theme-text-primary">Analiz topilmadi</h2>
            <p className="mt-2 text-sm theme-text-secondary">Yangi rasm yuklang yoki qidiruv/filter shartlarini o'zgartiring.</p>
            <Link href="/dashboard/image-analyzer" className="btn btn-cyan mt-5">
              Birinchi analizni boshlash
            </Link>
          </div>
        </section>
      ) : (
        <section className="grid gap-4">
          {filtered.map((item) => (
            <AnalysisCard key={item.id} item={item} locale={locale} />
          ))}
        </section>
      )}
    </div>
  );
}

function AnalysisCard({ item, locale }: { item: CaseSummary; locale: string }) {
  const type = TYPE_META[item.media_type] || TYPE_META.image;
  const Icon = type.icon;
  const ai = Math.round((item.ai_score || 0) * 100);
  const real = Math.round((item.real_score || 0) * 100);
  const manip = Math.round((item.manipulated_score || 0) * 100);
  const highRisk = Math.max(ai, manip) >= 60;
  const models = parseModels(item.model_results_json);
  const publicUrl = reportPublicUrl(item.id, locale);
  const qrUrl = reportQrCodeUrl(item.id, locale, 132);

  return (
    <article className="group overflow-hidden rounded-2xl border theme-border bg-[var(--bg-card)] shadow-[0_18px_45px_rgba(0,0,0,0.16)] transition hover:border-[var(--accent-cyan,#00d4ff)]/45 hover:shadow-[0_24px_70px_rgba(0,212,255,0.10)]">
      <div className="grid gap-0 lg:grid-cols-[minmax(0,1.25fr)_320px]">
        <div className="p-4 lg:p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div className="flex min-w-0 gap-4">
              <div
                className="grid h-12 w-12 flex-shrink-0 place-items-center rounded-2xl border"
                style={{ color: type.color, borderColor: `${type.color}40`, background: `${type.color}14` }}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="truncate text-base font-black theme-text-primary">{item.original_filename}</h2>
                  <span className={highRisk ? "risk-high" : "risk-low"}>{highRisk ? "Yuqori risk" : "Past risk"}</span>
                </div>
                <div className="mt-1 flex flex-wrap items-center gap-3 text-xs theme-text-muted">
                  <span className="font-mono">CASE-{item.id}</span>
                  <span>{type.label}</span>
                  <span>{item.status}</span>
                  <span className="inline-flex items-center gap-1">
                    <CalendarDays className="h-3.5 w-3.5" />
                    {formatDate(item.uploaded_at)}
                  </span>
                </div>
              </div>
            </div>

            <Link href={`/dashboard/reports/${item.id}`} className="btn btn-cyan h-9 px-3 text-xs">
              <Eye className="h-3.5 w-3.5" />
              Ochish
            </Link>
          </div>

          <div className="mt-5 rounded-2xl border theme-border bg-white/[0.025] p-4">
            <div className="flex items-start gap-3">
              {highRisk ? (
                <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-red-400" />
              ) : (
                <CheckCircle2 className="mt-0.5 h-5 w-5 flex-shrink-0 text-green-400" />
              )}
              <div>
                <p className="text-sm font-bold theme-text-primary">{item.final_verdict || "Tahlil yakunlanmagan"}</p>
                <p className="mt-1 text-sm leading-6 theme-text-secondary">
                  Confidence: {item.confidence || "Noma'lum"} Â· Model versiyasi: {item.model_version || "Noma'lum"}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <ScoreMeter label="AI ehtimoli" value={ai} color={highRisk ? "#ef4444" : "#22c55e"} />
            <ScoreMeter label="Haqiqiylik" value={real} color="#22c55e" />
            <ScoreMeter label="Manipulyatsiya" value={manip} color="#f59e0b" />
          </div>
        </div>

        <aside className="border-t theme-border bg-black/[0.06] p-4 lg:border-l lg:border-t-0 lg:p-5">
          <p className="text-xs font-black uppercase tracking-[0.14em] theme-text-muted">Model natijalari</p>
          <div className="mt-3 space-y-2">
            {models.length === 0 ? (
              <p className="text-xs theme-text-muted">Model natijalari report faylda mavjud.</p>
            ) : (
              models.slice(0, 5).map((model, index) => (
                <div key={`${model.model_id || model.name}-${index}`} className="rounded-xl border theme-border bg-white/[0.03] p-3">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-xs font-bold theme-text-primary">{model.name || model.model_id}</p>
                    <span className={`text-[10px] font-bold ${model.status === "ready" ? "text-green-400" : "text-amber-400"}`}>
                      {model.status}
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] theme-text-muted">{model.verdict || model.error || "Status qayd etildi"}</p>
                </div>
              ))
            )}
          </div>
          <div className="mt-4 rounded-2xl border theme-border bg-white/[0.03] p-3">
            <div className="mb-3 flex items-center gap-2">
              <QrCode className="h-4 w-4 text-cyan-400" />
              <p className="text-xs font-black uppercase tracking-[0.14em] theme-text-muted">Individual QR</p>
            </div>
            <div className="rounded-xl bg-white p-2">
              <img src={qrUrl} alt={`CASE-${item.id} QR code`} className="mx-auto h-28 w-28" />
            </div>
            <p className="mt-2 break-all font-mono text-[10px] theme-text-muted">{publicUrl}</p>
            <a href={qrUrl} download={`xabarnavis-case-${item.id}-qr.png`} className="btn btn-ghost mt-3 h-8 justify-center text-[11px]">
              QR yuklab olish
            </a>
          </div>
        </aside>
      </div>
    </article>
  );
}

function ScoreMeter({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-xl border theme-border bg-black/[0.04] p-3">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold theme-text-muted">{label}</span>
        <span className="font-black" style={{ color }}>
          {value}%
        </span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full" style={{ width: `${value}%`, background: color }} />
      </div>
    </div>
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

function toneClass(tone: string) {
  if (tone === "red") return "text-red-400";
  if (tone === "amber") return "text-amber-400";
  if (tone === "green") return "text-green-400";
  return "text-cyan-300";
}



