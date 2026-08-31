# -*- coding: utf-8 -*-
"""
연간사업계획서 랜딩 페이지 (Streamlit)

- 레퍼런스: public/reference/annual-business-plan-landing-reference.png
- main.py 최초 진입 시 기존 작성 화면 대신 이 랜딩 화면을 표시한다.
- 버튼은 실제 st.button(클릭 가능)이며, 나머지 비주얼은 HTML/CSS+SVG 로 재현했다.
- render_landing() 은 "start" / "example" / None 을 반환하며 상태 전환은 main.py 가 수행한다.
"""

LANDING_STYLE = """
<style>
/* ===== 랜딩 전용 전역 오버라이드 (이 CSS는 랜딩 렌더 시에만 DOM에 존재) ===== */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #FAF7EC !important;
}
.main .block-container {
    background: transparent !important;
    max-width: 1400px !important;
    border: none !important;
    box-shadow: none !important;
    padding-top: 1.5rem !important;
}
#abp-landing { font-family: 'NanumGothic', 'Nanum Gothic', sans-serif; }

#abp-landing * { box-sizing: border-box; }

/* ---------------- 배경 도트 ---------------- */
.abp-dot {
    position: absolute; width: 14px; height: 14px; border-radius: 50%;
    pointer-events: none;
}

/* ---------------- 상단 리본 ---------------- */
.abp-top-ribbon {
    position: relative; width: 348px; max-width: 90%; height: 52px;
    margin: 0 auto 10px; background: #F6F1C4;
    border: 2.5px solid #3A3A3A; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; z-index: 3;
}
.abp-top-ribbon::before, .abp-top-ribbon::after {
    content: ""; position: absolute; top: 6px; width: 46px; height: 40px;
    background: #CBC887; border: 2.5px solid #3A3A3A; z-index: -1;
}
.abp-top-ribbon::before { left: -34px; clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 34% 50%); }
.abp-top-ribbon::after { right: -34px; clip-path: polygon(0 0, 100% 0, 66% 50%, 100% 100%, 0 100%); }
.abp-top-ribbon span { font-size: 21px; font-weight: 800; color: #3A3A3A; letter-spacing: -0.01em; }

/* ---------------- 하늘색 메인 제목 박스 ---------------- */
.abp-hero-box {
    position: relative; width: 820px; max-width: 100%; margin: 0 auto;
    padding: 44px 60px 54px; background: #BDE3F5;
    border: 3px solid #3A3A3A; border-radius: 30px;
    box-shadow: 0 6px 0 rgba(58,58,58,.18); text-align: center; z-index: 2;
}
.abp-title {
    margin: 0; font-size: 96px; line-height: 1; font-weight: 800; color: #FFFFFF;
    -webkit-text-stroke: 4px #3A3A3A; paint-order: stroke fill;
    text-shadow: 5px 6px 0 rgba(58,58,58,.22); letter-spacing: -0.02em;
}
.abp-subtitle { margin: 22px 0 0; font-size: 30px; line-height: 1.5; font-weight: 700; color: #3A3A3A; }
.abp-subtitle + .abp-subtitle { margin-top: 0; }

/* ---------------- 캐릭터 + 책상 ---------------- */
.abp-scene { position: relative; margin-top: -34px; display: flex; justify-content: center; z-index: 1; }
.abp-desk-scene { position: relative; width: 760px; max-width: 100%; display: flex; flex-direction: column; align-items: center; }
.abp-characters {
    display: flex; align-items: flex-end; justify-content: center; gap: 4px;
    margin-bottom: -92px; position: relative; z-index: 2;
}
.abp-character { width: 220px; height: auto; }
.abp-desk { position: relative; width: 100%; z-index: 1; }
.abp-desk-top { width: 100%; height: 26px; background: #F5EAD4; border: 3px solid #3A3A3A; border-radius: 8px; }
.abp-desk-front {
    width: 92%; height: 78px; margin: -3px auto 0; background: #EFE0C2;
    border: 3px solid #3A3A3A; border-top: none; border-radius: 0 0 14px 14px;
    clip-path: polygon(2% 0, 98% 0, 100% 100%, 0 100%);
}
.abp-desk-books { position: absolute; top: -50px; right: 34px; }
.abp-desk-books svg { width: 96px; height: auto; display: block; }

/* ---------------- 좌우 장식 ---------------- */
.abp-scene .abp-side { position: absolute; top: 0; width: 180px; height: 100%; pointer-events: none; }
.abp-side-left { left: 0; }
.abp-side-right { right: 0; }
.abp-deco { position: absolute; }
.abp-deco-clover-excl { width: 84px; top: -28px; left: 12px; }
.abp-deco-laptop { width: 128px; top: 130px; left: -8px; transform: rotate(-8deg); }
.abp-side-left .abp-deco-pencil { width: 34px; top: 300px; left: 24px; }
.abp-side-right .abp-deco-pencil { width: 34px; top: -34px; right: 30px; }
.abp-deco-book { width: 104px; top: 100px; right: -6px; transform: rotate(8deg); }
.abp-deco-clover-sparkle { width: 92px; top: 260px; right: 6px; }

/* ---------------- 이렇게 진행돼요! 패널 ---------------- */
.abp-process-row { display: flex; justify-content: center; align-items: stretch; gap: 28px; margin-top: 44px; }
.abp-process-panel {
    position: relative; width: 1020px; max-width: 100%;
    background: #FDFBF3; border: 2.5px dashed #3A3A3A; border-radius: 20px;
    padding: 52px 44px 40px;
}
.abp-process-ribbon {
    position: absolute; top: -22px; left: 50%; transform: translateX(-50%);
    background: #FBE88A; border: 2.5px solid #3A3A3A; border-radius: 8px;
    padding: 9px 34px; font-size: 20px; font-weight: 800; color: #3A3A3A; white-space: nowrap;
}
.abp-process-ribbon::before, .abp-process-ribbon::after {
    content: ""; position: absolute; top: 5px; width: 22px; height: 30px;
    background: #D9C25E; border: 2.5px solid #3A3A3A; z-index: -1;
}
.abp-process-ribbon::before { left: -18px; clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 40% 50%); }
.abp-process-ribbon::after { right: -18px; clip-path: polygon(0 0, 100% 0, 60% 50%, 100% 100%, 0 100%); }

.abp-steps { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.abp-step { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; text-align: center; }
.abp-step-icon { position: relative; width: 86px; height: 86px; display: flex; align-items: center; justify-content: center; }
.abp-step-icon svg { width: 86px; height: 86px; }
.abp-step-badge {
    position: absolute; top: -8px; left: -10px; width: 34px; height: 34px;
    border-radius: 50%; border: 2.5px solid #3A3A3A; color: #FFFFFF;
    font-size: 15px; font-weight: 800; display: flex; align-items: center;
    justify-content: center; z-index: 1;
}
.abp-step-title { margin: 14px 0 0; font-size: 22px; font-weight: 800; color: #3A3A3A; }
.abp-step-desc { margin: 6px 0 0; font-size: 15px; line-height: 1.45; color: #6B6B6B; word-break: keep-all; }
.abp-arrow { flex-shrink: 0; align-self: center; margin-top: 30px; font-size: 30px; color: #9A9A9A; line-height: 1; }

/* ---------------- 준비 자료 박스 ---------------- */
.abp-materials {
    position: relative; width: 250px; flex-shrink: 0;
    background: #EAF4E2; border: 2.5px solid #3A3A3A; border-radius: 16px;
    padding: 40px 22px 26px; text-align: center;
}
.abp-materials-tab {
    position: absolute; top: -18px; left: 50%; transform: translateX(-50%);
    background: #A5CF8D; border: 2.5px solid #3A3A3A; border-radius: 9999px;
    padding: 7px 26px; font-size: 18px; font-weight: 800; color: #FFFFFF; white-space: nowrap;
}
.abp-materials-icon { width: 88px; margin: 4px auto 0; display: block; }
.abp-materials-title { margin: 10px 0 0; font-size: 21px; font-weight: 800; color: #3A3A3A; }
.abp-materials-desc { margin: 8px 0 0; font-size: 14px; line-height: 1.5; font-weight: 600; color: #4F6B41; word-break: keep-all; }

/* ---------------- 하단 버튼 (실제 st.button) ---------------- */
.abp-btn-anchor { height: 0; }
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] {
    display: flex; justify-content: center; align-items: stretch; gap: 56px;
    margin-top: 44px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] button {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 2px; border-radius: 16px; cursor: pointer;
    font-family: 'NanumGothic', 'Nanum Gothic', sans-serif;
    transition: transform .15s ease;
    height: auto; min-height: 96px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] button:hover { transform: translateY(-2px); }
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button {
    background: #2BB8B8; border: 3px solid #3A3A3A;
    box-shadow: 0 6px 0 rgba(58,58,58,.25);
    color: #FFFFFF; font-size: 26px; font-weight: 800;
    padding: 14px 30px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
    background: #2CC4C4; border: 3px solid #3A3A3A; color: #FFFFFF;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button::after {
    content: "지금 바로 시작해요!"; display: block; font-size: 15px; font-weight: 600;
    color: rgba(255,255,255,.92); margin-top: 2px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button {
    background: #FFFFFF; border: 3px solid #3A3A3A;
    box-shadow: 0 6px 0 rgba(58,58,58,.15);
    color: #3A3A3A; font-size: 23px; font-weight: 800;
    padding: 11px 26px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button:hover {
    background: #FFFFFF; border: 3px solid #3A3A3A; color: #3A3A3A;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button::after {
    content: "작성 예시를 확인해보세요."; display: block; font-size: 14px; font-weight: 600;
    color: #6B6B6B; margin-top: 2px;
}

/* ---------------- 하단 안내 문구 ---------------- */
.abp-notice {
    margin-top: 30px; text-align: center; font-size: 17px; font-weight: 700;
    color: #4A4A4A; word-break: keep-all;
}

/* ---------------- 반응형 (깨짐 방지 최소한) ---------------- */
@media (max-width: 1280px) {
    .abp-hero-box { width: 100%; padding: 36px 40px 46px; }
    .abp-title { font-size: 76px; }
    .abp-subtitle { font-size: 25px; }
    .abp-desk-scene { width: 640px; }
    .abp-character { width: 190px; }
    .abp-scene .abp-side { width: 150px; }
    .abp-process-panel { padding: 48px 28px 34px; }
}
@media (max-width: 1024px) {
    .abp-title { font-size: 58px; -webkit-text-stroke: 3px #3A3A3A; }
    .abp-subtitle { font-size: 21px; }
    .abp-scene .abp-side { display: none; }
    .abp-desk-scene { width: 560px; }
    .abp-character { width: 170px; }
    .abp-process-row { flex-direction: column; align-items: center; gap: 40px; }
    .abp-process-panel { width: 100%; }
    .abp-steps { flex-wrap: wrap; gap: 20px 12px; }
    .abp-step { flex: 1 1 40%; }
    .abp-arrow { display: none; }
    .abp-materials { width: 100%; max-width: 430px; }
}
@media (max-width: 640px) {
    .abp-top-ribbon span { font-size: 17px; }
    .abp-hero-box { padding: 26px 18px 34px; border-radius: 22px; }
    .abp-title { font-size: 40px; -webkit-text-stroke: 2.5px #3A3A3A; }
    .abp-subtitle { margin-top: 14px; font-size: 16px; }
    .abp-desk-scene { width: 100%; }
    .abp-character { width: 42vw; max-width: 150px; }
    .abp-characters { margin-bottom: -64px; }
    .abp-desk-front { height: 54px; }
    .abp-desk-books { top: -38px; right: 10px; }
    .abp-desk-books svg { width: 68px; }
    .abp-process-ribbon { padding: 8px 20px; font-size: 17px; }
    .abp-process-panel { padding: 42px 16px 28px; }
    .abp-step { flex: 1 1 100%; }
    .abp-notice { font-size: 15px; }
}
</style>
"""

