import { IconMoon, IconSun } from "./icons";
import { useTheme } from "../theme/ThemeContext";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div
      className="inline-flex rounded-lg border border-border bg-elevated p-0.5"
      role="group"
      aria-label="主题切换"
    >
      <button
        type="button"
        className={`inline-flex cursor-pointer items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 ${
          theme === "light" ? "bg-surface text-primary shadow-sm" : "text-muted hover:text-primary"
        }`}
        aria-pressed={theme === "light"}
        onClick={() => setTheme("light")}
      >
        <IconSun className="h-3.5 w-3.5" />
        浅色
      </button>
      <button
        type="button"
        className={`inline-flex cursor-pointer items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 ${
          theme === "dark" ? "bg-surface text-primary shadow-sm" : "text-muted hover:text-primary"
        }`}
        aria-pressed={theme === "dark"}
        onClick={() => setTheme("dark")}
      >
        <IconMoon className="h-3.5 w-3.5" />
        深色
      </button>
    </div>
  );
}
