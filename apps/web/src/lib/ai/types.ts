export type AnalysisType = "IMAGE" | "VIDEO" | "AUDIO" | "TEXT";

export type Verdict =
  | "AUTHENTIC"
  | "SUSPICIOUS"
  | "AI_GENERATED"
  | "MANIPULATED"
  | "FAKE"
  | "UNKNOWN";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | "UNKNOWN";

export interface AnalysisSignal {
  name: string;
  value: string | number | boolean;
  status: "pass" | "warning" | "fail" | "info";
  description: string;
}

export interface AnalysisResult {
  analysisType: AnalysisType;
  verdict: Verdict;
  confidenceScore: number;
  fakeProbability: number;
  authenticProbability: number;
  manipulationProbability: number;
  aiGeneratedProbability: number;
  riskLevel: RiskLevel;
  detectedSignals: AnalysisSignal[];
  metadata: Record<string, unknown>;
  modelName: string;
  modelVersion: string;
  processingTimeMs: number;
  recommendation: string;
}



