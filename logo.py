import base64
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# SVG inline do porquinho - baseado na mascote do projeto
PORQUINHO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220">
  <defs>
    <radialGradient id="bodyGrad" cx="50%" cy="40%" r="50%">
      <stop offset="0%" style="stop-color:#FFB6C8"/>
      <stop offset="100%" style="stop-color:#FF8FAA"/>
    </radialGradient>
    <radialGradient id="snoutGrad" cx="50%" cy="40%" r="50%">
      <stop offset="0%" style="stop-color:#FFCCD5"/>
      <stop offset="100%" style="stop-color:#FFB3C1"/>
    </radialGradient>
    <radialGradient id="coinGrad" cx="40%" cy="30%" r="60%">
      <stop offset="0%" style="stop-color:#FFD700"/>
      <stop offset="100%" style="stop-color:#F0B800"/>
    </radialGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#00000020"/>
    </filter>
  </defs>
  <!-- Corpo -->
  <ellipse cx="100" cy="130" rx="72" ry="65" fill="url(#bodyGrad)" filter="url(#shadow)"/>
  <!-- Pernas -->
  <ellipse cx="60" cy="185" rx="16" ry="12" fill="#FF8FAA"/>
  <ellipse cx="140" cy="185" rx="16" ry="12" fill="#FF8FAA"/>
  <!-- Orelhas -->
  <ellipse cx="55" cy="65" rx="22" ry="30" fill="#FF8FAA" transform="rotate(-20 55 65)"/>
  <ellipse cx="55" cy="65" rx="14" ry="20" fill="#FFCCD5" transform="rotate(-20 55 65)"/>
  <ellipse cx="145" cy="65" rx="22" ry="30" fill="#FF8FAA" transform="rotate(20 145 65)"/>
  <ellipse cx="145" cy="65" rx="14" ry="20" fill="#FFCCD5" transform="rotate(20 145 65)"/>
  <!-- Cabeca -->
  <circle cx="100" cy="95" r="52" fill="url(#bodyGrad)"/>
  <!-- Olhos -->
  <circle cx="80" cy="88" r="7" fill="#2D2D3F"/>
  <circle cx="120" cy="88" r="7" fill="#2D2D3F"/>
  <circle cx="82" cy="85" r="2.5" fill="white"/>
  <circle cx="122" cy="85" r="2.5" fill="white"/>
  <!-- Focinho -->
  <ellipse cx="100" cy="105" rx="20" ry="14" fill="url(#snoutGrad)"/>
  <circle cx="93" cy="105" r="3" fill="#FF7A99"/>
  <circle cx="107" cy="105" r="3" fill="#FF7A99"/>
  <!-- Bochecha -->
  <circle cx="65" cy="100" r="8" fill="#FF9AB8" opacity="0.5"/>
  <circle cx="135" cy="100" r="8" fill="#FF9AB8" opacity="0.5"/>
  <!-- Sorriso -->
  <path d="M 90 112 Q 100 120 110 112" fill="none" stroke="#FF7A99" stroke-width="2" stroke-linecap="round"/>
  <!-- Moeda -->
  <circle cx="158" cy="55" r="20" fill="url(#coinGrad)" filter="url(#shadow)"/>
  <circle cx="158" cy="55" r="16" fill="none" stroke="#E5A600" stroke-width="1.5"/>
  <text x="158" y="61" text-anchor="middle" font-size="18" font-weight="bold" fill="#B8860B" font-family="Arial">$</text>
</svg>'''


def get_logo_html(width=120):
    """Retorna HTML da logo do porquinho para usar em st.markdown()"""
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" width="{width}" style="display:block;margin:0 auto;">'
    # Fallback: SVG inline
    svg_b64 = base64.b64encode(PORQUINHO_SVG.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{svg_b64}" width="{width}" style="display:block;margin:0 auto;">'


def get_logo_sidebar_html(width=80):
    """Logo menor para a sidebar"""
    return get_logo_html(width)
