# -*- coding: utf-8 -*-
"""
연간사업계획서 랜딩 페이지 (Streamlit)

- 히어로(상단 제목/캐릭터/책상) 영역: public/reference/annual-business-plan-hero-reference.png
  원본 이미지를 그대로 st.image 로 표시한다 (종횡비 유지).
- 그 아래 '이렇게 진행돼요!' 01~04 / 준비 자료 / CTA 버튼 / 안내 문구는 기존 구조 유지.
- 버튼은 실제 st.button(클릭 가능).
- render_landing() 은 "start" / "example" / None 을 반환하며 상태 전환은 main.py 가 수행한다.

[HTML 노출 방지]
st.markdown 의 마크다운 파서는 빈 줄에서 HTML 블록을 종료하고, 이어지는
들여쓰기 라인을 코드 블록으로 해석할 수 있다. 이로 인해 다중 줄 SVG/HTML이
텍스트로 노출되었으므로, 본문 HTML 은 렌더 직전에 모든 연속 공백을 1칸으로
정규화하여 "빈 줄 없는 단일 HTML 블록"으로 만들어 전달한다.
"""

from pathlib import Path

# 히어로 원본 이미지 (임의 가공 금지 - 원본 그대로 표시)
HERO_IMAGE_PATH = (
    Path(__file__).parent / "public" / "reference"
    / "annual-business-plan-hero-reference.png"
)

