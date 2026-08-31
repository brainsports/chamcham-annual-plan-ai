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

import base64
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
    max-width: 1240px !important;
    border: none !important;
    box-shadow: none !important;
    padding: 18px 32px 24px !important;
}
#abp-landing {
    width: 100%; max-width: 1176px; margin: 0 auto;
    font-family: 'NanumGothic', 'Nanum Gothic', sans-serif;
}
#abp-landing * { box-sizing: border-box; }

/* 히어로 원본 이미지: 콘텐츠 폭의 약 78%, 중앙 정렬, 종횡비 유지 */
.abp-hero-image {
    display: block; width: 78%; max-width: 920px; height: auto;
    margin: 0 auto; object-fit: contain;
}

/* ---------------- 이렇게 진행돼요! 패널 ---------------- */
.abp-process-row {
    display: flex; justify-content: center; align-items: stretch;
    gap: 20px; margin-top: 28px;
}
.abp-process-panel {
    position: relative; flex: 1 1 auto; min-width: 0;
    background: #FDFBF3; border: 1.5px dashed #C9A86A; border-radius: 20px;
    padding: 44px 20px 24px;
}
.abp-process-ribbon {
    position: absolute; top: -19px; left: 50%; transform: translateX(-50%);
    background: #FBE88A; border: 1.5px solid #6F6547; border-radius: 2px;
    padding: 7px 27px; font-size: 18px; font-weight: 800; color: #2F2F2F; white-space: nowrap;
}
.abp-process-ribbon::before, .abp-process-ribbon::after {
    content: ""; position: absolute; top: 4px; width: 20px; height: 26px;
    background: #D9C25E; border: 1.5px solid #6F6547; z-index: -1;
}
.abp-process-ribbon::before { left: -18px; clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%, 40% 50%); }
.abp-process-ribbon::after { right: -18px; clip-path: polygon(0 0, 100% 0, 60% 50%, 100% 100%, 0 100%); }

