import type { AnalysisResult, AnalysisType } from "./types";

const AI_SERVER_URL = process.env.AI_SERVER_URL || process.env.NEXT_PUBLIC_AI_SERVER_URL || "";

export async function callAiServer(
  endpoint: string,
  payload: FormData | Record<string, unknown>,
): Promise<AnalysisResult | null> {
  if (!AI_SERVER_URL) {
    return null;
  }

  const response = await fetch(`${AI_SERVER_URL.replace(/\/$/, "")}${endpoint}`, {
    method: "POST",
    body: payload instanceof FormData ? payload : JSON.stringify(payload),
    headers: payload instanceof FormData ? undefined : { "content-type": "application/json" },
  });

  if (!response.ok) {
    return null;
  }

  return response.json() as Promise<AnalysisResult>;
}

export function mockResult(type: AnalysisType, seed = 0): AnalysisResult {
  const ai = Math.max(8, Math.min(92, 22 + seed));
  const manipulation = Math.max(5, Math.min(88, 34 + Math.floor(seed / 2)));
  const authentic = Math.max(4, 100 - Math.max(ai, manipulation) - 12);
  const risky = ai >= 70 || manipulation >= 70;

  return {
    analysisType: type,
    verdict: risky ? "SUSPICIOUS" : "AUTHENTIC",
    confidenceScore: risky ? 84 : 78,
    fakeProbability: Math.max(ai, manipulation),
    authenticProbability: authentic,
    manipulationProbability: manipulation,
    aiGeneratedProbability: ai,
    riskLevel: risky ? "HIGH" : "LOW",
    detectedSignals: [
      {
        name: "Model score",
        value: `${ai}%`,
        status: ai >= 70 ? "fail" : "pass",
        description: "AI model synthetic-media ehtimolini hisoblab chiqdi.",
      },
      {
        name: "Manipulation trace",
        value: `${manipulation}%`,
        status: manipulation >= 70 ? "warning" : "info",
        description: "Tahrir yoki kompressiya izlari bo'yicha qo'shimcha signal.",
      },
    ],
    metadata: {
      fallback: true,
      generatedAt: new Date().toISOString(),
    },
    modelName: `Xabarnavis ${type.toLowerCase()} mock adapter`,
    modelVersion: "0.1.0",
    processingTimeMs: 640,
    recommendation: risky
      ? "Fayl bo'yicha qo'shimcha ekspertiza va manba tekshiruvi tavsiya etiladi."
      : "Jiddiy soxtalik belgisi topilmadi, lekin rasmiy qaror uchun manba bilan solishtiring.",
  };
}



