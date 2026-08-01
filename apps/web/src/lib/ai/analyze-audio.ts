import { callAiServer, mockResult } from "./client";
import type { AnalysisResult } from "./types";

export async function analyzeAudio(input: FormData): Promise<AnalysisResult> {
  return (await callAiServer("/analyze/audio", input)) ?? mockResult("AUDIO", 12);
}



