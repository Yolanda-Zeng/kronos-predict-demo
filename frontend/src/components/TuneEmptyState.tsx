import { IconTune } from "./icons";

export default function TuneEmptyState() {
  return (
    <div className="card space-y-4 py-10 text-center">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/10 text-accent ring-1 ring-accent/20">
        <IconTune className="h-7 w-7" />
      </div>
      <div>
        <h3 className="text-base font-semibold">尚未开始调参</h3>
        <p className="mt-1 text-sm text-muted">网格搜索耗时较长，建议先用预设试跑。</p>
      </div>
      <ol className="mx-auto max-w-sm space-y-2.5 text-left text-sm text-muted">
        <li className="flex gap-3 rounded-lg bg-elevated/40 px-3 py-2">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
            1
          </span>
          <span>选择「快速试跑 / 标准 / 精细」预设，或手动填写 grid 参数</span>
        </li>
        <li className="flex gap-3 rounded-lg bg-elevated/40 px-3 py-2">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
            2
          </span>
          <span>查看组合数与预计耗时，确认不会跑太久</span>
        </li>
        <li className="flex gap-3 rounded-lg bg-elevated/40 px-3 py-2">
          <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
            3
          </span>
          <span>点击「开始调参」，完成后查看 MAPE 图表与排序表格</span>
        </li>
      </ol>
      <p className="text-xs text-muted">右侧调试指南含推荐调参顺序与常见问题排查。</p>
    </div>
  );
}