# ============================================================
# SVG 조각 (캐릭터·장식·아이콘)
# ============================================================

_SVG_UPLOAD = """
<svg viewBox="0 0 80 80" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M14 26 L26 12 H62 L70 26 V62 a4 4 0 0 1 -4 4 H18 a4 4 0 0 1 -4 -4 Z" fill="#F7CE55"/>
    <path d="M14 26 H70" fill="none"/>
    <circle cx="40" cy="48" r="14" fill="#FFFFFF"/>
    <path d="M40 55 V42 M34 47 L40 41 L46 47" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_ROBOT = """
<svg viewBox="0 0 80 80" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M40 14 V8" fill="none" stroke-linecap="round"/>
    <circle cx="40" cy="7" r="3.5" fill="#F272A8"/>
    <rect x="18" y="14" width="44" height="34" rx="10" fill="#FFFFFF"/>
    <circle cx="30" cy="29" r="4" fill="#3A3A3A" stroke="none"/>
    <circle cx="50" cy="29" r="4" fill="#3A3A3A" stroke="none"/>
    <path d="M32 38 Q40 43 48 38" fill="none" stroke-linecap="round"/>
    <rect x="32" y="48" width="16" height="10" rx="4" fill="#BDE3F5"/>
    <path d="M12 26 V40" fill="none" stroke-linecap="round"/>
    <circle cx="12" cy="43" r="3.5" fill="#F7CE55"/>
    <path d="M68 26 V40" fill="none" stroke-linecap="round"/>
    <circle cx="68" cy="43" r="3.5" fill="#F7CE55"/>
    <path d="M22 52 V62 M58 52 V62" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_DOC_CHART = """
<svg viewBox="0 0 80 80" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M18 8 H50 L64 22 V70 a3 3 0 0 1 -3 3 H18 a3 3 0 0 1 -3 -3 V11 a3 3 0 0 1 3 -3 Z" fill="#FFFFFF"/>
    <path d="M50 8 V22 H64" fill="#EDEAE0"/>
    <circle cx="34" cy="44" r="12" fill="#F7CE55"/>
    <path d="M34 32 V44 H46" fill="none" stroke-linecap="round"/>
    <path d="M24 64 H56 M24 70 H44" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_CALENDAR = """
