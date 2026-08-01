"use client";

import { motion } from "framer-motion";
import { 
  ShieldCheck, 
  Check,
  Globe2,
  FileCheck2,
  ShieldAlert
} from "lucide-react";
import { use } from "react";
import { usePathname } from "next/navigation";
import { localeFromPathname, reportPublicUrl, reportQrCodeUrl } from "@/lib/qr";

export default function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const pathname = usePathname();
  const locale = localeFromPathname(pathname);
  const reportId = resolvedParams.id || "a8f5f167f44f4964e6c998dee827110c";
  const reportUrl = reportPublicUrl(reportId, locale);
  const qrCodeUrl = reportQrCodeUrl(reportId, locale, 150);

  return (
    <main className="min-h-screen bg-[#050B18] neural-grid p-4 md:p-8 flex items-center justify-center">
      {/* Official Report Document */}
      <div className="relative mx-auto w-full max-w-2xl">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-8 md:p-12 relative overflow-hidden text-slate-900 border border-slate-200"
        >
          {/* Watermark */}
          <div className="absolute inset-0 flex items-center justify-center opacity-[0.02] pointer-events-none">
            <ShieldCheck className="size-[400px]" />
          </div>
          
          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b-2 border-slate-200 pb-6 mb-8 gap-6">
            <div className="flex items-center gap-4">
              <div className="size-16 rounded-xl bg-slate-900 flex items-center justify-center overflow-hidden p-2">
                <img src="/xabarnavis-logo.png" alt="Xabarnavis AI logo" className="size-full object-contain" />
              </div>
              <div>
                <h3 className="font-bold text-2xl text-slate-900">VERIFICATION REPORT</h3>
                <p className="text-sm text-slate-500 font-medium tracking-widest mt-1">XABARNAVIS AI SYSTEM</p>
              </div>
            </div>
            <div className="bg-white p-2 border border-slate-200 rounded-lg shadow-sm">
               <img 
                 src={qrCodeUrl}
                 alt={`QR Code to Report ${reportId}`}
                 className="size-20"
               />
            </div>
          </div>

          {/* Details */}
          <div className="space-y-4 text-base mb-10">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <span className="text-slate-500 font-medium">Date:</span>
              <span className="sm:col-span-3 font-mono text-slate-900">2026-06-30 14:45</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <span className="text-slate-500 font-medium">Hash ID:</span>
              <span className="sm:col-span-3 font-mono text-xs break-all text-slate-900 bg-slate-100 p-2 rounded-md">{reportId}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <span className="text-slate-500 font-medium">Public URL:</span>
              <span className="sm:col-span-3 font-mono text-xs break-all text-blue-700 bg-blue-50 p-2 rounded-md">{reportUrl}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
              <span className="text-slate-500 font-medium">File Name:</span>
              <span className="sm:col-span-3 font-mono text-slate-900">evidence_01.jpg</span>
            </div>
          </div>

          {/* Result Banner */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-10 flex items-center gap-4">
             <div className="size-14 rounded-full bg-red-100 flex items-center justify-center shrink-0">
               <ShieldAlert className="size-7 text-red-600" />
             </div>
             <div>
               <p className="text-red-800 font-bold text-xl mb-1">HIGH RISK (87%)</p>
               <p className="text-red-600 text-sm uppercase tracking-wider font-semibold">AI Manipulation Detected</p>
             </div>
          </div>

          {/* Detailed Analysis */}
          <h4 className="font-bold text-lg mb-4 border-b border-slate-200 pb-2">Analysis Breakdown</h4>
          <div className="space-y-3 mb-12">
            {[
              { label: "AI Generator Artifacts", status: "Detected", isDanger: true },
              { label: "EXIF Metadata", status: "Missing/Modified", isDanger: true },
              { label: "Compression Signature", status: "Mismatch", isDanger: true },
              { label: "Copy-Move Cloning", status: "Not Detected", isDanger: false },
            ].map((item, i) => (
              <div key={i} className="flex justify-between items-center text-sm p-3 rounded-md bg-slate-50 border border-slate-100">
                <span className="text-slate-600 font-medium">{item.label}</span>
                <span className={`font-bold flex items-center gap-2 ${item.isDanger ? 'text-red-600' : 'text-green-600'}`}>
                   {item.status}
                   {item.isDanger ? <ShieldAlert className="size-4" /> : <Check className="size-4" />}
                </span>
              </div>
            ))}
          </div>

          {/* Footer Signatures */}
          <div className="border-t-2 border-slate-200 pt-8 mt-12 flex flex-col sm:flex-row justify-between items-center gap-8">
             <div className="text-center">
               <div className="w-40 h-16 border-2 border-slate-300 border-dashed rounded-lg flex items-center justify-center mb-2 mx-auto relative overflow-hidden">
                  <div className="absolute inset-0 bg-slate-50 opacity-50"></div>
                  <span className="text-xs text-slate-400 font-mono font-bold tracking-widest relative z-10">DIGITAL SIGNATURE</span>
               </div>
               <p className="text-xs text-slate-500 uppercase tracking-widest font-semibold mt-2">Verified by Xabarnavis AI</p>
               <p className="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1"><Globe2 className="size-3" /> xabarnavis.ai</p>
             </div>
             
             <div className="size-24 rounded-full border-4 border-red-600/30 flex items-center justify-center text-red-600/50 font-bold text-xl rotate-[-15deg] uppercase tracking-widest shadow-sm">
               FAKE
             </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}



