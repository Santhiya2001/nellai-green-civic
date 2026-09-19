interface LogoProps {
  size?: number;
  className?: string;
}

/**
 * The platform's mark: a water drop (Neervalam / water-resource focus)
 * containing a veined leaf (Green Nellai / afforestation focus) -- the two
 * halves of the platform's mission in one silhouette. Inline SVG so it's
 * crisp at any size with no image request.
 */
export default function Logo({ size = 40, className }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      className={className}
      role="img"
      aria-label="Nellai Green & Civic logo"
    >
      <defs>
        <linearGradient id="logo-g" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#239a63" />
          <stop offset="1" stopColor="#0f4d30" />
        </linearGradient>
      </defs>

      <path
        d="M32 58 C18.5 58 8.5 47.6 8.5 36.4 C8.5 22 27 5.5 30.6 2.6 C31.5 1.9 32.5 1.9 33.4 2.6 C37 5.5 55.5 22 55.5 36.4 C55.5 47.6 45.5 58 32 58 Z"
        fill="url(#logo-g)"
      />

      <path
        d="M32 44 C24 42 20.5 34.5 22.5 25.5 C23.7 20 27 15.8 32 13 C37 15.8 40.3 20 41.5 25.5 C43.5 34.5 40 42 32 44 Z"
        fill="#e7f3ea"
      />

      <g stroke="#1a7a4c" strokeLinecap="round" fill="none">
        <path d="M32 15 C32 24 32 35 32 43.3" strokeWidth={1.3} />
        <path d="M32 21 C29.2 22.3 27.3 24 26.2 26.3" strokeWidth={1} opacity={0.85} />
        <path d="M32 21 C34.8 22.3 36.7 24 37.8 26.3" strokeWidth={1} opacity={0.85} />
        <path d="M32 28.5 C28.9 30 26.8 32 25.6 34.6" strokeWidth={1} opacity={0.85} />
        <path d="M32 28.5 C35.1 30 37.2 32 38.4 34.6" strokeWidth={1} opacity={0.85} />
        <path d="M32 36 C29.6 37 28 38.3 27.1 40" strokeWidth={1} opacity={0.85} />
        <path d="M32 36 C34.4 37 36 38.3 36.9 40" strokeWidth={1} opacity={0.85} />
      </g>

      <path
        d="M18 33 C18.5 25 24 15.5 30 10"
        fill="none"
        stroke="#ffffff"
        strokeWidth={2.4}
        strokeLinecap="round"
        opacity={0.16}
      />
    </svg>
  );
}