<svg viewBox="0 0 80 80" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <rect x="12" y="16" width="56" height="56" rx="6" fill="#FFFFFF"/>
    <path d="M12 16 a6 6 0 0 1 6 -6 H62 a6 6 0 0 1 6 6 V30 H12 Z" fill="#F5A623"/>
    <path d="M26 8 V20 M54 8 V20" fill="none" stroke-linecap="round"/>
    <circle cx="40" cy="52" r="11" fill="#8FCB6B"/>
    <path d="M34 52 L39 57 L47 47" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_DOCUMENTS = """
<svg viewBox="0 0 80 70" class="abp-materials-icon" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M22 12 a3 3 0 0 1 3 -3 H44 L58 23 V57 a3 3 0 0 1 -3 3 H25 a3 3 0 0 1 -3 -3 Z" fill="#FFFFFF"/>
    <path d="M44 9 V23 H58" fill="#EDEAE0"/>
    <path d="M28 32 H52 M28 40 H52 M28 48 H44" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_CLOVER_EXCL = """
<svg viewBox="0 0 100 100" class="abp-deco abp-deco-clover-excl" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <ellipse cx="34" cy="34" rx="17" ry="17" fill="#8FCB6B"/>
    <ellipse cx="66" cy="34" rx="17" ry="17" fill="#8FCB6B"/>
    <ellipse cx="34" cy="66" rx="17" ry="17" fill="#8FCB6B"/>
    <ellipse cx="66" cy="66" rx="17" ry="17" fill="#8FCB6B"/>
    <ellipse cx="50" cy="50" rx="4" ry="4" fill="#FFFFFF"/>
    <path d="M50 36 V50 M50 58 v2" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_CLOVER_SPARKLE = """
<svg viewBox="0 0 100 100" class="abp-deco abp-deco-clover-sparkle" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <ellipse cx="34" cy="34" rx="16" ry="16" fill="#B5D96B"/>
    <ellipse cx="66" cy="34" rx="16" ry="16" fill="#B5D96B"/>
    <ellipse cx="34" cy="66" rx="16" ry="16" fill="#B5D96B"/>
    <ellipse cx="66" cy="66" rx="16" ry="16" fill="#B5D96B"/>
    <ellipse cx="50" cy="50" rx="4" ry="4" fill="#FFFFFF"/>
  </g>
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linecap="round">
    <path d="M14 8 L14 0 M10 4 H18" fill="none"/>
    <path d="M88 92 L88 84 M84 88 H92" fill="none"/>
  </g>
</svg>
"""

