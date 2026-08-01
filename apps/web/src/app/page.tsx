"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  BadgeCheck,
  BookOpenCheck,
  BrainCircuit,
  Camera,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Download,
  FileCheck2,
  Fingerprint,
  Gavel,
  Globe2,
  Headphones,
  IdCard,
  Image as ImageIcon,
  Languages,
  LockKeyhole,
  MessageSquareText,
  Newspaper,
  Palette,
  Play,
  Radar,
  ShieldCheck,
  Sparkles,
  ShoppingBag,
  Trophy,
  Users,
  Video,
  Zap,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { dictionaries, getLocale, locales, switchLocalePath } from "@/lib/i18n";
import { reportQrCodeUrl } from "@/lib/qr";

const stats = [
  { value: "4", label: "Media moduli" },
  { value: "7+", label: "AI va forensic model" },
  { value: "DOCX", label: "Rasmiy hisobot" },
  { value: "SHA-256", label: "Dalil identifikatori" },
];

const modules = [
  {
    title: "Rasm tahlili",
    desc: "AI rasm, real kamera rasmi, manipulyatsiya, EXIF, ELA va heatmap dalillari.",
    icon: ImageIcon,
    status: "JONLI",
    href: "/dashboard/image-analyzer",
  },
  {
    title: "Audio tahlili",
    desc: "Synthetic voice, spoof signal, spektral izlar va ovoz forensikasi.",
    icon: Headphones,
    status: "JONLI",
    href: "/dashboard/audio-analyzer",
  },
  {
    title: "Video tahlili",
    desc: "Deepfake, frame izlari, montaj alomatlari va timeline bo'yicha tekshiruv.",
    icon: Video,
    status: "TEZ ORADA",
    href: "/dashboard/video-analyzer",
  },
  {
    title: "Matn tahlili",
    desc: "AI matn, propaganda, dezinformatsiya va xabar ishonchliligi tahlili.",
    icon: MessageSquareText,
    status: "TEZ ORADA",
    href: "/dashboard/text-analyzer",
  },
];

const featureCards = [
  ["Xavfsiz yuklash", "Fayllar foydalanuvchi hisobiga bog'lanadi va dalil zanjiri saqlanadi.", LockKeyhole],
  ["Xabarnavis 0.5", "Yakuniy rasm qarori asosiy model natijasiga tayangan holda ko'rsatiladi.", BrainCircuit],
  ["Forensik dalillar", "Metadata, heatmap, hash, model ballari va texnik izohlar bir joyda.", Fingerprint],
  ["Rasmiy eksport", "DOCX va JSON hisobotlar case ID, vaqt va tavsiyalar bilan tayyorlanadi.", Download],
];

const useCases = [
  ["Online tarqalgan rasmlar", "Ijtimoiy tarmoq, xabar va maqolalardagi rasmni ulashishdan oldin tekshiring.", Radar],
  ["Profil suratlari", "Fake profil, catfishing va sintetik avatarlarni aniqlash uchun.", Users],
  ["Sud va sug'urta dalillari", "Vizual dalil tahrirlangan yoki AI yaratilgan emasligini tekshirish.", Gavel],
  ["ID va hujjat rasmlari", "Shaxsni tasdiqlovchi suratlarda soxtalik va manipulyatsiya izlarini ko'rish.", IdCard],
  ["Mahsulot rasmlari", "E-commerce listinglarda AI yaratilgan mahsulot suratlarini aniqlash.", ShoppingBag],
  ["Yangilik fotografiyasi", "Jurnalistik materialdagi rasmning manba va haqiqiyligini baholash.", Newspaper],
  ["AI artwork", "AI yaratilgan ijodiy rasmlar va attribution transparency uchun.", Palette],
  ["Dezinformatsiya", "Viral deepfake, propaganda va vizual manipulyatsiya kampaniyalariga qarshi.", ShieldCheck],
];

const process = [
  ["Fayl yuklanadi", "Rasm yoki audio fayl shaxsiy kabinetga xavfsiz qabul qilinadi."],
  ["AI modellar tekshiradi", "Asosiy model qaror beradi, yordamchi modellar dalil sifatida ishlaydi."],
  ["Forensik izlar yig'iladi", "Metadata, kompressiya, heatmap, spektr va hash ma'lumotlari jamlanadi."],
  ["Hisobot yaratiladi", "Foydalanuvchi o'z analizini ko'radi va legal report yuklab oladi."],
];

