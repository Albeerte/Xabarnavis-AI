"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

type Theme = "dark" | "light";

interface ThemeCtx { theme: Theme; setTheme: (t: Theme) => void; toggleTheme: () => void; }

const ThemeContext = createContext<ThemeCtx>({ theme: "dark", setTheme: () => {}, toggleTheme: () => {} });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");

  useEffect(() => {
    const saved = (localStorage.getItem("xbn-theme") as Theme) || "dark";
    applyTheme(saved);
    queueMicrotask(() => setThemeState(saved));
  }, []);

  const setTheme = (t: Theme) => {
    applyTheme(t);
    setThemeState(t);
    localStorage.setItem("xbn-theme", t);
  };

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

function applyTheme(t: Theme) {
  document.documentElement.setAttribute("data-theme", t);
}

export const useTheme = () => useContext(ThemeContext);