_SVG_LAPTOP = """
<svg viewBox="0 0 120 100" class="abp-deco abp-deco-laptop" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M24 16 a4 4 0 0 1 4 -4 H92 a4 4 0 0 1 4 4 V70 H24 Z" fill="#6B7280"/>
    <rect x="31" y="20" width="58" height="42" rx="2" fill="#BDE3F5"/>
    <path d="M14 70 H106 L112 80 a3 3 0 0 1 -3 4 H11 a3 3 0 0 1 -3 -4 Z" fill="#9CA3AF"/>
    <path d="M50 76 H70" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""


def _svg_pencil(rotation):
    return (
        '<svg viewBox="0 0 40 140" class="abp-deco abp-deco-pencil" '
        'style="transform: rotate(%ddeg)" aria-hidden="true">'
        '<g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">'
        '<rect x="10" y="26" width="20" height="86" fill="#F7CE55"/>'
        '<path d="M10 26 V112" fill="none"/>'
        '<path d="M10 112 H30 L20 134 Z" fill="#F7CE55"/>'
        '<path d="M10 112 V118 M30 112 V118" fill="none"/>'
        '<rect x="10" y="10" width="20" height="16" rx="4" fill="#F272A8"/>'
        "</g></svg>" % rotation
    )


_SVG_OPEN_BOOK = """
<svg viewBox="0 0 110 80" class="abp-deco abp-deco-book" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <path d="M55 18 C44 10 28 8 12 12 V62 C28 58 44 60 55 68 Z" fill="#FBD9C0"/>
    <path d="M55 18 C66 10 82 8 98 12 V62 C82 58 66 60 55 68 Z" fill="#FBD9C0"/>
    <path d="M55 18 V68" fill="none"/>
    <path d="M20 24 C30 21 40 22 48 27 M20 34 C30 31 40 32 48 37 M20 44 C30 41 40 42 48 47" fill="none" stroke="#C89B7B" stroke-width="2" stroke-linecap="round"/>
    <path d="M90 24 C80 21 70 22 62 27 M90 34 C80 31 70 32 62 37 M90 44 C80 41 70 42 62 47" fill="none" stroke="#C89B7B" stroke-width="2" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_BOOK_STACK = """
<svg viewBox="0 0 90 60" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round">
    <rect x="8" y="34" width="74" height="16" rx="3" fill="#E56B9F"/>
    <rect x="14" y="18" width="62" height="16" rx="3" fill="#8FCB6B"/>
    <path d="M24 40 H66 M30 24 H60" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
  </g>
</svg>
"""

