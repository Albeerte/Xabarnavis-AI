import { callAiServer, mockResult } from "./client";
import type { AnalysisResult } from "./types";

export async function analyzeText(input: { text?: string; url?: string }): Promise<AnalysisResult> {
  return (await callAiServer("/analyze/text", input)) ?? mockResult("TEXT", 8);
}



