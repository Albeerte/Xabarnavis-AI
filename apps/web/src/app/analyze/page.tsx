import {
  FileText,
  Headphones,
  Image as ImageIcon,
  MessageSquareText,
  Video,
} from "lucide-react";
import Link from "next/link";

const analyzers = [
  {
    title: "Rasm tahlili",
    description: "AI rasm, real kamera rasmi, EXIF, ELA, heatmap va manipulyatsiya tekshiruvi.",
    href: "/dashboard/image-analyzer",
    icon: ImageIcon,
    status: "JONLI",
  },
  {
    title: "Audio tahlili",
    description: "Synthetic voice, spoof audio, spektral signal va model confidence tahlili.",
    href: "/dashboard/audio-analyzer",
    icon: Headphones,
    status: "JONLI",
  },
  {
    title: "Video tahlili",
    description: "Deepfake, frame timeline, yuz mosligi va video forensikasi uchun sahifa.",
    href: "/dashboard/video-analyzer",
    icon: Video,
    status: "TEZ ORADA",
  },
  {
    title: "Matn/xabar tahlili",
    description: "Fake news, propaganda signal, claim detection va manba ishonchliligi.",
    href: "/dashboard/text-analyzer",
    icon: MessageSquareText,
    status: "TEZ ORADA",
  },
];

export default function AnalyzePage() {
  return (
    <main className="min-h-screen bg-[#f4f8ff] px-5 py-16 text-[#081427]">
      <div className="mx-auto max-w-6xl">
        <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Xabarnavis AI</p>
        <h1 className="mt-3 text-5xl font-black tracking-tight">Tekshiruv markazi</h1>
        <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-600">
          Media turini tanlang. Jonli modullar hozir bazaga hisobot yozadi, tayyor modullar esa keyingi AI adapterlarga ulash uchun sahifa sifatida mavjud.
        </p>

        <div className="mt-10 grid gap-5 md:grid-cols-2">
          {analyzers.map((item) => (
            <Link
              key={item.title}
              href={item.href}
              className="group rounded-[1.75rem] border border-blue-100 bg-white p-7 shadow-xl shadow-blue-900/5 transition hover:-translate-y-1 hover:border-blue-300"
            >
              <div className="flex items-center justify-between">
                <span className="grid size-14 place-items-center rounded-2xl bg-blue-50 text-blue-700">
                  <item.icon className="size-7" />
                </span>
                <span className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-black text-yellow-800">
                  {item.status}
                </span>
              </div>
              <h2 className="mt-6 text-2xl font-black">{item.title}</h2>
              <p className="mt-3 text-sm font-medium leading-6 text-slate-600">{item.description}</p>
            </Link>
          ))}
        </div>

        <div className="mt-8 rounded-3xl border border-blue-100 bg-white p-6 shadow-lg shadow-blue-900/5">
          <div className="flex items-center gap-3 text-blue-700">
            <FileText className="size-6" />
            <h2 className="text-xl font-black">Hisobot tizimi</h2>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Har bir yakunlangan analiz foydalanuvchining hisobotlar bo'limiga qo'shiladi va web/DOCX/QR ko'rinishida ochiladi.
          </p>
        </div>
      </div>
    </main>
  );
}



