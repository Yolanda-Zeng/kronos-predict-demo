type BrandMarkProps = {
  className?: string;
  size?: number;
};

/** Kronos brand mark — matches favicon, indigo→violet gradient + time arc */
export default function BrandMark({ className = "", size = 40 }: BrandMarkProps) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="kronos-bg" x1="4" y1="2" x2="28" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366F1" />
          <stop offset="1" stopColor="#7C3AED" />
        </linearGradient>
        <linearGradient id="kronos-shine" x1="8" y1="6" x2="24" y2="26" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFFFFF" stopOpacity="0.95" />
          <stop offset="1" stopColor="#C7D2FE" stopOpacity="0.85" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#kronos-bg)" />
      <path
        d="M8 9.5h2.8v5.2l6.2-5.2h3.4l-5.8 4.9 6.4 8.6h-3.3l-5.1-6.9-1.8 1.5v5.4H8V9.5Z"
        fill="url(#kronos-shine)"
      />
      <path
        d="M22.5 8.5c1.2.8 2 2.2 2 3.8 0 2.5-2 4.5-4.5 4.5-.6 0-1.2-.1-1.7-.4"
        stroke="#E0E7FF"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <circle cx="22.5" cy="12.3" r="1.1" fill="#E0E7FF" />
    </svg>
  );
}