_SVG_BOY = """
<svg viewBox="0 0 200 220" class="abp-character" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="3" stroke-linejoin="round">
    <path d="M60 130 C60 108 78 96 100 96 C122 96 140 108 140 130 V190 H60 Z" fill="#5B9BD5"/>
    <path d="M62 140 C48 150 42 164 44 178" fill="none" stroke-width="10" stroke="#5B9BD5" stroke-linecap="round"/>
    <path d="M138 140 C152 150 158 164 156 178" fill="none" stroke-width="10" stroke="#5B9BD5" stroke-linecap="round"/>
    <circle cx="44" cy="180" r="8" fill="#FFE3CF"/>
    <circle cx="156" cy="180" r="8" fill="#FFE3CF"/>
    <rect x="90" y="112" width="20" height="18" fill="#FFE3CF"/>
    <ellipse cx="100" cy="72" rx="46" ry="42" fill="#FFE3CF"/>
    <path d="M54 72 C54 42 74 28 100 28 C126 28 146 42 146 72 C146 60 138 52 128 50 C120 44 108 42 100 42 C92 42 80 44 72 50 C62 52 54 60 54 72 Z" fill="#4A3B32"/>
    <path d="M80 74 q6 -8 12 0" fill="none" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M108 74 q6 -8 12 0" fill="none" stroke-width="3.5" stroke-linecap="round"/>
    <ellipse cx="74" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none"/>
    <ellipse cx="126" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none"/>
    <path d="M92 90 q8 8 16 0" fill="none" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M64 186 C50 178 38 178 30 182 V196 C38 192 50 192 64 200 Z" fill="#E05252"/>
    <path d="M136 186 C150 178 162 178 170 182 V196 C162 192 150 192 136 200 Z" fill="#E05252"/>
    <path d="M100 190 C92 184 84 182 78 182 M100 190 C108 184 116 182 122 182" fill="none" stroke-width="3"/>
  </g>
</svg>
"""

