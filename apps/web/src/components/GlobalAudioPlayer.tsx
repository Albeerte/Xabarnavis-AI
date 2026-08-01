"use client";

import { useEffect, useRef, useState } from "react";
import { Download, Music2, Pause, Play, X } from "lucide-react";

const TRACK_SRC = "/audio/xabarnavis-ai.mp3";

export function GlobalAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isVisible, setIsVisible] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const updateTime = () => setCurrentTime(audio.currentTime || 0);
    const updateDuration = () => setDuration(audio.duration || 0);
    const stopPlaying = () => setIsPlaying(false);
    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("ended", stopPlaying);
    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("ended", stopPlaying);
    };
  }, []);

  if (!isVisible) return null;

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  async function togglePlay() {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      await audio.play();
      setIsPlaying(true);
    } else {
      audio.pause();
      setIsPlaying(false);
    }
  }

  function seek(value: string) {
    const audio = audioRef.current;
    if (!audio || duration <= 0) return;
    audio.currentTime = (Number(value) / 100) * duration;
  }

  return (
    <div className="fixed inset-x-0 top-0 z-[80] border-b border-amber-400/25 bg-[#070a14]/95 text-white shadow-[0_12px_35px_rgba(0,0,0,0.35)] backdrop-blur-xl">
      <audio ref={audioRef} src={TRACK_SRC} preload="metadata" />
      <div className="mx-auto grid h-12 max-w-7xl grid-cols-[minmax(180px,1fr)_auto_minmax(220px,2fr)_auto] items-center gap-5 px-4">
        <div className="flex min-w-0 items-center gap-3">
          <Music2 className="h-5 w-5 flex-shrink-0 text-amber-300" />
          <div className="min-w-0 leading-none">
            <p className="truncate text-[10px] font-black uppercase tracking-[0.18em] text-amber-300">Xabarnavis AI audio</p>
            <p className="mt-1 truncate text-sm font-bold text-slate-100">Xabarnavis AI</p>
          </div>
        </div>

        <button
          type="button"
          onClick={togglePlay}
          className="grid h-9 w-9 place-items-center rounded-xl border border-indigo-400/40 bg-indigo-500/15 text-indigo-200 shadow-[0_0_18px_rgba(99,102,241,0.25)] transition hover:bg-indigo-500/25"
          aria-label={isPlaying ? "Pause music" : "Play music"}
        >
          {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="ml-0.5 h-4 w-4" />}
        </button>

        <div className="flex min-w-0 items-center gap-3">
          <input
            type="range"
            min="0"
            max="100"
            value={progress}
            onChange={(event) => seek(event.target.value)}
            className="audio-player-range"
            aria-label="Audio progress"
          />
          <span className="w-11 text-right font-mono text-xs text-slate-400">{formatTime(currentTime)}</span>
        </div>

        <div className="flex items-center gap-2">
          <a
            href={TRACK_SRC}
            download
            className="grid h-8 w-8 place-items-center rounded-lg text-slate-300 transition hover:bg-white/10 hover:text-white"
            aria-label="Download audio"
          >
            <Download className="h-4 w-4" />
          </a>
          <button
            type="button"
            onClick={() => {
              audioRef.current?.pause();
              setIsPlaying(false);
              setIsVisible(false);
            }}
            className="grid h-8 w-8 place-items-center rounded-lg text-slate-300 transition hover:bg-white/10 hover:text-white"
            aria-label="Close audio player"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function formatTime(value: number) {
  if (!Number.isFinite(value)) return "0:00";
  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}



