export function SkeletonLine({ className = "h-4 w-full" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-elevated ${className}`} />;
}

export function HistoryListSkeleton() {
  return (
    <div className="space-y-2" aria-hidden="true">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="rounded-lg border border-border bg-elevated/50 px-3 py-3">
          <SkeletonLine className="h-4 w-24" />
          <SkeletonLine className="mt-2 h-3 w-full" />
        </div>
      ))}
    </div>
  );
}