_SVG_GIRL = """
<svg viewBox="0 0 200 220" class="abp-character" aria-hidden="true">
  <g stroke="#3A3A3A" stroke-width="3" stroke-linejoin="round">
    <path d="M60 130 C60 108 78 96 100 96 C122 96 140 108 140 130 V190 H60 Z" fill="#F08080"/>
    <path d="M64 138 C46 126 34 108 32 90" fill="none" stroke-width="10" stroke="#F08080" stroke-linecap="round"/>
    <path d="M136 138 C154 126 166 108 168 90" fill="none" stroke-width="10" stroke="#F08080" stroke-linecap="round"/>
    <circle cx="32" cy="86" r="8" fill="#FFE3CF"/>
    <circle cx="168" cy="86" r="8" fill="#FFE3CF"/>
    <rect x="90" y="112" width="20" height="18" fill="#FFE3CF"/>
    <ellipse cx="100" cy="72" rx="46" ry="42" fill="#FFE3CF"/>
    <path d="M52 66 C52 36 74 24 100 24 C126 24 148 36 148 66 L150 108 C150 114 144 116 140 110 L138 84 C130 74 116 68 100 68 C84 68 70 74 62 84 L60 110 C56 116 50 114 50 108 Z" fill="#A9764F"/>
    <path d="M80 74 q6 -8 12 0" fill="none" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M108 74 q6 -8 12 0" fill="none" stroke-width="3.5" stroke-linecap="round"/>
    <ellipse cx="74" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none"/>
    <ellipse cx="126" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none"/>
    <path d="M90 88 q10 12 20 0 Z" fill="#B55A5A" stroke-width="2.5"/>
  </g>
</svg>
"""

_STEPS = [
    ("01", "#2BB8B8", _SVG_UPLOAD, "자료 업로드", "기존 사업보고서나 관련 자료를 올려주세요."),
    ("02", "#F5A623", _SVG_ROBOT, "AI 분석·작성", "AI가 내용을 분석하여 계획 초안을 작성해드려요."),
    ("03", "#2BB8B8", _SVG_DOC_CHART, "연간 계획 완성", "연간 사업계획서를 한눈에 확인하고 수정해요."),
    ("04", "#F5A623", _SVG_CALENDAR, "월간 계획 생성", "월간 사업계획서(12개월)를 자동으로 만들어드려요."),
]


