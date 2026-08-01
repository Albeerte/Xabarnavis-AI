import { callAiServer, mockResult } from "./client";
import type { AnalysisResult } from "./types";

export async function analyzeVideo(input: FormData): Promise<AnalysisResult> {
  return (await callAiServer("/analyze/video", input)) ?? mockResult("VIDEO", 18);
}