LANDING_STYLE = """
<style>
/* ===== 랜딩 전용 전역 오버라이드 (이 CSS는 랜딩 렌더 시에만 DOM에 존재) ===== */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #FAF7EC !important;
}
.main .block-container {
    background: transparent !important;
    max-width: 1080px !important;
    border: none !important;
    box-shadow: none !important;
    padding-top: 1.2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
#abp-landing { font-family: 'NanumGothic', 'Nanum Gothic', sans-serif; }
#abp-landing * { box-sizing: border-box; }

/* 히어로 원본 이미지: 최대폭 축소·중앙 정렬, 종횡비 유지 (왜곡/크롭 금지) */
[data-testid="stImageContainer"] {
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stImageContainer"] img {
    width: min(760px, 100%) !important;
    height: auto !important;
    object-fit: contain !important;
}

/* ---------------- 이렇게 진행돼요! 패널 ---------------- */
.abp-process-row {
    display: flex; justify-content: center; align-items: stretch;
    gap: 32px; margin-top: 40px;
}
.abp-process-panel {
    position: relative; flex: 1 1 auto; min-width: 0;
    background: #FDFBF3; border: 2.5px dashed #3A3A3A; border-radius: 20px;
    padding: 54px 40px 42px;
}
.abp-process-ribbon {
    position: absolute; top: -22px; left: 50%; transform: translateX(-50%);
    background: #FBE88A; border: 2.5px solid #3A3A3A; border-radius: 8px;
    padding: 9px 34px; font-size: 21px; font-weight: 800; color: #3A3A3A; white-space: nowrap;
}
.abp-process-ribbon::before, .abp-process-ribbon::after {
    content: ""; position: absolute; top: 5px; width: 22px; height: 30px;
    background: #D9C25E; border: 2.5px solid #3A3A3A; z-index: -1;
}
.abp-process-ribbon::before { left: -18px; clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 40% 50%); }
.abp-process-ribbon::after { right: -18px; clip-path: polygon(0 0, 100% 0, 60% 50%, 100% 100%, 0 100%); }

.abp-steps { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.abp-step { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; text-align: center; }
.abp-step-icon { position: relative; width: 88px; height: 88px; display: flex; align-items: center; justify-content: center; }
.abp-step-icon svg { width: 88px; height: 88px; }
.abp-step-badge {
    position: absolute; top: -8px; left: -10px; width: 36px; height: 36px;
    border-radius: 50%; border: 2.5px solid #3A3A3A; color: #FFFFFF;
    font-size: 16px; font-weight: 800; display: flex; align-items: center;
    justify-content: center; z-index: 1;
}
.abp-step-title { margin: 16px 0 0; font-size: 23px; font-weight: 800; color: #3A3A3A; }
.abp-step-desc { margin: 8px 0 0; font-size: 16px; line-height: 1.5; color: #6B6B6B; word-break: keep-all; }
.abp-arrow { flex-shrink: 0; align-self: center; margin-top: 32px; font-size: 30px; color: #9A9A9A; line-height: 1; }

/* ---------------- 준비 자료 박스 ---------------- */
.abp-materials {
    position: relative; width: 252px; flex-shrink: 0;
    display: flex; flex-direction: column; justify-content: center;
    background: #EAF4E2; border: 2.5px solid #3A3A3A; border-radius: 16px;
    padding: 44px 24px 30px; text-align: center;
}
.abp-materials-tab {
    position: absolute; top: -18px; left: 50%; transform: translateX(-50%);
    background: #A5CF8D; border: 2.5px solid #3A3A3A; border-radius: 9999px;
    padding: 7px 26px; font-size: 19px; font-weight: 800; color: #FFFFFF; white-space: nowrap;
}
.abp-materials-icon { width: 92px; margin: 4px auto 0; display: block; }
.abp-materials-title { margin: 12px 0 0; font-size: 22px; font-weight: 800; color: #3A3A3A; }
.abp-materials-desc { margin: 10px 0 0; font-size: 15px; line-height: 1.55; font-weight: 600; color: #4F6B41; word-break: keep-all; }

/* ---------------- 하단 버튼 (실제 st.button) ---------------- */
.abp-btn-anchor { height: 0; }
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] {
    display: flex; justify-content: center; align-items: stretch; gap: 48px;
    margin-top: 48px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div { flex: 1 1 0; }
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] button {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 3px; border-radius: 16px; cursor: pointer; width: 100%;
    font-family: 'NanumGothic', 'Nanum Gothic', sans-serif;
    transition: transform .15s ease;
    height: auto; min-height: 104px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] button:hover { transform: translateY(-2px); }
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button {
    background: #2BB8B8; border: 3px solid #3A3A3A;
    box-shadow: 0 6px 0 rgba(58,58,58,.25);
    color: #FFFFFF; font-size: 26px; font-weight: 800;
    padding: 16px 30px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
    background: #2CC4C4; border: 3px solid #3A3A3A; color: #FFFFFF;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:first-child button::after {
    content: "지금 바로 시작해요!"; display: block; font-size: 16px; font-weight: 600;
    color: rgba(255,255,255,.92); margin-top: 3px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button {
    background: #FFFFFF; border: 3px solid #3A3A3A;
    box-shadow: 0 6px 0 rgba(58,58,58,.15);
    color: #3A3A3A; font-size: 25px; font-weight: 800;
    padding: 16px 30px;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button:hover {
    background: #FFFFFF; border: 3px solid #3A3A3A; color: #3A3A3A;
}
.abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div:last-child button::after {
    content: "작성 예시를 확인해보세요."; display: block; font-size: 15px; font-weight: 600;
    color: #6B6B6B; margin-top: 3px;
}

/* ---------------- 하단 안내 문구 ---------------- */
.abp-notice {
    margin-top: 36px; text-align: center; font-size: 18px; font-weight: 700;
    color: #4A4A4A; word-break: keep-all;
}

/* ---------------- 반응형 (PC 우선, 모바일 종횡비 유지) ---------------- */
@media (max-width: 1280px) {
    [data-testid="stImageContainer"] img { width: min(700px, 100%) !important; }
    .abp-process-panel { padding: 50px 30px 36px; }
}
@media (max-width: 1024px) {
    [data-testid="stImageContainer"] img { width: min(620px, 100%) !important; }
    .abp-process-row { flex-direction: column; align-items: center; gap: 44px; }
    .abp-process-panel { width: 100%; }
    .abp-steps { flex-wrap: wrap; gap: 24px 14px; }
    .abp-step { flex: 1 1 40%; }
    .abp-arrow { display: none; }
    .abp-materials { width: 100%; max-width: 460px; }
    .abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] { flex-direction: column; align-items: center; gap: 20px; }
    .abp-btn-anchor ~ div[data-testid="stHorizontalBlock"] > div { flex: 0 0 auto; width: 100%; max-width: 460px; }
}
@media (max-width: 640px) {
    .abp-process-ribbon { padding: 8px 20px; font-size: 17px; }
    .abp-process-panel { padding: 44px 18px 30px; }
    .abp-step { flex: 1 1 100%; }
    .abp-step-title { font-size: 20px; }
    .abp-step-desc { font-size: 15px; }
    .abp-notice { font-size: 15px; }
}
</style>
"""

# ============================================================
# 01~04 단계 아이콘 SVG (히어로 이미지 아래 섹션에만 사용)
# ============================================================

_SVG_UPLOAD = '<svg viewBox="0 0 80 80" aria-hidden="true"><g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round"><path d="M14 26 L26 12 H62 L70 26 V62 a4 4 0 0 1 -4 4 H18 a4 4 0 0 1 -4 -4 Z" fill="#F7CE55"/><path d="M14 26 H70" fill="none"/><circle cx="40" cy="48" r="14" fill="#FFFFFF"/><path d="M40 55 V42 M34 47 L40 41 L46 47" fill="none" stroke-linecap="round"/></g></svg>'

_SVG_ROBOT = '<svg viewBox="0 0 80 80" aria-hidden="true"><g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round"><path d="M40 14 V8" fill="none" stroke-linecap="round"/><circle cx="40" cy="7" r="3.5" fill="#F272A8"/><rect x="18" y="14" width="44" height="34" rx="10" fill="#FFFFFF"/><circle cx="30" cy="29" r="4" fill="#3A3A3A" stroke="none"/><circle cx="50" cy="29" r="4" fill="#3A3A3A" stroke="none"/><path d="M32 38 Q40 43 48 38" fill="none" stroke-linecap="round"/><rect x="32" y="48" width="16" height="10" rx="4" fill="#BDE3F5"/><path d="M12 26 V40" fill="none" stroke-linecap="round"/><circle cx="12" cy="43" r="3.5" fill="#F7CE55"/><path d="M68 26 V40" fill="none" stroke-linecap="round"/><circle cx="68" cy="43" r="3.5" fill="#F7CE55"/><path d="M22 52 V62 M58 52 V62" fill="none" stroke-linecap="round"/></g></svg>'