def _build_landing_html():
    steps_html = ""
    for i, (num, color, icon, title, desc) in enumerate(_STEPS):
        if i > 0:
            steps_html += '<span class="abp-arrow">➜</span>'
        steps_html += (
            '<div class="abp-step">'
            '<div class="abp-step-icon">'
            '<span class="abp-step-badge" style="background:%s">%s</span>%s</div>'
            '<p class="abp-step-title">%s</p>'
            '<p class="abp-step-desc">%s</p></div>' % (color, num, icon, title, desc)
        )

    return """
<div id="abp-landing">
  <span class="abp-dot" style="top:8%;left:22%;background:#F272A8"></span>
  <span class="abp-dot" style="top:15%;left:8%;background:#35C4C8"></span>
  <span class="abp-dot" style="top:40%;left:3%;background:#F5D442"></span>
  <span class="abp-dot" style="top:70%;left:6%;background:#B5D96B"></span>
  <span class="abp-dot" style="top:10%;right:6%;background:#F272A8"></span>
  <span class="abp-dot" style="top:35%;right:4%;background:#35C4C8"></span>
  <span class="abp-dot" style="top:55%;right:10%;background:#F5D442"></span>
  <span class="abp-dot" style="top:82%;right:3%;background:#B5D96B"></span>

  <div class="abp-top-ribbon"><span>AI와 함께 쉽고 빠르게!</span></div>

  <div class="abp-hero-box">
    <h1 class="abp-title">연간사업계획서</h1>
    <p class="abp-subtitle">우리 기관의 비전과 계획을 한눈에!</p>
    <p class="abp-subtitle">AI가 연간·월간 사업계획서 작성을 도와드립니다.</p>
  </div>

  <div class="abp-scene">
    <div class="abp-side abp-side-left">
      __CLOVER_EXCL__
      __LAPTOP__
      __PENCIL_LEFT__
    </div>
    <div class="abp-desk-scene">
      <div class="abp-characters">
        __BOY__
        __GIRL__
      </div>
      <div class="abp-desk">
        <div class="abp-desk-top"></div>
        <div class="abp-desk-front"></div>
        <div class="abp-desk-books">__BOOK_STACK__</div>
      </div>
    </div>
    <div class="abp-side abp-side-right">
      __PENCIL_RIGHT__
      __OPEN_BOOK__
      __CLOVER_SPARKLE__
    </div>
  </div>

  <div class="abp-process-row">
    <div class="abp-process-panel">
      <div class="abp-process-ribbon">이렇게 진행돼요!</div>
      <div class="abp-steps">__STEPS__</div>
    </div>
    <div class="abp-materials">
      <div class="abp-materials-tab">준비 자료</div>
      __DOCUMENTS__
      <p class="abp-materials-title">PDF, DOCX 등</p>
      <p class="abp-materials-desc">사업보고서, 계획서, 평가서, 참고자료 등 다양한 형식 가능!</p>
    </div>
  </div>
</div>
""".replace("__CLOVER_EXCL__", _SVG_CLOVER_EXCL).replace(
    "__LAPTOP__", _SVG_LAPTOP
).replace("__PENCIL_LEFT__", _svg_pencil(-35)).replace(
    "__PENCIL_RIGHT__", _svg_pencil(30)
).replace("__BOY__", _SVG_BOY).replace("__GIRL__", _SVG_GIRL).replace(
    "__BOOK_STACK__", _SVG_BOOK_STACK
).replace("__OPEN_BOOK__", _SVG_OPEN_BOOK).replace(
    "__CLOVER_SPARKLE__", _SVG_CLOVER_SPARKLE
).replace("__DOCUMENTS__", _SVG_DOCUMENTS).replace("__STEPS__", steps_html)


def render_landing():
    """랜딩 화면 렌더링. 반환값: "start" | "example" | None"""
    import streamlit as st

    st.markdown(LANDING_STYLE, unsafe_allow_html=True)
    st.markdown(_build_landing_html(), unsafe_allow_html=True)

    # 실제 클릭 가능한 버튼 (CSS 로 레퍼런스 스타일 적용)
    st.markdown('<div class="abp-btn-anchor"></div>', unsafe_allow_html=True)
    start_col, example_col = st.columns([1.2, 1], gap="large")

    action = None
    with start_col:
        if st.button("✏️ 연간사업계획서 작성하기",
                     key="abp_btn_start",
                     use_container_width=True,
                     type="primary"):
            action = "start"
    with example_col:
        if st.button("📖 예시로 살펴보기",
                     key="abp_btn_example",
                     use_container_width=True):
            action = "example"

    st.markdown(
        '<div class="abp-notice">💡 처음이신가요? 걱정 마세요! '
        "따라하기 쉽도록 안내해드릴게요. 😊</div>",
        unsafe_allow_html=True,
    )
    return action
