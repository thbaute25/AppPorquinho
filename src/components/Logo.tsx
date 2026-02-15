export default function Logo({ width = 120 }: { width?: number }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 220"
      width={width}
      style={{ display: "block", margin: "0 auto" }}
    >
      <defs>
        <radialGradient id="bodyGrad" cx="50%" cy="40%" r="50%">
          <stop offset="0%" style={{ stopColor: "#FFB6C8" }} />
          <stop offset="100%" style={{ stopColor: "#FF8FAA" }} />
        </radialGradient>
        <radialGradient id="snoutGrad" cx="50%" cy="40%" r="50%">
          <stop offset="0%" style={{ stopColor: "#FFCCD5" }} />
          <stop offset="100%" style={{ stopColor: "#FFB3C1" }} />
        </radialGradient>
        <radialGradient id="coinGrad" cx="40%" cy="30%" r="60%">
          <stop offset="0%" style={{ stopColor: "#FFD700" }} />
          <stop offset="100%" style={{ stopColor: "#F0B800" }} />
        </radialGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="3" stdDeviation="4" floodColor="#00000020" />
        </filter>
      </defs>
      {/* Corpo */}
      <ellipse cx="100" cy="130" rx="72" ry="65" fill="url(#bodyGrad)" filter="url(#shadow)" />
      {/* Pernas */}
      <ellipse cx="60" cy="185" rx="16" ry="12" fill="#FF8FAA" />
      <ellipse cx="140" cy="185" rx="16" ry="12" fill="#FF8FAA" />
      {/* Orelhas */}
      <ellipse cx="55" cy="65" rx="22" ry="30" fill="#FF8FAA" transform="rotate(-20 55 65)" />
      <ellipse cx="55" cy="65" rx="14" ry="20" fill="#FFCCD5" transform="rotate(-20 55 65)" />
      <ellipse cx="145" cy="65" rx="22" ry="30" fill="#FF8FAA" transform="rotate(20 145 65)" />
      <ellipse cx="145" cy="65" rx="14" ry="20" fill="#FFCCD5" transform="rotate(20 145 65)" />
      {/* Cabeca */}
      <circle cx="100" cy="95" r="52" fill="url(#bodyGrad)" />
      {/* Olhos */}
      <circle cx="80" cy="88" r="7" fill="#2D2D3F" />
      <circle cx="120" cy="88" r="7" fill="#2D2D3F" />
      <circle cx="82" cy="85" r="2.5" fill="white" />
      <circle cx="122" cy="85" r="2.5" fill="white" />
      {/* Focinho */}
      <ellipse cx="100" cy="105" rx="20" ry="14" fill="url(#snoutGrad)" />
      <circle cx="93" cy="105" r="3" fill="#FF7A99" />
      <circle cx="107" cy="105" r="3" fill="#FF7A99" />
      {/* Bochecha */}
      <circle cx="65" cy="100" r="8" fill="#FF9AB8" opacity="0.5" />
      <circle cx="135" cy="100" r="8" fill="#FF9AB8" opacity="0.5" />
      {/* Sorriso */}
      <path d="M 90 112 Q 100 120 110 112" fill="none" stroke="#FF7A99" strokeWidth="2" strokeLinecap="round" />
      {/* Moeda */}
      <circle cx="158" cy="55" r="20" fill="url(#coinGrad)" filter="url(#shadow)" />
      <circle cx="158" cy="55" r="16" fill="none" stroke="#E5A600" strokeWidth="1.5" />
      <text x="158" y="61" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#B8860B" fontFamily="Arial">
        $
      </text>
    </svg>
  );
}
