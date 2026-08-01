import { callAiServer, mockResult } from "./client";
import type { AnalysisResult } from "./types";

export async function analyzeImage(input: FormData): Promise<AnalysisResult> {
  return (await callAiServer("/analyze/image", input)) ?? mockResult("IMAGE", 0);
}



