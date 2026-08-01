"use client";

import { useEffect, useState } from "react";

export function AnimatedCursor() {
  const [position, setPosition] = useState({ x: -100, y: -100 });
  const [pressed, setPressed] = useState(false);
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(pointer: fine)");
    setEnabled(media.matches);

    const move = (event: MouseEvent) => {
      setPosition({ x: event.clientX, y: event.clientY });
    };
    const down = () => setPressed(true);
    const up = () => setPressed(false);
    const update = () => setEnabled(media.matches);

    window.addEventListener("mousemove", move);
    window.addEventListener("mousedown", down);
    window.addEventListener("mouseup", up);
    media.addEventListener("change", update);

    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mousedown", down);
      window.removeEventListener("mouseup", up);
      media.removeEventListener("change", update);
    };
  }, []);

  if (!enabled) return null;

  return (
    <>
      <div
        className={`xb-cursor-ring ${pressed ? "xb-cursor-ring-pressed" : ""}`}
        style={{ transform: `translate3d(${position.x - 22}px, ${position.y - 22}px, 0)` }}
      />
      <div
        className={`xb-cursor-dot ${pressed ? "xb-cursor-dot-pressed" : ""}`}
        style={{ transform: `translate3d(${position.x - 5}px, ${position.y - 5}px, 0)` }}
      />
    </>
  );
}



