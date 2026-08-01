import { Mail, Send } from "lucide-react";

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-[#f4f8ff] px-5 py-16 text-[#081427]">
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Aloqa</p>
          <h1 className="mt-3 text-5xl font-black tracking-tight">Xabarnavis AI bilan bog'lanish</h1>
          <p className="mt-5 text-lg leading-8 text-slate-600">
            Universitet, jurnalistika, bank, sud ekspertizasi va media monitoring loyihalari uchun platformani moslab berish mumkin.
          </p>
          <div className="mt-8 flex items-center gap-3 rounded-2xl bg-white p-5 font-bold shadow-lg shadow-blue-900/5">
            <Mail className="size-5 text-blue-700" /> info@xabarnavis.ai
          </div>
        </div>
        <form className="rounded-[2rem] border border-blue-100 bg-white p-7 shadow-xl shadow-blue-900/5">
          <label className="block text-sm font-black text-slate-700">Ism</label>
          <input className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3" placeholder="Ismingiz" />
          <label className="mt-5 block text-sm font-black text-slate-700">Email</label>
          <input className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3" placeholder="email@example.com" />
          <label className="mt-5 block text-sm font-black text-slate-700">Xabar</label>
          <textarea className="mt-2 min-h-36 w-full rounded-2xl border border-slate-200 px-4 py-3" placeholder="Loyiha haqida yozing" />
          <button className="mt-5 inline-flex items-center gap-2 rounded-full bg-blue-700 px-6 py-3 font-black text-white">
            Yuborish <Send className="size-4" />
          </button>
        </form>
      </div>
    </main>
  );
}