.abp-steps { display: flex; align-items: flex-start; justify-content: space-between; gap: 6px; }
.abp-step { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; text-align: center; }
.abp-step-icon { position: relative; width: 82px; height: 82px; display: flex; align-items: center; justify-content: center; }
.abp-step-icon svg { width: 82px; height: 82px; }
.abp-step-badge {
    position: absolute; top: -7px; left: -9px; width: 34px; height: 34px;
    border-radius: 50%; border: 1.5px solid #FFFFFF; color: #FFFFFF;
    font-size: 15px; font-weight: 800; display: flex; align-items: center;
    justify-content: center; z-index: 1;
}
.abp-step-title { margin: 12px 0 0; font-size: 21px; font-weight: 800; color: #2F2F2F; }
.abp-step-desc { margin: 6px 0 0; font-size: 15px; line-height: 1.42; color: #454545; word-break: keep-all; }
.abp-arrow { flex-shrink: 0; align-self: center; margin-top: 29px; font-size: 29px; color: #555555; line-height: 1; }

/* ---------------- 준비 자료 박스 ---------------- */
.abp-materials {
    position: relative; width: 198px; flex-shrink: 0;
    display: flex; flex-direction: column; justify-content: center;
    background: #F3F9E9; border: 1.5px solid #91C86B; border-radius: 12px;
    padding: 38px 14px 20px; text-align: center;
}
.abp-materials-tab {
    position: absolute; top: -16px; left: 50%; transform: translateX(-50%);
    background: #EDE8CF; border: 1.5px solid #6F6547; border-radius: 2px;
    padding: 5px 22px; font-size: 17px; font-weight: 800; color: #2F2F2F; white-space: nowrap;
}
.abp-materials-icon { width: 74px; margin: 0 auto; display: block; }
.abp-materials-title { margin: 7px 0 0; font-size: 18px; font-weight: 800; color: #2F2F2F; }
.abp-materials-desc { margin: 7px 0 0; font-size: 14px; line-height: 1.4; font-weight: 600; color: #3F4C37; word-break: keep-all; }

/* ---------------- 하단 버튼 (실제 st.button) ---------------- */
.abp-btn-anchor { height: 0; margin: 0; }
div[data-testid="stHorizontalBlock"] {
    display: flex !important; justify-content: center !important;
    align-items: stretch !important; gap: 44px !important; margin-top: 18px;
}
div[data-testid="stHorizontalBlock"] > div:first-child {
    flex: 0 1 400px !important; width: 400px !important; max-width: 400px;
}
div[data-testid="stHorizontalBlock"] > div:last-child {
    flex: 0 1 320px !important; width: 320px !important; max-width: 320px;
}
div[data-testid="stHorizontalBlock"] button {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 2px; border-radius: 14px; cursor: pointer; width: 100%;
    font-family: 'NanumGothic', 'Nanum Gothic', sans-serif;
    transition: transform .15s ease;
    height: auto; min-height: 86px;
}
div[data-testid="stHorizontalBlock"] button:hover { transform: translateY(-2px); }
div[data-testid="stHorizontalBlock"] > div:first-child button {
    background: #20B8B6; border: 2px solid #3A3A3A;
    box-shadow: 0 4px 0 rgba(58,58,58,.20);
    color: #FFFFFF; font-size: 25px; font-weight: 800;
    padding: 12px 24px;
}
div[data-testid="stHorizontalBlock"] > div:first-child button:hover {
    background: #2CC4C4; border: 3px solid #3A3A3A; color: #FFFFFF;
}
div[data-testid="stHorizontalBlock"] > div:first-child button::after {
    content: "지금 바로 시작해요!"; display: block; font-size: 14px; font-weight: 600;
    color: rgba(255,255,255,.94); margin-top: 2px;
}
div[data-testid="stHorizontalBlock"] > div:last-child button {
    background: #FFFFFF; border: 2px solid #3A3A3A;
    box-shadow: 0 4px 0 rgba(58,58,58,.12);
    color: #2F2F2F; font-size: 22px; font-weight: 800;
    padding: 12px 22px;
}
div[data-testid="stHorizontalBlock"] > div:last-child button:hover {
    background: #FFFFFF; border: 3px solid #3A3A3A; color: #3A3A3A;
}
div[data-testid="stHorizontalBlock"] > div:last-child button::after {
    content: "작성 예시를 확인해보세요."; display: block; font-size: 13px; font-weight: 600;
    color: #555555; margin-top: 2px;
}

/* ---------------- 하단 안내 문구 ---------------- */
.abp-notice {
    margin-top: 22px; text-align: center; font-size: 16px; font-weight: 700;
    color: #4A4A4A; word-break: keep-all;
}

/* ---------------- 반응형 (PC 우선, 모바일 종횡비 유지) ---------------- */
@media (max-width: 1280px) {
    .main .block-container { padding-left: 24px !important; padding-right: 24px !important; }
    .abp-process-panel { padding-left: 16px; padding-right: 16px; }
}
@media (max-width: 1024px) {
    .abp-hero-image { width: 86%; }
    .abp-process-row { flex-direction: column; align-items: center; gap: 44px; }
    .abp-process-panel { width: 100%; }
    .abp-steps { flex-wrap: wrap; gap: 24px 14px; }
    .abp-step { flex: 1 1 40%; }
    .abp-arrow { display: none; }
    .abp-materials { width: 100%; max-width: 490px; min-height: 210px; }
    div[data-testid="stHorizontalBlock"] { flex-direction: column; align-items: center; gap: 20px !important; }
    div[data-testid="stHorizontalBlock"] > div:first-child,
    div[data-testid="stHorizontalBlock"] > div:last-child {
        flex: 0 0 auto !important; width: 100% !important; max-width: 490px;
    }
}
@media (max-width: 640px) {
    .main .block-container { padding: 12px 16px 20px !important; }
    .abp-hero-image { width: 100%; }
    .abp-process-ribbon { padding: 8px 20px; font-size: 17px; }
    .abp-process-panel { padding: 44px 18px 30px; }
    .abp-step { flex: 1 1 100%; }
    .abp-step-title { font-size: 21px; }
    .abp-step-desc { font-size: 15px; }
    .abp-notice { font-size: 16px; }
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


def _build_landing_html(hero_src):
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
        '<img class="abp-hero-image" src="' + hero_src + '" '
        'alt="AI와 함께 쉽고 빠르게 연간사업계획서 작성">'
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

    # 히어로: 원본을 data URI로 넣어 본문과 동일한 중앙 컨테이너 안에 배치한다.
    if HERO_IMAGE_PATH.exists():
        hero_src = "data:image/png;base64," + base64.b64encode(
            HERO_IMAGE_PATH.read_bytes()
        ).decode("ascii")
    else:  # 이미지 누락 시에도 기능은 진행 가능하도록 최소 안내만
        st.info("히어로 이미지(public/reference/"
                "annual-business-plan-hero-reference.png)를 찾을 수 없습니다.")
        hero_src = ""

    # 본문 HTML: 모든 연속 공백을 정규화해 단일 HTML 블록으로 전달
    # (빈 줄/들여쓰기로 인한 마크다운 코드블록 오해석 → 코드 노출 방지)
    body_html = " ".join(_build_landing_html(hero_src).split())
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
