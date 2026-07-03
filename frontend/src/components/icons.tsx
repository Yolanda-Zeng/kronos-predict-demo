type IconProps = { className?: string; active?: boolean };

const inactive = "text-muted";
const activeCls = "text-accent";

function tone(active?: boolean) {
  return active ? activeCls : inactive;
}

/** Duotone nav icon shell */
function IconShell({
  className = "h-5 w-5",
  active,
  children,
}: IconProps & { children: React.ReactNode }) {
  return (
    <svg className={`${className} ${tone(active)}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      {children}
    </svg>
  );
}

export function IconChart({ className = "h-5 w-5", active }: IconProps) {
  return (
    <IconShell className={className} active={active}>
      <rect x="3" y="14" width="4" height="7" rx="1.2" fill="currentColor" opacity={active ? 0.35 : 0.2} />
      <rect x="10" y="10" width="4" height="11" rx="1.2" fill="currentColor" opacity={active ? 0.55 : 0.35} />
      <rect x="17" y="6" width="4" height="15" rx="1.2" fill="currentColor" />
      <path d="M5 12.5 11 8.5l4 3 5-6.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </IconShell>
  );
}

export function IconHistory({ className = "h-5 w-5", active }: IconProps) {
  return (
    <IconShell className={className} active={active}>
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.75" opacity={active ? 1 : 0.7} />
      <circle cx="12" cy="12" r="5.5" fill="currentColor" opacity={active ? 0.18 : 0.1} />
      <path d="M12 7.5v5l3.2 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5.5 5.5 4 4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" opacity={0.6} />
    </IconShell>
  );
}

export function IconTune({ className = "h-5 w-5", active }: IconProps) {
  return (
    <IconShell className={className} active={active}>
      <path d="M5 7h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M5 12h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M5 17h12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="9" cy="7" r="2.2" fill="currentColor" />
      <circle cx="17" cy="12" r="2.2" fill="currentColor" opacity={active ? 1 : 0.75} />
      <circle cx="11" cy="17" r="2.2" fill="currentColor" opacity={active ? 0.85 : 0.65} />
    </IconShell>
  );
}

export function IconEmptyChart({ className = "h-8 w-8" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="5" fill="currentColor" opacity="0.08" />
      <rect x="6" y="14" width="3" height="5" rx="1" fill="currentColor" opacity="0.25" />
      <rect x="10.5" y="11" width="3" height="8" rx="1" fill="currentColor" opacity="0.4" />
      <rect x="15" y="8" width="3" height="11" rx="1" fill="currentColor" opacity="0.65" />
      <path d="M7 13.5 11.5 10 15 12l3.5-4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
    </svg>
  );
}

export function IconInfo({ className = "h-4 w-4" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" fill="currentColor" opacity="0.12" />
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.5" />
      <path d="M12 11v5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <circle cx="12" cy="8" r="1.1" fill="currentColor" />
    </svg>
  );
}

export function IconSun({ className = "h-4 w-4" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4.5" fill="currentColor" opacity="0.2" />
      <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.75" />
      <g stroke="currentColor" strokeWidth="1.75" strokeLinecap="round">
        <path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4l1.4-1.4M17 7l1.4-1.4" />
      </g>
    </svg>
  );
}

export function IconMoon({ className = "h-4 w-4" }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5 8.5 8.5 0 1 0 20.5 14.5Z"
        fill="currentColor"
        opacity="0.22"
      />
      <path
        d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5 8.5 8.5 0 1 0 20.5 14.5Z"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinejoin="round"
      />
    </svg>
  );
}
