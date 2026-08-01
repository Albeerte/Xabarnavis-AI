const plans = [
  ["Free", "0 so'm", "5 ta sinov tahlili, oddiy natija, dashboardga kirish"],
  ["Pro", "99 000 so'm", "Cheksiz tahlil, DOCX hisobot, heatmap, QR public link"],
  ["Enterprise", "Kelishiladi", "API, jamoaviy kabinet, admin review, maxsus model adapterlari"],
];

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-[#f4f8ff] px-5 py-16 text-[#081427]">
      <div className="mx-auto max-w-6xl">
        <p className="text-sm font-black uppercase tracking-[0.28em] text-blue-700">Narxlar</p>
        <h1 className="mt-3 text-5xl font-black tracking-tight">Xabarnavis AI tariflari</h1>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {plans.map(([name, price, description]) => (
            <div key={name} className="rounded-[1.75rem] border border-blue-100 bg-white p-7 shadow-xl shadow-blue-900/5">
              <h2 className="text-2xl font-black">{name}</h2>
              <div className="mt-4 text-4xl font-black text-blue-700">{price}</div>
              <p className="mt-5 text-sm font-medium leading-6 text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}