_SVG_DOC_CHART = '<svg viewBox="0 0 80 80" aria-hidden="true"><g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round"><path d="M18 8 H50 L64 22 V70 a3 3 0 0 1 -3 3 H18 a3 3 0 0 1 -3 -3 V11 a3 3 0 0 1 3 -3 Z" fill="#FFFFFF"/><path d="M50 8 V22 H64" fill="#EDEAE0"/><circle cx="34" cy="44" r="12" fill="#F7CE55"/><path d="M34 32 V44 H46" fill="none" stroke-linecap="round"/><path d="M24 64 H56 M24 70 H44" fill="none" stroke-linecap="round"/></g></svg>'

_SVG_CALENDAR = '<svg viewBox="0 0 80 80" aria-hidden="true"><g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round"><rect x="12" y="16" width="56" height="56" rx="6" fill="#FFFFFF"/><path d="M12 16 a6 6 0 0 1 6 -6 H62 a6 6 0 0 1 6 6 V30 H12 Z" fill="#F5A623"/><path d="M26 8 V20 M54 8 V20" fill="none" stroke-linecap="round"/><circle cx="40" cy="52" r="11" fill="#8FCB6B"/><path d="M34 52 L39 57 L47 47" fill="none" stroke-linecap="round"/></g></svg>'

_SVG_DOCUMENTS = '<svg viewBox="0 0 80 70" class="abp-materials-icon" aria-hidden="true"><g stroke="#3A3A3A" stroke-width="2.5" stroke-linejoin="round"><path d="M22 12 a3 3 0 0 1 3 -3 H44 L58 23 V57 a3 3 0 0 1 -3 3 H25 a3 3 0 0 1 -3 -3 Z" fill="#FFFFFF"/><path d="M44 9 V23 H58" fill="#EDEAE0"/><path d="M28 32 H52 M28 40 H52 M28 48 H44" fill="none" stroke-linecap="round"/></g></svg>'

_STEPS = [
    ("01", "#2BB8B8", _SVG_UPLOAD, "자료 업로드", "기존 사업보고서나 관련 자료를 올려주세요."),
    ("02", "#F5A623", _SVG_ROBOT, "AI 분석·작성", "AI가 내용을 분석하여 계획 초안을 작성해드려요."),
    ("03", "#2BB8B8", _SVG_DOC_CHART, "연간 계획 완성", "연간 사업계획서를 한눈에 확인하고 수정해요."),
    ("04", "#F5A623", _SVG_CALENDAR, "월간 계획 생성", "월간 사업계획서(12개월)를 자동으로 만들어드려요."),
]


def _build_landing_html():
    """본문 HTML(단계 패널/준비자료) 생성. 개행·들여쓰기 없이 조립한다."""
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

    return (
        '<div id="abp-landing">'
        '<div class="abp-process-row">'
        '<div class="abp-process-panel">'
        '<div class="abp-process-ribbon">이렇게 진행돼요!</div>'
        '<div class="abp-steps">' + steps_html + "</div></div>"
        '<div class="abp-materials">'
        '<div class="abp-materials-tab">준비 자료</div>' + _SVG_DOCUMENTS +
        '<p class="abp-materials-title">PDF, DOCX 등</p>'
        '<p class="abp-materials-desc">사업보고서, 계획서, 평가서, 참고자료 등 다양한 형식 가능!</p>'
        "</div></div></div>"
    )


def render_landing():
    """랜딩 화면 렌더링. 반환값: "start" | "example" | None"""
    import streamlit as st

    st.markdown(LANDING_STYLE, unsafe_allow_html=True)

    # 히어로: 원본 이미지 그대로 표시 (종횡비 유지, 왜곡/크롭 없음)
    if HERO_IMAGE_PATH.exists():
        st.image(str(HERO_IMAGE_PATH), use_container_width=True)
    else:  # 이미지 누락 시에도 기능은 진행 가능하도록 최소 안내만
        st.info("히어로 이미지(public/reference/"
                "annual-business-plan-hero-reference.png)를 찾을 수 없습니다.")

    # 본문 HTML: 모든 연속 공백을 정규화해 단일 HTML 블록으로 전달
    # (빈 줄/들여쓰기로 인한 마크다운 코드블록 오해석 → 코드 노출 방지)
    body_html = " ".join(_build_landing_html().split())
    st.markdown(body_html, unsafe_allow_html=True)

    # 실제 클릭 가능한 버튼 (CSS 로 레퍼런스 스타일 적용)
    st.markdown('<div class="abp-btn-anchor"></div>', unsafe_allow_html=True)
    start_col, example_col = st.columns([1, 1], gap="medium")

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