const pricing = [
  { name: "Free", price: "0 so'm", items: ["5 ta test", "Oddiy natija", "Rasm tahlili"] },
  { name: "Pro", price: "99 000 so'm", items: ["Cheksiz tahlil", "DOCX hisobot", "Heatmap va metadata"], featured: true },
  { name: "Enterprise", price: "Kelishiladi", items: ["API ulanish", "Jamoaviy kabinet", "Maxsus model"] },
];

export default function Home() {
  const pathname = usePathname();
  const locale = getLocale(pathname.split("/").filter(Boolean)[0]);
  const t = dictionaries[locale];
  const localePrefix = `/${locale}`;
  const demoQrUrl = reportQrCodeUrl("demo", locale, 92);
  const navItems = [
    { label: t.nav.home, href: `${localePrefix}#home` },
    { label: t.nav.analyze, href: `${localePrefix}#modules` },
    { label: t.nav.reports, href: `${localePrefix}#report` },
    { label: t.nav.pricing, href: `${localePrefix}#pricing` },
    { label: t.nav.api, href: "/api-docs" },
    { label: t.nav.contact, href: `${localePrefix}#contact` },
  ];

  return (
    <main
      id="home"
      className="min-h-screen bg-[#f4f8ff] text-[#081427]"
      style={{
        backgroundImage:
          "linear-gradient(rgba(37, 99, 235, 0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(37, 99, 235, 0.08) 1px, transparent 1px), radial-gradient(circle at 80% 15%, rgba(250, 204, 21, 0.24), transparent 28rem), radial-gradient(circle at 15% 25%, rgba(14, 165, 233, 0.22), transparent 34rem)",
        backgroundSize: "76px 76px, 76px 76px, auto, auto",
      }}
    >
      <header className="sticky top-12 z-40 border-b border-blue-900/10 bg-white/78 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-5 px-5 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-4">
            <span className="grid size-16 place-items-center rounded-2xl border border-blue-200 bg-[#07111f] p-2 shadow-lg shadow-blue-900/10">
              <Image
                src="/xabarnavis-logo.png"
                alt="Xabarnavis AI logo"
                width={54}
                height={54}
                className="size-full object-contain"
                priority
              />
            </span>
            <span>
              <strong className="block text-xl font-black tracking-tight">Xabarnavis AI</strong>
              <span className="text-xs font-bold uppercase tracking-[0.35em] text-sky-600">Forensik platforma</span>
            </span>
          </Link>

          <nav className="hidden items-center gap-1 xl:flex">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="rounded-full px-4 py-2 text-sm font-bold text-slate-600 transition hover:bg-blue-50 hover:text-blue-700"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <div className="hidden items-center gap-1 rounded-full border border-slate-200 bg-white p-1 text-xs font-black text-slate-700 shadow-sm sm:flex">
              <Languages className="ml-2 size-4 text-blue-600" />
              {locales.map((item) => (
                <Link
                  key={item}
                  href={switchLocalePath(pathname, item)}
                  className={`rounded-full px-3 py-2 uppercase transition ${
                    item === locale ? "bg-blue-700 text-white" : "hover:bg-blue-50 hover:text-blue-700"
                  }`}
                >
                  {item}
                </Link>
              ))}
            </div>
            <Link
              href={`/${locale}/login?next=dashboard`}
              className="rounded-full border border-slate-200 bg-white px-5 py-3 text-sm font-black text-slate-800 shadow-sm transition hover:border-blue-300 hover:text-blue-700"
            >
              {t.nav.login}
            </Link>
            <Link
              href={`/${locale}/register?next=dashboard`}
              className="hidden rounded-full bg-[#facc15] px-5 py-3 text-sm font-black text-[#081427] shadow-lg shadow-yellow-300/30 transition hover:bg-yellow-300 sm:inline-flex"
            >
              {t.nav.register}
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-[1440px] items-center gap-10 px-5 pb-20 pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-28 lg:pt-28">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-200 bg-white/80 px-4 py-2 text-sm font-black uppercase tracking-[0.22em] text-sky-700 shadow-sm">
            <Sparkles className="size-4" /> {t.home.badge}
          </div>

          <h1 className="mt-8 max-w-4xl text-5xl font-black leading-[0.96] tracking-tight text-[#061226] md:text-7xl lg:text-[88px]">
            {t.home.title}
          </h1>
          <p className="mt-5 max-w-3xl text-3xl font-black leading-tight text-blue-700 md:text-5xl">
            {t.home.subtitle}
          </p>
          <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-650">
            {t.home.description}
          </p>

          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/dashboard/image-analyzer"
              className="inline-flex items-center justify-center gap-3 rounded-full bg-blue-700 px-7 py-4 text-base font-black text-white shadow-xl shadow-blue-700/25 transition hover:bg-blue-800"
            >
              {t.home.start} <ArrowRight className="size-5" />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-3 rounded-full border border-blue-200 bg-white px-7 py-4 text-base font-black text-blue-800 shadow-sm transition hover:border-blue-400"
            >
              {t.home.dashboard} <ChevronRight className="size-5" />
            </Link>
          </div>

          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-3xl border border-white bg-white/78 p-5 shadow-lg shadow-blue-900/5">
                <div className="text-3xl font-black text-[#07111f]">{stat.value}</div>
                <div className="mt-1 text-sm font-bold text-slate-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.12, duration: 0.55 }}
          className="relative"
        >
          <div className="absolute right-8 -top-9 z-20 hidden rounded-full border border-yellow-200 bg-[#facc15] px-5 py-3 text-sm font-black text-[#081427] shadow-xl shadow-yellow-400/30 lg:flex lg:items-center">
            <Clock3 className="mr-2 inline size-4" /> Real vaqt tahlili
          </div>
          <div className="relative z-10 rounded-[2rem] border border-blue-100 bg-white/85 p-5 shadow-2xl shadow-blue-900/12 backdrop-blur-xl">
            <div className="rounded-[1.5rem] border border-sky-100 bg-gradient-to-br from-blue-50 via-white to-yellow-50 p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-black uppercase tracking-[0.25em] text-sky-700">Namuna tekshiruv</p>
                  <h2 className="mt-3 text-3xl font-black text-[#061226]">Dalil rasmi tahlili</h2>
                </div>
                <span className="rounded-full bg-emerald-50 px-4 py-2 text-sm font-black text-emerald-700 ring-1 ring-emerald-200">
                  TAYYOR
                </span>
              </div>

              <div className="mt-7 grid gap-4 md:grid-cols-[1fr_170px]">
                <div className="min-h-64 rounded-3xl border border-dashed border-blue-200 bg-[#eef6ff] p-5">
                  <div className="grid h-full place-items-center rounded-2xl bg-white/65">
                    <div className="text-center">
                      <div className="mx-auto grid size-20 place-items-center rounded-3xl bg-blue-700 text-white shadow-xl shadow-blue-700/25">
                        <Camera className="size-10" />
                      </div>
                      <p className="mt-5 text-lg font-black">Fayl yuklang</p>
                      <p className="mt-2 text-sm font-semibold text-slate-500">JPG, PNG, WEBP, WAV, MP3</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-3xl bg-[#081427] p-5 text-white shadow-xl shadow-blue-900/20">
                    <div className="flex items-center gap-2 text-sm font-bold text-sky-200">
                      <Radar className="size-4" /> AI ehtimoli
                    </div>
                    <div className="mt-4 text-5xl font-black">22%</div>
                    <p className="mt-2 text-sm text-slate-300">Asosiy qaror: Real rasmga yaqin</p>
                  </div>
                  <div className="rounded-3xl border border-yellow-200 bg-yellow-50 p-5">
                    <div className="text-sm font-black text-yellow-700">Forensik dalillar</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {["EXIF", "ELA", "Heatmap", "Hash"].map((item) => (
                        <span key={item} className="rounded-full bg-white px-3 py-1 text-xs font-black text-slate-700 shadow-sm">
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {["Xabarnavis 0.5", "Metadata tekshiruvi", "Legal report"].map((item) => (
                  <div key={item} className="flex items-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm font-black text-slate-700 shadow-sm">
                    <CheckCircle2 className="size-4 text-emerald-600" /> {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section id="modules" className="mx-auto max-w-[1440px] px-5 py-16 lg:px-8">
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Yo'nalishlar</p>
            <h2 className="mt-3 text-4xl font-black tracking-tight md:text-5xl">Tahlil modullari</h2>
          </div>
          <p className="max-w-xl text-base leading-7 text-slate-600">
            Har bir modul alohida sahifaga ega. Jonli modullar hozir ishlaydi, qolganlari tayyor UI bilan bosqichma-bosqich ulanadi.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {modules.map((module) => (
            <Link
              href={module.href}
              key={module.title}
              className="group rounded-[1.75rem] border border-blue-100 bg-white/85 p-6 shadow-lg shadow-blue-900/5 transition hover:-translate-y-1 hover:border-blue-300 hover:shadow-2xl hover:shadow-blue-900/10"
            >
              <div className="flex items-center justify-between">
                <span className="grid size-14 place-items-center rounded-2xl bg-blue-50 text-blue-700 ring-1 ring-blue-100">
                  <module.icon className="size-7" />
                </span>
                <span className="rounded-full bg-[#facc15]/30 px-3 py-1 text-xs font-black text-yellow-800 ring-1 ring-yellow-200">
                  {module.status}
                </span>
              </div>
              <h3 className="mt-7 text-2xl font-black">{module.title}</h3>
              <p className="mt-3 min-h-20 text-sm font-medium leading-6 text-slate-600">{module.desc}</p>
              <div className="mt-6 inline-flex items-center gap-2 text-sm font-black text-blue-700">
                Ochish <ArrowRight className="size-4 transition group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-[1440px] px-5 py-16 lg:px-8">
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          {featureCards.map(([title, desc, Icon]) => (
            <div key={title as string} className="rounded-[1.75rem] border border-white bg-white/75 p-6 shadow-lg shadow-slate-900/5">
              <Icon className="size-9 text-blue-700" />
              <h3 className="mt-5 text-xl font-black">{title as string}</h3>
              <p className="mt-3 text-sm font-medium leading-6 text-slate-600">{desc as string}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-[1440px] px-5 py-16 lg:px-8">
        <div className="mb-8 text-center">
          <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Qo'llanish holatlari</p>
          <h2 className="mt-3 text-4xl font-black tracking-tight md:text-5xl">Xabarnavis AI qayerda yordam beradi?</h2>
          <p className="mx-auto mt-5 max-w-3xl text-base leading-7 text-slate-600">
            Platforma jurnalistlar, universitetlar, tergovchilar, fact-checkerlar, banklar va media xavfsizlik jamoalari uchun
            media dalilni tez, tushunarli va hujjatlashtirilgan shaklda tekshiradi.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {useCases.map(([title, desc, Icon]) => (
            <div
              key={title as string}
              className="group rounded-[1.5rem] border border-blue-100 bg-white/85 p-5 shadow-lg shadow-blue-900/5 transition hover:-translate-y-1 hover:border-blue-300 hover:shadow-xl hover:shadow-blue-900/10"
            >
              <div className="grid size-12 place-items-center rounded-2xl bg-blue-50 text-blue-700 ring-1 ring-blue-100 transition group-hover:bg-blue-700 group-hover:text-white">
                <Icon className="size-6" />
              </div>
              <h3 className="mt-5 text-lg font-black">{title as string}</h3>
              <p className="mt-2 text-sm font-medium leading-6 text-slate-600">{desc as string}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="process" className="mx-auto max-w-[1440px] px-5 py-16 lg:px-8">
        <div className="rounded-[2rem] bg-[#081427] p-6 text-white shadow-2xl shadow-blue-900/20 md:p-10">
          <div className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
            <div>
              <p className="text-sm font-black uppercase tracking-[0.28em] text-cyan-300">Jarayon</p>
              <h2 className="mt-3 text-4xl font-black tracking-tight md:text-5xl">Qanday ishlaydi?</h2>
              <p className="mt-5 text-lg leading-8 text-slate-300">
                Oddiy foydalanuvchi uchun jarayon sodda: fayl yuklanadi, model tahlil qiladi, dalillar jamlanadi va hisobot tayyorlanadi.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {process.map(([title, desc], index) => (
                <div key={title} className="rounded-3xl border border-white/10 bg-white/7 p-5">
                  <div className="flex items-center gap-3">
                    <span className="grid size-10 place-items-center rounded-full bg-[#facc15] text-sm font-black text-[#081427]">
                      {index + 1}
                    </span>
                    <h3 className="text-lg font-black">{title}</h3>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-300">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section
        id="report"
        className="relative overflow-hidden border-y border-slate-800 bg-[#060a16] px-5 py-24 text-white lg:px-8"
      >
        <div
          className="absolute inset-0 opacity-70"
          style={{
            backgroundImage:
              "radial-gradient(circle at 70% 30%, rgba(14,165,233,0.28), transparent 26rem), radial-gradient(circle at 45% 60%, rgba(250,204,21,0.12), transparent 18rem), linear-gradient(rgba(56,189,248,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,0.08) 1px, transparent 1px)",
            backgroundSize: "auto, auto, 84px 84px, 84px 84px",
          }}
        />
        <div className="pointer-events-none absolute right-[10%] top-10 h-[34rem] w-[34rem] rounded-full border border-cyan-400/20 bg-cyan-500/5 shadow-[0_0_120px_rgba(34,211,238,0.18)]" />
        <div className="pointer-events-none absolute right-[13%] top-24 h-[27rem] w-[27rem] rounded-full border-2 border-yellow-300/35 rotate-[-24deg]" />
        <div className="pointer-events-none absolute right-[6%] top-20 h-[32rem] w-[12rem] rounded-[100%] border-2 border-cyan-400/25 rotate-[12deg]" />

        <div className="relative mx-auto grid max-w-[1440px] gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-yellow-300/25 bg-yellow-300/10 px-4 py-2 text-sm font-black uppercase tracking-[0.24em] text-yellow-300">
              <FileCheck2 className="size-4" /> Professional legal report
            </div>
            <h2 className="mt-7 text-4xl font-black tracking-tight md:text-6xl">
              Har bir analiz chiroyli va rasmiy hisobotga aylanadi
            </h2>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
              Xabarnavis AI tahlildan keyin web report, PDF, DOCX va QR orqali tekshiriladigan public sahifa yaratadi.
              Hisobotda model qarori, dalil hash, metadata, heatmap, signal breakdown va tavsiya bir joyda ko'rsatiladi.
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-2">
              {[
                "PDF va DOCX eksport",
                "QR orqali public report",
                "Case ID va timestamp",
                "SHA-256 evidence hash",
                "Har bir model natijasi",
                "Texnik metadata va tavsiya",
              ].map((item) => (
                <div key={item} className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-3 font-bold text-slate-100 backdrop-blur">
                  <BadgeCheck className="size-5 text-emerald-300" /> {item}
                </div>
              ))}
            </div>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/report/demo"
                className="inline-flex items-center justify-center gap-3 rounded-full bg-yellow-300 px-7 py-4 font-black text-[#07111f] shadow-xl shadow-yellow-300/20 transition hover:bg-yellow-200"
              >
                Demo hisobotni ko'rish <ArrowRight className="size-5" />
              </Link>
              <Link
                href="/dashboard/reports"
                className="inline-flex items-center justify-center gap-3 rounded-full border border-white/15 bg-white/[0.06] px-7 py-4 font-black text-white backdrop-blur transition hover:bg-white/[0.12]"
              >
                Hisobotlar paneli <ChevronRight className="size-5" />
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-white/10 bg-[#0c1224]/85 p-4 shadow-2xl shadow-black/40 backdrop-blur-xl">
            <div className="rounded-[1.5rem] border border-cyan-300/15 bg-gradient-to-br from-white/[0.10] via-white/[0.04] to-yellow-300/[0.08] p-6">
              <div className="flex flex-col gap-5 border-b border-white/10 pb-5 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-center gap-4">
                  <span className="grid size-14 place-items-center rounded-2xl bg-[#07111f] p-2 ring-1 ring-cyan-300/20">
                    <Image src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" width={46} height={46} className="size-full object-contain" />
                  </span>
                  <div>
                    <p className="text-xs font-black uppercase tracking-[0.22em] text-cyan-300">Xabarnavis AI report</p>
                    <h3 className="mt-1 text-2xl font-black">CASE-059 forensic xulosa</h3>
                  </div>
                </div>
                <div className="rounded-2xl bg-white p-2">
                  <img src={demoQrUrl} alt="Xabarnavis demo report QR" className="size-20 rounded-xl" />
                </div>
              </div>

              <div className="mt-6 rounded-3xl border border-emerald-300/25 bg-emerald-300/10 p-5">
                <p className="text-sm font-bold text-emerald-200">Yakuniy qaror</p>
                <div className="mt-2 text-3xl font-black text-white">Ehtimol haqiqiy kamera rasmi</div>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                  Xabarnavis 0.5 modeli asosiy qarorni berdi, EXIF, ELA va heatmap qo'shimcha forensic dalil sifatida biriktirildi.
                </p>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {[
                  ["AI ehtimoli", "22%", "text-red-300"],
                  ["Haqiqiylik", "71%", "text-emerald-300"],
                  ["Manipulyatsiya", "49%", "text-yellow-300"],
                ].map(([label, value, color]) => (
                  <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                    <p className="text-xs font-bold text-slate-400">{label}</p>
                    <p className={`mt-2 text-3xl font-black ${color}`}>{value}</p>
                  </div>
                ))}
              </div>

              <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_0.9fr]">
                <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">Dalil ma'lumotlari</p>
                  <div className="mt-4 space-y-3 text-sm">
                    {[
                      ["Fayl", "ai-generated-image-main.png"],
                      ["Model", "Xabarnavis 0.5"],
                      ["Vaqt", "2026-07-06 14:45"],
                      ["SHA-256", "e45a441dc526b061..."],
                    ].map(([label, value]) => (
                      <div key={label} className="flex justify-between gap-4 border-b border-white/10 pb-2 last:border-0">
                        <span className="text-slate-400">{label}</span>
                        <span className="text-right font-bold text-slate-100">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
                  <p className="text-xs font-black uppercase tracking-[0.16em] text-slate-400">Report tarkibi</p>
                  <div className="mt-4 space-y-2">
                    {["Heatmap evidence", "Metadata table", "Model breakdown", "Recommendation"].map((item) => (
                      <div key={item} className="flex items-center gap-2 text-sm font-bold text-slate-200">
                        <CheckCircle2 className="size-4 text-cyan-300" /> {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="mx-auto max-w-[1440px] px-5 py-16 lg:px-8">
        <div className="mb-8 text-center">
          <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Tariflar</p>
          <h2 className="mt-3 text-4xl font-black tracking-tight md:text-5xl">Foydalanish rejasi</h2>
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          {pricing.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-[1.75rem] border p-7 shadow-xl ${
                plan.featured
                  ? "border-blue-300 bg-blue-700 text-white shadow-blue-700/20"
                  : "border-blue-100 bg-white/85 text-[#081427] shadow-blue-900/5"
              }`}
            >
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-black">{plan.name}</h3>
                {plan.featured ? <Trophy className="size-6 text-yellow-300" /> : <ShieldCheck className="size-6 text-blue-700" />}
              </div>
              <div className="mt-5 text-4xl font-black">{plan.price}</div>
              <ul className="mt-7 space-y-3">
                {plan.items.map((item) => (
                  <li key={item} className="flex items-center gap-3 text-sm font-bold">
                    <CheckCircle2 className={`size-5 ${plan.featured ? "text-yellow-300" : "text-emerald-600"}`} /> {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="relative overflow-hidden bg-[#070b18] px-5 py-24 text-white lg:px-8">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "radial-gradient(circle at 62% 38%, rgba(34,211,238,0.28), transparent 24rem), radial-gradient(circle at 50% 50%, rgba(21,94,117,0.28), transparent 34rem)",
          }}
        />
        <div className="absolute left-[12%] top-[18%] h-3 w-3 rounded-full bg-white/80 shadow-[0_0_18px_white]" />
        <div className="absolute left-[28%] top-[32%] h-2 w-2 rounded-full bg-yellow-300/80" />
        <div className="absolute right-[18%] top-[25%] h-3 w-3 rounded-full bg-emerald-400" />
        <div className="absolute right-[7%] top-[42%] h-2 w-2 rounded-full bg-cyan-300" />
        <div className="pointer-events-none absolute right-[16%] top-12 h-[28rem] w-[28rem] rounded-full border border-cyan-300/20 bg-cyan-400/10" />
        <div className="pointer-events-none absolute right-[20%] top-20 h-[23rem] w-[23rem] rounded-full border-2 border-yellow-300/35 rotate-[24deg]" />

        <div className="relative mx-auto max-w-4xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-yellow-300/30 bg-yellow-300/10 px-5 py-3 text-sm font-black text-yellow-300">
            <Sparkles className="size-4" /> Xabarnavis AI tekshiruvini boshlang
          </div>
          <h2 className="mt-7 text-4xl font-black tracking-tight md:text-6xl">
            Media dalilni ishonchli, tez va hujjatlashtirilgan shaklda tekshiring
          </h2>
          <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-300">
            Faylni yuklang, Xabarnavis 0.5 va forensic modullar natijasini oling, so'ng QR bilan tasdiqlanadigan report yarating.
          </p>
          <div className="mx-auto mt-9 flex max-w-lg flex-col justify-center gap-3 sm:flex-row">
            <Link
              href="/dashboard/image-analyzer"
              className="inline-flex items-center justify-center gap-3 rounded-2xl bg-yellow-300 px-8 py-4 font-black text-[#07111f] shadow-xl shadow-yellow-300/20 transition hover:bg-yellow-200"
            >
              <Play className="size-5" /> Tekshiruvni boshlash
            </Link>
            <Link
              href="/dashboard/reports"
              className="inline-flex items-center justify-center gap-3 rounded-2xl border border-white/15 bg-white/[0.06] px-8 py-4 font-black text-white backdrop-blur transition hover:bg-white/[0.12]"
            >
              <FileCheck2 className="size-5" /> Reportlarni ko'rish
            </Link>
          </div>
        </div>
      </section>

      <footer id="contact" className="border-t border-white/10 bg-[#050816] px-5 py-16 text-white lg:px-8">
        <div className="mx-auto grid max-w-[1200px] gap-10 md:grid-cols-[1.2fr_0.8fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-4">
              <span className="grid size-14 place-items-center rounded-2xl border border-cyan-300/20 bg-white/[0.06] p-2">
                <Image src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" width={46} height={46} className="size-full object-contain" />
              </span>
              <div>
                <div className="text-xl font-black">Xabarnavis AI</div>
                <div className="bg-gradient-to-r from-cyan-300 via-blue-400 to-yellow-300 bg-clip-text text-xs font-black uppercase tracking-[0.24em] text-transparent">
                  Forensik platforma
                </div>
              </div>
            </div>
            <p className="mt-6 max-w-sm text-sm font-medium leading-7 text-slate-400">
              Xabarnavis AI â€” AI-generated, fake, edited yoki real media fayllarni tekshiruvchi professional platforma.
              Jurnalistlar, universitetlar, tergovchilar va fact-checkerlar uchun.
            </p>
            <div className="mt-6 flex gap-3">
              {["TG", "IG", "YT", "FB"].map((item) => (
                <span key={item} className="grid size-10 place-items-center rounded-full border border-white/10 bg-white/[0.06] text-xs font-black text-slate-300">
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-[0.18em] text-white">Quick links</h3>
            <div className="mt-5 h-px w-8 bg-blue-500" />
            <div className="mt-5 grid gap-3 text-sm font-bold text-slate-400">
              <Link href={`${localePrefix}`}>Bosh sahifa</Link>
              <Link href="/analyze">Tekshiruv</Link>
              <Link href="/dashboard/reports">Hisobotlar</Link>
              <Link href="/pricing">Narxlar</Link>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-[0.18em] text-white">Yo'nalishlar</h3>
            <div className="mt-5 h-px w-8 bg-blue-500" />
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm font-bold text-slate-400">
              <span>Image AI detection</span>
              <span>Audio spoof</span>
              <span>Video deepfake</span>
              <span>Text/news</span>
              <span>EXIF metadata</span>
              <span>Heatmap report</span>
              <span>QR verification</span>
              <span>DOCX export</span>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-black uppercase tracking-[0.18em] text-white">Contact</h3>
            <div className="mt-5 h-px w-8 bg-blue-500" />
            <div className="mt-5 grid gap-4 text-sm font-bold text-slate-400">
              <span className="inline-flex gap-3"><Globe2 className="size-5 text-blue-400" /> Tashkent, Uzbekistan</span>
              <span className="inline-flex gap-3"><BookOpenCheck className="size-5 text-blue-400" /> support@xabarnavis.ai</span>
              <span className="inline-flex gap-3"><Zap className="size-5 text-blue-400" /> 24/7 instant analysis</span>
              <span className="inline-flex gap-3"><LockKeyhole className="size-5 text-blue-400" /> Secure private uploads</span>
            </div>
          </div>
        </div>
        <div className="mx-auto mt-14 flex max-w-[1200px] flex-col justify-between gap-4 border-t border-white/10 pt-8 text-sm font-bold text-slate-500 md:flex-row">
          <span>Â© 2026 Xabarnavis AI. All rights reserved.</span>
          <span className="flex gap-6">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </span>
        </div>
      </footer>
    </main>
  );
}



