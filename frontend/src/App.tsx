import { useMemo, useState } from "react";
import BrandMark from "./components/BrandMark";
import { IconChart, IconHistory, IconTune } from "./components/icons";
import ThemeToggle from "./components/ThemeToggle";
import HistoryPage from "./pages/HistoryPage";
import PredictPage from "./pages/PredictPage";
import TunePage from "./pages/TunePage";
import type { PredictFormValues, PredictResult } from "./types";
import { defaultPredictForm } from "./types";

type Tab = "predict" | "history" | "tune";

const tabMeta: Record<Tab, { label: string; icon: typeof IconChart; hint: string }> = {
  predict: { label: "预测", icon: IconChart, hint: "运行预测并查看图表" },
  history: { label: "历史", icon: IconHistory, hint: "浏览过往预测记录" },
  tune: { label: "调参", icon: IconTune, hint: "网格搜索最优参数" },
};

export default function App() {
  const [tab, setTab] = useState<Tab>("predict");
  const [form, setForm] = useState<PredictFormValues>(defaultPredictForm);
  const [sharedResult, setSharedResult] = useState<PredictResult | null>(null);

  const tabs = useMemo(() => (["predict", "history", "tune"] as const).map((id) => ({ id, ...tabMeta[id] })), []);

  return (
    <div className="min-h-screen bg-base">
      <header className="sticky top-0 z-40 border-b border-border/80 bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <BrandMark size={44} className="shrink-0 drop-shadow-sm" />
            <div>
              <h1 className="bg-gradient-to-r from-accent to-accent-secondary bg-clip-text text-xl font-bold tracking-tight text-transparent">
                Kronos
              </h1>
              <p className="text-sm text-muted">A 股 / 港美股 K 线预测 · 交互图表 · 历史记录</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <ThemeToggle />
            <nav className="flex flex-wrap gap-1 rounded-xl border border-border bg-elevated/80 p-1" aria-label="主导航">
              {tabs.map((item) => {
                const Icon = item.icon;
                const active = tab === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    title={item.hint}
                    aria-current={active ? "page" : undefined}
                    className={active ? "tab-active" : "tab"}
                    onClick={() => setTab(item.id)}
                  >
                    <Icon className="h-5 w-5" active={active} />
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6">
        {tab === "predict" && (
          <PredictPage form={form} setForm={setForm} result={sharedResult} setResult={setSharedResult} />
        )}
        {tab === "history" && (
          <HistoryPage
            onOpenResult={(result) => {
              setSharedResult(result);
              setTab("predict");
            }}
          />
        )}
        {tab === "tune" && <TunePage form={form} setForm={setForm} onApplyBest={setForm} />}
      </main>
    </div>
  );
}
