export default function ApiDocsPage() {
  return (
    <main className="min-h-screen bg-[#f4f8ff] px-5 py-16 text-[#081427]">
      <div className="mx-auto max-w-5xl rounded-[2rem] border border-blue-100 bg-white p-8 shadow-xl shadow-blue-900/5">
        <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">API</p>
        <h1 className="mt-3 text-5xl font-black tracking-tight">API dokumentatsiya</h1>
        <p className="mt-5 text-lg leading-8 text-slate-600">
          Xabarnavis AI API qatlami FastAPI backend orqali ishlaydi. Keyingi bosqichda API key yaratish, rate limit va tashqi integratsiyalar shu sahifaga ulanadi.
        </p>
        <pre className="mt-8 overflow-auto rounded-2xl bg-[#081427] p-5 text-sm text-cyan-100">
{`POST /api/analyze
POST /api/reports
GET  /api/reports/{id}
GET  /api/r/public/{token}`}
        </pre>
      </div>
    </main>
  );
}



