# -*- coding: utf-8 -*-
"""
연간사업계획서 작업페이지 (4단계 진행 UI)

단계 흐름: UPLOAD(1 자료 업로드) → ANALYZING(2 분석하기) → EDITING(3 수정하기)
           → COMPLETED(4 완성/다운로드)

- 기존 AI 분석(get_partitioned_analysis) / 편집(data_editor) / PART1~4 Word
  다운로드 로직은 그대로 유지한다.
- 분석이 끝나도 자동으로 3단계로 넘어가지 않고, 사용자가
  '내용 확인 및 수정하기 →' 버튼을 눌러야 3단계에 진입한다.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import altair as alt
import logging
import os

# ============================================================
# [필수 수정 1] st.set_page_config는 반드시 최상단에 위치해야 합니다.
# ============================================================
st.set_page_config(page_title="AI 사업계획 도우미", page_icon="🤝", layout="wide")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 내부 메뉴 표시 여부 스위치 (운영: 숨김, 개발/디버그: 표시)
def is_internal_enabled():
    """환경변수 SHOW_INTERNAL=1 또는 URL 쿼리 ?debug=1 일 때 True"""
    env_on = os.getenv("SHOW_INTERNAL", "0").strip() == "1"
    try:
        qp = dict(st.query_params)
        debug_on = str(qp.get("debug", "0")) in ["1", "true", "True"]
    except Exception:
        debug_on = False
    return env_on or debug_on


SHOW_INTERNAL = is_internal_enabled()

from utils import (get_gemini_analysis, get_default_data, read_uploaded_file,
                   process_multiple_files, extract_file_summaries,
                   summaries_to_compact_text, get_partitioned_analysis,
                   load_guideline_rules, count_chars_no_space,
                   bucket_programs_by_month, apply_guidelines_to_analysis,
                   get_missing_categories, generate_part2_for_categories,
                   generate_part1, generate_part3, generate_part4,
                   ensure_feedback_table_complete)
from doc_utils import (generate_part1_report, generate_part2_report,
                       generate_monthly_report,
                       generate_monthly_program_report,
                       generate_part4_full_report, generate_full_report)
from landing_page import render_landing

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

try:
    plt.rc('font', family='NanumGothic')
except:
    pass

# ============================================================
# [필수 수정 2] APP_STYLE: 레퍼런스(annual-plan-step-ui-reference.png) 맞춤
# 연녹색 톤 / 카드형 2단 레이아웃 / 4단계 진행표시
# ============================================================
APP_STYLE = """
<style>
/* ===== 컬러 시스템 (레퍼런스 연녹색 테마) =====
   Primary: #1E6B3C / #2E7D4F, 연녹색 배경: #EAF4EC, 배경: #F5F7F5 */

/* 전체 앱 배경 */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #FBFCFB !important;
}

/* Streamlit 기본 UI 숨김 */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {visibility: hidden;}

/* 사이드바 완전 숨김 */
[data-testid="stSidebar"] {
    display: none !important;
}

/* 레이아웃 컨테이너: 카드 없는 넓은 캔버스 (카드는 본문에서 개별 렌더) */
.main .block-container {
    max-width: 1450px !important;
    margin: 0 auto !important;
    padding: 20px 20px 28px !important;
    background: transparent;
    border: none;
    box-shadow: none;
}

/* ===== 공통 카드 ===== */
.abp-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
.abp-card h3, .abp-card h4 { margin: 0; }

/* 작업 단계의 큰 왼쪽 카드 */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E7E3 !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(31, 41, 55, .035);
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 24px 28px !important;
}
.abp-analysis-section { padding: 2px 0 0; margin-bottom: 18px; }

/* ===== 4단계 진행표시 (스텝 인디케이터) ===== */
.abp-steps {
    display: flex; align-items: flex-start; justify-content: space-between;
    background: #FFFFFF; border: 1px solid #DDE3DF; border-radius: 10px;
    padding: 24px 74px 18px; margin-bottom: 24px;
    box-shadow: 0 2px 7px rgba(31, 41, 55, .035);
}
.abp-step {
    flex: 1 1 0; min-width: 0; display: flex; align-items: flex-start;
    gap: 14px; position: relative; padding-bottom: 14px;
}
.abp-step-num {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 800; color: #334155;
    background: #EEF1F0; border: none;
}
.abp-step.done .abp-step-num,
.abp-step.active .abp-step-num { background: #3E9653; color: #FFFFFF; }
.abp-step-txt { min-width: 0; }
.abp-step-title {
    font-size: 17px; font-weight: 800; color: #263244; line-height: 1.3;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.abp-step.done .abp-step-title { color: #263244; }
.abp-step.active .abp-step-title { color: #26783A; }
.abp-step-desc {
    font-size: 13px; color: #536071; margin-top: 4px; line-height: 1.4;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.abp-step.active .abp-step-desc { color: #455264; }
.abp-step.active::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0;
    height: 3px; border-radius: 2px; background: #2F8B45;
}
.abp-step-link {
    flex: 0 0 84px; align-self: center; margin: 5px 14px 15px;
    color: #59A568; font-size: 24px; font-weight: 500; line-height: 1;
    text-align: center;
}
.abp-step-link.pending { color: #C7CFCB; }
.abp-step-link.pending::before { content: "┈┈┈"; letter-spacing: 1px; }
.abp-step-link.done-link::before { content: "→"; }

/* ===== 헤더 (제목 + 우측 버튼) ===== */
.abp-header {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; margin-bottom: 22px; flex-wrap: wrap;
}
.abp-header h1 {
    font-size: 38px; line-height: 1.2; font-weight: 900;
    color: #17202D; margin: 0; letter-spacing: -.8px;
}
.abp-header h1 .abp-ai { color: #2F8B45; }
.abp-header h1 .abp-sparkle { color: #F3B93F; font-size: 32px; }
.abp-header p { font-size: 16px; color: #526070; margin: 12px 0 0; }
.abp-header-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.abp-header-btn {
    display: inline-flex; align-items: center; gap: 6px;
    background: #FFFFFF; border: 1px solid #D6DDE2; border-radius: 8px;
    padding: 13px 20px; font-size: 15px; font-weight: 700; color: #344054;
    cursor: pointer; transition: background .15s ease;
}
.abp-header-btn:hover { background: #F3F6F4; }

/* ===== 왼쪽 메인 영역 공통 ===== */
.abp-main-title { font-size: 24px; font-weight: 850; color: #1B2430; margin: 0 0 8px; }
.abp-main-desc { font-size: 15px; color: #596574; margin: 0 0 22px; line-height: 1.55; }

/* ===== 업로드 드롭존 안내 ===== */
.abp-upload-guide {
    background: #FAFBFA; border: 2px dashed #A7C9B4; border-radius: 12px;
    padding: 26px 20px; text-align: center; margin-bottom: 16px;
}
.abp-upload-guide .abp-ug-icon { font-size: 40px; line-height: 1; }
.abp-upload-guide .abp-ug-title {
    font-size: 16px; font-weight: 700; color: #374151; margin: 10px 0 4px;
}
.abp-upload-guide .abp-ug-desc { font-size: 13px; color: #6B7280; margin: 0; }
.abp-upload-guide .abp-ug-formats { font-size: 12px; color: #9CA3AF; margin-top: 8px; }

/* ===== 업로드한 자료 카드 ===== */
.abp-files-head {
    display: flex; align-items: center; justify-content: space-between;
    margin: 4px 0 10px;
}
.abp-files-head h4 { font-size: 15px; font-weight: 700; color: #1F2937; margin: 0; }
.abp-badge {
    display: inline-block; background: #E4F1E7; color: #2E7D4F;
    border-radius: 999px; padding: 3px 12px; font-size: 13px; font-weight: 700;
}
.abp-file-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 10px;
}
.abp-file {
    display: flex; align-items: center; gap: 10px;
    background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px;
    padding: 10px 12px; min-width: 0;
}
.abp-file-icon {
    width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800; color: #FFFFFF;
}
.abp-file-icon.pdf { background: #E05252; }
.abp-file-icon.docx { background: #4184F3; }
.abp-file-icon.txt { background: #6B7280; }
.abp-file-icon.csv { background: #7CB342; }
.abp-file-meta { min-width: 0; }
.abp-file-name {
    font-size: 13px; font-weight: 700; color: #374151;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.abp-file-size { font-size: 12px; color: #9CA3AF; margin-top: 2px; }

/* ===== 분석 진행 화면 ===== */
.abp-analyze-head { display: flex; align-items: center; gap: 16px; margin-bottom: 18px; }
.abp-analyze-emoji { font-size: 44px; line-height: 1; }
.abp-analyze-title { font-size: 19px; font-weight: 800; color: #1F2937; margin: 0; }
.abp-analyze-desc { font-size: 14px; color: #6B7280; margin: 4px 0 0; }

.abp-task-list {
    background: #F7F8F7; border: 1px solid #E9EDEA; border-radius: 12px;
    padding: 8px 18px; margin-bottom: 16px;
}
.abp-task {
    display: flex; align-items: center; justify-content: space-between;
    gap: 12px; padding: 11px 0; border-bottom: 1px solid #E9EDEA;
}
.abp-task:last-child { border-bottom: none; }
.abp-task-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.abp-task-label { font-size: 15px; color: #374151; white-space: nowrap;
                  overflow: hidden; text-overflow: ellipsis; }
.abp-task-state { font-size: 13px; font-weight: 700; flex-shrink: 0; }
.abp-task-state.done { color: #2E7D4F; }
.abp-task-state.doing { color: #2E7D4F; }
.abp-task-state.wait { color: #9CA3AF; }
.abp-check-circle {
    width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 800; color: #FFFFFF; background: #2E7D4F;
}
.abp-check-wait {
    width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
    border: 2px solid #D5DBD7; background: transparent;
}
.abp-spinner {
    width: 20px; height: 20px; border-radius: 50%; flex-shrink: 0;
    border: 3px solid #DCE9E1; border-top-color: #2E7D4F;
    animation: abp-spin 0.9s linear infinite;
}
@keyframes abp-spin { to { transform: rotate(360deg); } }

/* 진행률 바 */
.abp-progress-wrap { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
.abp-progress-track {
    flex: 1 1 auto; height: 8px; border-radius: 999px;
    background: #E9EDEA; overflow: hidden;
}
.abp-progress-bar {
    height: 100%; border-radius: 999px;
    background: #2E7D4F; transition: width .4s ease;
}
.abp-progress-label { font-size: 13px; font-weight: 700; color: #2E7D4F; white-space: nowrap; }

/* 분석 완료 배너 */
.abp-done-banner {
    display: flex; align-items: center; gap: 14px;
    background: #EAF4EC; border-radius: 12px; padding: 18px 20px;
    margin-bottom: 16px;
}
.abp-done-icon {
    width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
    background: #2E7D4F; color: #FFFFFF; font-size: 20px;
    display: flex; align-items: center; justify-content: center;
}
.abp-done-title { font-size: 16px; font-weight: 800; color: #1F2937; margin: 0; }
.abp-done-desc { font-size: 13px; color: #4B5563; margin: 3px 0 0; }

/* 연녹색 안내 박스 */
.abp-info-box {
    display: flex; align-items: flex-start; gap: 10px;
    background: #F7FAF8; border: 1px solid #E3EDE6; border-radius: 10px;
    padding: 12px 14px; font-size: 13px; color: #4B5563; line-height: 1.5;
}
.abp-info-box.green { background: #EAF4EC; border-color: #CDE5D4; color: #2E7D4F; font-weight: 600; }

/* ===== 완성(4단계) 화면 ===== */
.abp-complete-hero { text-align: center; padding: 10px 0 6px; }
.abp-complete-icon {
    width: 72px; height: 72px; border-radius: 50%; margin: 0 auto 16px;
    background: #EAF4EC; color: #2E7D4F; font-size: 34px;
    display: flex; align-items: center; justify-content: center;
}
.abp-complete-title { font-size: 22px; font-weight: 800; color: #1F2937; margin: 0; }
.abp-complete-desc { font-size: 14px; color: #6B7280; margin: 8px 0 0; }
.abp-dl-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }

/* ===== 오른쪽 도움말 영역 ===== */
.abp-help-card {
    background: #FCFEFB; border: 1px solid #D5E5D7; border-radius: 12px;
    padding: 24px 22px 20px; min-height: 100%;
    box-shadow: 0 2px 8px rgba(31, 41, 55, .025);
}
.abp-help-title {
    font-size: 18px; font-weight: 850; color: #26783A; margin: 0 0 8px;
    display: flex; align-items: center; gap: 8px;
}
.abp-help-sub { font-size: 13px; color: #647080; margin: 0 0 16px; }
.abp-help-sep { border: none; border-top: 1px solid #E1EAE2; margin: 0 0 18px; }
.abp-qa {
    display: flex; gap: 12px; margin-bottom: 18px; padding-bottom: 18px;
    border-bottom: 1px solid #E1EAE2;
}
.abp-qa-icon {
    width: 40px; height: 40px; border-radius: 50%; flex-shrink: 0;
    background: #FFFFFF; border: 1px solid #DDE5E0; font-size: 18px;
    display: flex; align-items: center; justify-content: center;
}
.abp-qa-q { font-size: 16px; font-weight: 800; color: #26783A; margin: 0 0 7px; }
.abp-qa-a { font-size: 13px; color: #485566; line-height: 1.6; margin: 0 0 5px;
            display: flex; gap: 6px; }
.abp-qa-a::before { content: "✓"; color: #2E7D4F; font-weight: 800; flex-shrink: 0; }
.abp-help-secure {
    background: #F0F7EF; border: 1px solid #D5E5D4; border-radius: 10px; padding: 14px 16px;
    display: flex; align-items: flex-start; gap: 10px;
    font-size: 13px; color: #2E7D4F; font-weight: 600; line-height: 1.5;
}
.abp-help-secure .abp-secure-title { font-weight: 800; margin: 0 0 2px; }
.abp-help-secure p { margin: 0; }

/* ===== 버튼 (Streamlit 버튼 오버라이드 - 연녹색 톤) ===== */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
    border: 1px solid #D1D5DB;
}
.stButton > button[kind="primary"] {
    background: #1E6B3C !important;
    border: none !important;
    color: #FFFFFF !important;
    font-size: 16px !important;
    padding: 0.75rem 1.6rem !important;
    box-shadow: 0 2px 8px rgba(30, 107, 60, 0.25);
}
.stButton > button[kind="primary"]:hover {
    background: #2E7D4F !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(30, 107, 60, 0.32);
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    color: #374151 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #F3F6F4 !important;
    border-color: #2E7D4F !important;
    color: #2E7D4F !important;
}

/* 파일 업로더: 단일 대형 카드 + 한글 선택 버튼 */
[data-testid="stFileUploader"] {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
}
[data-testid="stFileUploaderDropzone"] {
    min-height: 205px;
    background: #FBFDFB !important;
    border: 2px dashed #8DBA98 !important;
    border-radius: 12px !important;
    padding: 34px 32px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    font-size: 0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: "참고자료를 끌어다 놓거나 선택하세요";
    display: block; font-size: 17px; font-weight: 800; color: #273342;
    margin-bottom: 8px;
}
[data-testid="stFileUploaderDropzoneInstructions"]::after {
    content: "여러 파일을 한 번에 업로드할 수 있어요  ·  PDF, DOCX, TXT, CSV";
    display: block; font-size: 13px; color: #687585;
}
[data-testid="stFileUploaderDropzoneInstructions"] small { display: none !important; }
[data-testid="stFileUploader"] button {
    min-width: 132px; min-height: 44px; font-size: 0 !important;
    color: #FFFFFF !important; background: #2F8B45 !important;
    border: 1px solid #26783A !important; border-radius: 8px !important;
}
[data-testid="stFileUploader"] button * { font-size: 0 !important; }
[data-testid="stFileUploader"] button::after {
    content: "파일 선택하기"; font-size: 15px; font-weight: 800; color: #FFFFFF;
}

/* 성공/정보 메시지 스타일 */
.stSuccess {
    background-color: #EAF4EC !important;
    border: 1px solid #CDE5D4 !important;
    border-radius: 10px !important;
}

.stInfo, .stWarning {
    border-radius: 10px !important;
}

/* 탭 스타일 - 연녹색 언더라인 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
    border-bottom: 2px solid #E5E7EB;
    padding: 0;
    border-radius: 0;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 0;
    padding: 12px 24px;
    color: #6B7280;
    background: transparent;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
}

.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #2E7D4F !important;
    font-weight: 600;
    border-bottom: 3px solid #2E7D4F !important;
}

/* 텍스트 스타일 */
p, span, div {
    color: #374151;
}

h1, h2, h3, h4, h5, h6 {
    color: #1F2937 !important;
}

/* Expander 스타일 */
.streamlit-expanderHeader {
    border-radius: 10px !important;
    background: #F9FAFB !important;
    border: 1px solid #E5E7EB !important;
}

/* 테이블 스타일 (참참 공문서 스타일) */
.stDataFrame, [data-testid="stDataFrame"] {
    border: 1px solid #D1D5DB !important;
    border-radius: 4px !important;
}

/* 테이블 헤더 - 연한 연녹색 */
.stDataFrame thead tr th {
    background-color: #EAF4EC !important;
    color: #374151 !important;
    font-weight: 600 !important;
    border: 1px solid #D1D5DB !important;
}

/* 테이블 셀 테두리 */
.stDataFrame tbody tr td {
    border: 1px solid #D1D5DB !important;
}

/* 텍스트 에어리어 스타일 */
.stTextArea textarea {
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
}

.stTextArea textarea:focus {
    border-color: #2E7D4F !important;
    box-shadow: 0 0 0 2px rgba(46, 125, 79, 0.2) !important;
}

/* 숫자 입력 스타일 */
.stNumberInput input {
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
}

.stNumberInput input:focus {
    border-color: #2E7D4F !important;
}

/* 라디오 버튼 스타일 */
.stRadio > div {
    gap: 0.5rem;
}

/* 다운로드 버튼 스타일 */
.stDownloadButton > button {
    background: #1E6B3C !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
}

.stDownloadButton > button:hover {
    background: #2E7D4F !important;
}

/* ===== 반응형 ===== */
@media (max-width: 1024px) {
    .main .block-container { padding-left: 16px !important; padding-right: 16px !important; }
    .abp-steps { flex-wrap: wrap; padding: 18px 22px 12px; }
    .abp-step { flex: 1 1 42%; padding-bottom: 10px; }
    .abp-step-link { display: none; }
    .abp-step.active::after { left: 0; right: 0; }
    .abp-header h1 { font-size: 30px; }
}
@media (max-width: 640px) {
    .main .block-container { padding: 12px 12px 22px !important; }
    .abp-step { flex: 1 1 100%; }
    .abp-step-title, .abp-step-desc { white-space: normal; }
    .abp-file-grid { grid-template-columns: 1fr; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { padding: 20px 16px !important; }
    [data-testid="stFileUploaderDropzone"] { padding: 24px 16px !important; }
}
</style>
"""
st.markdown(APP_STYLE, unsafe_allow_html=True)

if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

if 'guideline_rules' not in st.session_state:
    st.session_state.guideline_rules = load_guideline_rules()

if 'month_bucket' not in st.session_state:
    st.session_state.month_bucket = None

if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

# ============================================================
# [4단계 진행 상태] UPLOAD → ANALYZING → EDITING → COMPLETED
# - 단계는 버튼 클릭으로만 전환한다 (분석 완료 후 자동 진입 금지)
# ============================================================
if 'work_step' not in st.session_state:
    st.session_state.work_step = 'UPLOAD'

# 업로드한 파일 메타(이름/용량) - 분석 화면의 "업로드한 자료" 카드용
if 'uploaded_meta' not in st.session_state:
    st.session_state.uploaded_meta = []

# 분석 진행 단계(0~4)와 진행률 - ANALYZING 화면 표시용
if 'analyze_stage' not in st.session_state:
    st.session_state.analyze_stage = 0
if 'analyze_progress' not in st.session_state:
    st.session_state.analyze_progress = 0

# 랜딩 페이지 상태 (새로고침 시 기본값 True → 랜딩부터 시작)
if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

MAX_FILES = 30
MAX_TOTAL_SIZE_MB = 200

if 'guideline_logs' not in st.session_state:
    st.session_state.guideline_logs = []


# ============================================================
# 4단계 진행표시 컴포넌트 (레퍼런스: annual-plan-step-ui-reference.png)
# ============================================================
STEPS_DEF = [
    ("1", "자료 업로드", "참고자료 업로드"),
    ("2", "분석하기", "AI가 자료를 분석합니다"),
    ("3", "수정하기", "내용을 확인하고 수정합니다"),
    ("4", "완성 / 다운로드", "계획서를 저장하고 다운로드"),
]


def get_step_index(step: str) -> int:
    return {'UPLOAD': 1, 'ANALYZING': 2, 'EDITING': 3, 'COMPLETED': 4}.get(step, 1)


def render_step_indicator(current_step: str):
    """상단 4단계 진행상태 표시 (완료=초록, 활성=초록+언더바, 대기=회색)"""
    cur = get_step_index(current_step)
    parts = []
    for i, (num, title, desc) in enumerate(STEPS_DEF, start=1):
        if i > 1:
            link_cls = "abp-step-link"
            if i <= cur:
                link_cls += " done-link"
            else:
                link_cls += " pending"
            parts.append(f'<div class="{link_cls}"></div>')
        cls = "abp-step"
        if i < cur:
            cls += " done"
        elif i == cur:
            cls += " active"
        parts.append(
            f'<div class="{cls}">'
            f'<div class="abp-step-num">{num}</div>'
            f'<div class="abp-step-txt">'
            f'<div class="abp-step-title">{title}</div>'
            f'<div class="abp-step-desc">{desc}</div>'
            f'</div></div>')
    st.markdown(
        '<div class="abp-steps">' + "".join(parts) + '</div>',
        unsafe_allow_html=True)


def render_header():
    """페이지 헤더 (제목 + 홈 버튼)"""
    st.markdown(
        """
        <div class="abp-header">
            <div>
                <h1><span class="abp-ai">AI</span> 연간사업계획서 만들기
                    <span class="abp-sparkle">✦</span></h1>
                <p>참고자료를 업로드하고 AI가 분석하여 연간사업계획서 작성을 도와드립니다.</p>
            </div>
            <div class="abp-header-actions">
                <button class="abp-header-btn" onclick="null">📖 사용 가이드</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True)


# ============================================================
# 오른쪽 도움말 영역 (단계별 내용 변경)
# ============================================================
HELP_CONTENT = {
    'UPLOAD': {
        'title': '도움말',
        'sub': '지금은 <b>1단계: 자료 업로드</b>예요',
        'qas': [
            ('💡', '어떤 자료를 올리면 좋을까요?',
             ['연간사업계획서 · 프로그램 계획서/보고서',
              '사업 결과보고서 · 평가서',
              '기타 운영 관련 문서 (PDF, DOCX 등)']),
            ('🤖', 'AI는 어떤 일을 하나요?',
             ['업로드한 자료의 핵심 내용을 정리해요',
              '목표·사업내용·예산을 계획서 양식에 맞게 구조화해요',
              '연간사업계획서 초안을 자동으로 작성해드려요']),
            ('✏️', '직접 수정할 수 있나요?',
             ['AI가 만든 초안을 확인한 후 원하는 부분을 직접 수정할 수 있어요',
              '기관 상황에 맞게 자유롭게 다듬어 보세요']),
        ],
        'secure': True,
        'tip': '여러 개의 자료를 올릴수록 더 정확하게 분석돼요!',
    },
    'ANALYZING': {
        'title': '도움말',
        'sub': '지금은 <b>2단계: 분석하기</b>예요',
        'qas': [
            ('🤖', 'AI가 무엇을 분석하나요?',
             ['사업의 필요성 및 운영 방향',
              '프로그램별 목적·목표와 핵심 내용',
              '사업평가·환류 내용과 월별 계획']),
            ('⏳', '얼마나 걸리나요?',
             ['자료의 양과 복잡도에 따라 1~5분 정도 걸려요',
              '화면을 닫지 말고 잠시만 기다려 주세요']),
            ('✏️', '분석이 끝나면 어떻게 되나요?',
             ['완료 안내와 함께 확인 버튼이 나타나요',
              '버튼을 누르면 초안을 확인하고 수정할 수 있어요']),
        ],
        'secure': True,
        'tip': None,
    },
    'EDITING': {
        'title': '도움말',
        'sub': '지금은 <b>3단계: 수정하기</b>예요',
        'qas': [
            ('✏️', '어떻게 수정하나요?',
             ['PART 1~4 탭에서 표와 입력창을 직접 수정할 수 있어요',
              '칸이 좁으면 더블클릭하면 큰 창에서 수정할 수 있어요',
              '"문서 형태로 미리보기"로 완성 문서를 확인해 보세요']),
            ('🔍', '누락된 영역이 있나요?',
             ['왼쪽 "보완 분석"에서 해당 자료만 추가 업로드하면 돼요',
              '누락 영역만 다시 분석해 PART 1~4에 반영해요']),
            ('⬇️', '언제 다운로드할 수 있나요?',
             ['검토가 끝나면 "계획서 작성 완료하기"를 눌러주세요',
              '4단계에서 PART 1~4 Word 파일을 내려받을 수 있어요']),
        ],
        'secure': False,
        'tip': None,
    },
    'COMPLETED': {
        'title': '도움말',
        'sub': '지금은 <b>4단계: 완성 / 다운로드</b>예요',
        'qas': [
            ('⬇️', '어떻게 다운로드하나요?',
             ['PART 1~4별로 Word(.docx) 파일로 내려받을 수 있어요',
              '버튼을 누르면 각 파트 파일이 저장돼요']),
            ('🔄', '다시 수정하고 싶다면?',
             ['"다시 수정하기" 버튼으로 3단계로 돌아갈 수 있어요',
              '수정 후 다시 완료 처리하면 돼요']),
            ('🏠', '새로 작성하고 싶다면?',
             ['"새로 시작하기"로 처음부터 다시 작성할 수 있어요']),
        ],
        'secure': False,
        'tip': None,
    },
}


def render_right_help(step: str):
    """오른쪽 도움말 카드 (현재 단계에 맞는 안내)"""
    c = HELP_CONTENT.get(step, HELP_CONTENT['UPLOAD'])
    qas_html = ""
    for icon, q, answers in c['qas']:
        answers_html = "".join(f'<p class="abp-qa-a">{a}</p>' for a in answers)
        qas_html += (
            f'<div class="abp-qa">'
            f'<div class="abp-qa-icon">{icon}</div>'
            f'<div><p class="abp-qa-q">{q}</p>{answers_html}</div></div>')
    tip_html = ""
    if c.get('tip'):
        tip_html = (
            '<div class="abp-help-secure" style="margin-bottom:16px;">'
            f'<p>{c["tip"]}</p></div>')
    secure_html = ""
    if c.get('secure'):
        secure_html = (
            '<div class="abp-help-secure">'
            '<span>🛡️</span><div><p class="abp-secure-title">안전하게 보호돼요</p>'
            '<p>업로드된 모든 자료는 안전하게 보호되며, 분석 후 자동으로 삭제됩니다.'
            '</p></div></div>')
    # 빈 줄 없이 조립 (마크다운 코드블록 오해석 방지)
    body = (
        f'<div class="abp-help-card"><p class="abp-help-title">💡 {c["title"]}</p>'
        f'<p class="abp-help-sub">{c["sub"]}</p><hr class="abp-help-sep">'
        f'{qas_html}{tip_html}{secure_html}</div>')
    st.markdown(" ".join(body.split()), unsafe_allow_html=True)


# ============================================================
# 분석 진행 화면 (2단계 ANALYZING)
# ============================================================
ANALYZE_TASKS = [
    "사업의 필요성 및 운영 방향 분석",
    "프로그램 목적·목표 분석",
    "사업평가 및 환류내용 분석",
    "연간사업계획서 초안 작성",
]


def _fmt_size(nbytes) -> str:
    try:
        n = float(nbytes or 0)
    except Exception:
        return ""
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f}MB"
    if n >= 1024:
        return f"{n / 1024:.0f}KB"
    return f"{n:.0f}B"


def _file_icon_cls(name: str) -> str:
    ext = (name.rsplit('.', 1)[-1] or '').lower()
    return ext if ext in ('pdf', 'docx', 'txt', 'csv') else 'docx'


def render_uploaded_files_card():
    """분석 화면 하단 "업로드한 자료" 카드"""
    meta = st.session_state.get('uploaded_meta') or []
    if not meta:
        return
    cards = ""
    for name, size in meta:
        cards += (
            f'<div class="abp-file">'
            f'<div class="abp-file-icon {_file_icon_cls(name)}">'
            f'{_file_icon_cls(name).upper()}</div>'
            f'<div class="abp-file-meta">'
            f'<div class="abp-file-name">{name}</div>'
            f'<div class="abp-file-size">{_fmt_size(size)}</div>'
            f'</div></div>')
    st.markdown(
        '<div class="abp-card">'
        '<div class="abp-files-head"><h4>업로드한 자료</h4>'
        f'<span class="abp-badge">{len(meta)}개</span></div>'
        f'<div class="abp-file-grid">{cards}</div></div>',
        unsafe_allow_html=True)


def render_analyzing_screen():
    """2단계 분석 진행/완료 화면 (실제 진행상태와 연결)"""
    done_all = st.session_state.analysis_data is not None
    stage = 4 if done_all else st.session_state.get('analyze_stage', 0)
    progress = 100 if done_all else st.session_state.get('analyze_progress', 0)

    tasks_html = ""
    for i, label in enumerate(ANALYZE_TASKS):
        if i < stage:
            state, state_cls = "완료", "done"
            mark = '<div class="abp-check-circle">✓</div>'
        elif i == stage and not done_all:
            state, state_cls = "진행 중", "doing"
            mark = '<div class="abp-spinner"></div>'
        else:
            state, state_cls = "대기", "wait"
            mark = '<div class="abp-check-wait"></div>'
        tasks_html += (
            f'<div class="abp-task">'
            f'<div class="abp-task-left">{mark}'
            f'<span class="abp-task-label">{label}</span></div>'
            f'<span class="abp-task-state {state_cls}">{state}</span></div>')

    if done_all:
        head = (
            '<div class="abp-analyze-head">'
            '<div class="abp-analyze-emoji">🎉</div>'
            '<div><p class="abp-analyze-title">분석이 완료되었습니다!</p>'
            '<p class="abp-analyze-desc">이제 내용을 확인하고 수정해 보세요.</p></div></div>')
        done_banner = (
            '<div class="abp-done-banner">'
            '<div class="abp-done-icon">✓</div>'
            '<div><p class="abp-done-title">분석이 완료되었습니다!</p>'
            f'<p class="abp-done-desc">첨부자료 {len(st.session_state.get("uploaded_meta") or [])}개를 분석하여 '
            '연간사업계획서 초안을 만들었습니다.</p></div></div>')
        body = head + done_banner + (
            f'<div class="abp-task-list">{tasks_html}</div>'
            '<div class="abp-progress-wrap"><div class="abp-progress-track">'
            '<div class="abp-progress-bar" style="width:100%"></div></div>'
            '<span class="abp-progress-label">분석 진행률 100%</span></div>')
        st.markdown(
            " ".join(('<div class="abp-analysis-section">' + body + '</div>').split()),
            unsafe_allow_html=True)

        # ── 반드시 버튼 클릭으로만 3단계 진입 ──
        if st.button("내용 확인 및 수정하기 →", type="primary",
                     use_container_width=True, key="abp_goto_edit"):
            st.session_state.work_step = 'EDITING'
            st.rerun()
    else:
        head = (
            '<div class="abp-analyze-head">'
            '<div class="abp-analyze-emoji">🤖</div>'
            '<div><p class="abp-analyze-title">AI가 자료를 분석하고 있어요</p>'
            '<p class="abp-analyze-desc">잠시만 기다려 주세요. 금방 끝나요!</p></div></div>')
        note = (
            '<div class="abp-info-box" style="margin-top:16px;"><span>🛡️</span>'
            '<span>자료의 양과 복잡도에 따라 분석 시간이 달라질 수 있습니다. '
            '잠시만 기다려 주세요.</span></div>')
        body = head + (
            f'<div class="abp-task-list">{tasks_html}</div>'
            '<div class="abp-progress-wrap"><div class="abp-progress-track">'
            f'<div class="abp-progress-bar" style="width:{progress}%"></div></div>'
            f'<span class="abp-progress-label">분석 진행률 {progress}%</span></div>'
            + note)
        st.markdown(
            " ".join(('<div class="abp-analysis-section">' + body + '</div>').split()),
            unsafe_allow_html=True)


# ============================================================
# 파일 업로드 처리 함수 (1단계 UPLOAD - 왼쪽 메인 영역)
# ============================================================
def render_file_upload_section():
    """1단계: 파일 업로드 UI 렌더링 (드래그앤드롭/다중 업로드)"""
    uploaded_files = st.file_uploader("파일 선택하기",
                                      type=['pdf', 'docx', 'txt', 'csv'],
                                      accept_multiple_files=True,
                                      label_visibility="collapsed",
                                      key="main_uploader")

    if uploaded_files:
        total_size_bytes = sum(uf.size for uf in uploaded_files)
        total_size_mb = total_size_bytes / (1024 * 1024)

        st.success(f"✓ {len(uploaded_files)}개 파일이 준비되었습니다")

        upload_valid = True
        if len(uploaded_files) > MAX_FILES:
            st.warning(f"최대 {MAX_FILES}개")
            upload_valid = False
        if total_size_mb > MAX_TOTAL_SIZE_MB:
            st.warning(f"최대 {MAX_TOTAL_SIZE_MB}MB")
            upload_valid = False

        file_summaries = extract_file_summaries(uploaded_files)
        compact_text = summaries_to_compact_text(file_summaries)

        if not file_summaries:
            st.warning("파일에서 텍스트를 읽지 못했어요. 스캔 이미지 PDF는 지원되지 않으니 Word(.docx)로 변환 후 업로드해 주세요.")
            upload_valid = False

        if SHOW_INTERNAL:
            with st.expander("디버그"):
                st.caption(f"요약: {len(compact_text)}자")

        month_bucket = bucket_programs_by_month(file_summaries)

        return uploaded_files, upload_valid, compact_text, month_bucket, file_summaries

    return None, False, "", {}, []


def render_upload_step():
    """1단계 화면: 업로드 UI + 분석 시작 버튼 + 예시 데이터"""
    st.markdown('<p class="abp-main-title">참고자료를 업로드해 주세요</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="abp-main-desc">기존 사업보고서 · 프로그램 계획서 · '
                '결과보고서 등을 올려주시면 AI가 분석해 연간사업계획서 초안을 '
                '만들어드려요.</p>', unsafe_allow_html=True)

    (uploaded_files, upload_valid, compact_text, month_bucket,
     file_summaries) = render_file_upload_section()

    if uploaded_files and upload_valid:
        if st.button("✨ 분석 시작하기", type="primary",
                     use_container_width=True, key="abp_analyze_start"):
            # 업로드 메타 저장 (분석 화면 "업로드한 자료" 카드용)
            st.session_state.uploaded_meta = [(uf.name, uf.size)
                                              for uf in uploaded_files]
            st.session_state.analyze_stage = 0
            st.session_state.analyze_progress = 0
            st.session_state.month_bucket = month_bucket
            st.session_state.is_analyzing = True
            # 2단계(ANALYZING)로 전환 → 분석은 이 화면에서 자동 진행
            st.session_state.work_step = 'ANALYZING'
            st.rerun()

    render_sample_button()

    if SHOW_INTERNAL:
        with st.expander("작성지침 (JSON)"):
            if st.session_state.guideline_rules:
                st.json(st.session_state.guideline_rules)


def run_analysis():
    """2단계 화면 안에서 실제 AI 분석 수행 (기존 로직 그대로)"""
    # 업로더에서 고른 파일은 런에서 유지되므로 다시 읽어 사용한다
    uploaded_files = st.file_uploader("PDF, DOCX 파일 지원",
                                      type=['pdf', 'docx', 'txt', 'csv'],
                                      accept_multiple_files=True,
                                      label_visibility="collapsed",
                                      key="main_uploader")
    if not uploaded_files:
        st.session_state.is_analyzing = False
        st.session_state.work_step = 'UPLOAD'
        st.rerun()
        return

    file_summaries = extract_file_summaries(uploaded_files)
    compact_text = summaries_to_compact_text(file_summaries)
    month_bucket = st.session_state.get('month_bucket') or bucket_programs_by_month(
        file_summaries)

    def update_progress(msg):
        """실제 분석 진행상태 → UI 단계/진행률 연결"""
        if "Part 1" in msg:
            st.session_state.analyze_stage = 0
            st.session_state.analyze_progress = 10
        elif "Part 2" in msg:
            st.session_state.analyze_stage = 1
            st.session_state.analyze_progress = 35
        elif "Part 3" in msg:
            st.session_state.analyze_stage = 2
            st.session_state.analyze_progress = 60
        elif "Part 4" in msg:
            st.session_state.analyze_stage = 3
            st.session_state.analyze_progress = 85
        elif "지침" in msg:
            st.session_state.analyze_stage = 3
            st.session_state.analyze_progress = 95

    result = get_partitioned_analysis(
        compact_text,
        progress_callback=update_progress,
        month_bucket=month_bucket,
        guideline_rules=st.session_state.guideline_rules,
        file_summaries=file_summaries)

    st.session_state.analyze_stage = 4
    st.session_state.analyze_progress = 100
    st.session_state.is_analyzing = False

    if result:
        failed_parts = result.pop("_failed_parts", [])
        guideline_logs = result.pop("_guideline_logs", [])
        st.session_state.analysis_data = result
        st.session_state.guideline_logs = guideline_logs
        if failed_parts:
            st.session_state['_partial_fail'] = True
        else:
            st.session_state['_partial_fail'] = False
    # 완료 후에도 ANALYZING 화면 유지 → 버튼 클릭으로만 3단계 진입
    st.rerun()


def render_sample_button():
    """예시 데이터 버튼 렌더링 (기존 로직 유지)"""
    st.markdown("---")
    st.caption("처음이라면 예시데이터로 체험해 보세요")
    if st.button("📋 예시 데이터로 시작하기", use_container_width=True,
                 key="abp_sample_btn"):
        raw_data = get_default_data()
        rules = load_guideline_rules()
        adjusted_data, adjustment_logs = apply_guidelines_to_analysis(
            raw_data, rules)
        st.session_state.analysis_data = adjusted_data
        st.session_state.guideline_rules = rules
        for log in adjustment_logs:
            logger.info(log)
        st.session_state.uploaded_meta = [("예시 데이터", 0)]
        st.session_state.analyze_stage = 4
        st.session_state.analyze_progress = 100
        st.session_state.work_step = 'ANALYZING'
        st.rerun()


# ============================================================
# 3단계: 수정하기 (기존 PART1~4 편집 로직 유지)
# ============================================================
def render_editing_step():
    """AI가 생성한 내용 확인/수정 (기존 편집 기능 그대로)"""
    data = st.session_state.analysis_data

    if 'part1_general' not in data:
        data['part1_general'] = {}
    if 'part2_programs' not in data:
        data['part2_programs'] = {}
    if 'part3_monthly_plan' not in data:
        data['part3_monthly_plan'] = {}
    if 'part4_monthly_plan' not in data:
        data['part4_monthly_plan'] = {}
    if 'part4_budget_evaluation' not in data:
        data['part4_budget_evaluation'] = {
            "budget_table": [],
            "feedback_summary": []
        }

    st.markdown('<p class="abp-main-title">내용을 확인하고 수정해 보세요</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="abp-main-desc">AI가 만든 초안을 PART 1~4 탭에서 '
                '직접 수정할 수 있어요. 수정한 내용은 자동으로 저장돼요.</p>',
                unsafe_allow_html=True)

    # ── 누락 카테고리 감지 및 보완 업로드 UI (기존 로직 유지) ──
    part2_now = data.get('part2_programs', {})
    missing_cats = get_missing_categories(part2_now)

    if missing_cats:
        missing_str = ", ".join(f"**{c}**" for c in missing_cats)
        st.warning(
            f"⚠️ 누락된 영역이 있습니다\n\n"
            f"다음 대분류의 정보가 부족합니다:\n{missing_str}\n\n"
            f"해당 영역 관련 자료를 추가로 업로드하면 누락 영역만 보완 분석합니다."
        )

        supplement_files = st.file_uploader(
            "추가 자료 업로드 (PDF, DOCX 등)",
            type=['pdf', 'docx', 'txt', 'csv'],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="supplement_uploader"
        )

        if supplement_files:
            st.caption(f"✓ {len(supplement_files)}개 파일 선택됨")
            for sf in supplement_files:
                st.caption(f"• {sf.name}")

            if st.button("🔍 누락 영역만 보완 분석",
                         type="primary",
                         use_container_width=True,
                         key="supplement_analyze_btn"):
                with st.spinner("누락 영역 보완 분석 중... (Part 1~4 모두 반영)"):
                    supp_summaries = extract_file_summaries(supplement_files)
                    supp_compact = summaries_to_compact_text(supp_summaries)
                    guideline_rules = st.session_state.get('guideline_rules', {})

                    any_updated = False

                    # ── Part 2 보완 ──
                    new_cat_data = generate_part2_for_categories(
                        supp_compact, missing_cats
                    )
                    if new_cat_data:
                        for cat in missing_cats:
                            if cat in new_cat_data:
                                data['part2_programs'][cat] = new_cat_data[cat]
                        any_updated = True

                    # ── Part 1 보완: feedback_table 누락 행 채우기 ──
                    new_p1 = generate_part1(supp_compact, detected_categories=missing_cats)
                    if new_p1:
                        new_fb = new_p1.get('feedback_table', [])
                        existing_fb = data.get('part1_general', {}).get('feedback_table', [])
                        existing_by_area = {row.get('area', ''): row for row in existing_fb if isinstance(row, dict)}
                        for row in new_fb:
                            area = row.get('area', '')
                            if area in missing_cats and isinstance(row, dict):
                                existing_by_area[area] = row
                        merged_order = ["보호", "교육", "문화", "정서지원", "지역사회연계"]
                        merged_fb = [existing_by_area[a] for a in merged_order if a in existing_by_area]
                        if 'part1_general' not in data:
                            data['part1_general'] = {}
                        data['part1_general']['feedback_table'] = ensure_feedback_table_complete(merged_fb)
                        any_updated = True

                    # ── Part 3 보완: 상반기 월별계획에 누락 카테고리 프로그램 추가 ──
                    new_p3 = generate_part3(supp_compact, detected_categories=missing_cats)
                    if new_p3 and isinstance(new_p3, dict):
                        existing_p3 = data.get('part3_monthly_plan', {})
                        for month in [f"{m}월" for m in range(1, 7)]:
                            new_progs = new_p3.get(month, [])
                            if new_progs:
                                existing_progs = existing_p3.get(month, [])
                                existing_p3[month] = existing_progs + new_progs
                        data['part3_monthly_plan'] = existing_p3
                        any_updated = True

                    # ── Part 4 보완: 하반기 월별계획에 누락 카테고리 프로그램 추가 ──
                    new_p4 = generate_part4(supp_compact, detected_categories=missing_cats,
                                            guideline_rules=guideline_rules)
                    if new_p4 and isinstance(new_p4, dict):
                        existing_p4 = data.get('part4_monthly_plan', {})
                        # generate_part4 returns {"monthly_plan": {...}, ...}
                        # but data['part4_monthly_plan'] stores months directly
                        new_monthly = new_p4.get('monthly_plan', new_p4)
                        for month in [f"{m}월" for m in range(7, 13)]:
                            new_progs = new_monthly.get(month, [])
                            if new_progs:
                                existing_p4[month] = existing_p4.get(month, []) + new_progs
                        data['part4_monthly_plan'] = existing_p4
                        any_updated = True

                    if any_updated:
                        st.session_state.analysis_data = data
                        st.success(
                            f"✅ 보완 완료! ({', '.join(missing_cats)} 영역이 Part 1~4에 모두 반영됨)"
                        )
                        st.rerun()
                    else:
                        st.error(
                            "보완 분석에 실패했습니다. 파일 내용을 확인하고 다시 시도해 주세요."
                        )
    else:
        st.markdown(
            '<div class="abp-info-box green"><span>✓</span>'
            '<span>5개 영역 모두 분석 완료</span></div>',
            unsafe_allow_html=True)

    # 중앙 칼럼 내 탭 (기존 PART 1~4 편집 UI 그대로)
    tab1, tab2, tab3, tab4 = st.tabs([
        "PART 1: 총괄/기획", "PART 2: 세부사업", "PART 3: 상반기(1~6월)",
        "PART 4: 하반기(7~12월)"
    ])

    with tab1:
        st.header("PART 1: 총괄 및 기획")
        view_mode_p1 = st.toggle("📄 문서 형태로 미리보기", key="view_mode_p1")

        part1 = data.get('part1_general', {})

        p1_rules = st.session_state.guideline_rules.get(
            'part1', {}) if st.session_state.guideline_rules else {}

        def show_char_count(text, field_name, rules_dict):
            rule = rules_dict.get(field_name, {})
            max_chars = rule.get('max_chars_no_space', 0)
            current = count_chars_no_space(text)
            if max_chars > 0:
                color = "red" if current > max_chars else "green"
                st.caption(
                    f":{color}[공백 제외 글자수: {current} / {max_chars}자]")
            else:
                st.caption(f"공백 제외 글자수: {current}자")

        with st.expander("1. 사업의 필요성", expanded=True):
            st.subheader("1) 이용아동의 욕구 및 문제점")
            need_1 = st.text_area("1) 이용아동의 욕구 및 문제점 (상세 서술)",
                                  value=part1.get('need_1_user_desire',
                                                  ''),
                                  height=300,
                                  key="p1_need_1")
            show_char_count(need_1, 'need_1_user_desire', p1_rules)
            data['part1_general']['need_1_user_desire'] = need_1

            st.subheader("2) 지역 환경적 특성")

            need_2_1 = st.text_area("(1) 지역적 특성 (상세 서술)",
                                    value=part1.get(
                                        'need_2_1_regional', ''),
                                    height=200,
                                    key="p1_need_2_1")
            show_char_count(need_2_1, 'need_2_1_regional', p1_rules)
            data['part1_general']['need_2_1_regional'] = need_2_1

            need_2_2 = st.text_area("(2) 주변환경 (상세 서술)",
                                    value=part1.get(
                                        'need_2_2_environment', ''),
                                    height=200,
                                    key="p1_need_2_2")
            show_char_count(need_2_2, 'need_2_2_environment', p1_rules)
            data['part1_general']['need_2_2_environment'] = need_2_2

            need_2_3 = st.text_area("(3) 교육적 특성 (상세 서술)",
                                    value=part1.get(
                                        'need_2_3_educational', ''),
                                    height=200,
                                    key="p1_need_2_3")
            show_char_count(need_2_3, 'need_2_3_educational', p1_rules)
            data['part1_general']['need_2_3_educational'] = need_2_3

        with st.expander("2. 전년도 사업평가 및 환류계획", expanded=True):
            st.subheader("1) 차년도 사업 환류 계획")
            feedback_data = part1.get('feedback_table', [])
            feedback_df = pd.DataFrame(
                feedback_data) if feedback_data else pd.DataFrame(
                    columns=['area', 'problem', 'improvement'])

            if not feedback_df.empty and 'area' in feedback_df.columns:
                feedback_df = feedback_df.rename(columns={
                    'area': '영역',
                    'problem': '문제점',
                    'improvement': '개선방안'
                })
            else:
                feedback_df = pd.DataFrame(columns=['영역', '문제점', '개선방안'])

            target_order = ["보호", "교육", "문화", "정서지원", "지역사회연계"]
            if not feedback_df.empty and '영역' in feedback_df.columns:
                feedback_df['영역'] = pd.Categorical(feedback_df['영역'],
                                                   categories=target_order,
                                                   ordered=True)
                feedback_df = feedback_df.sort_values('영역').reset_index(
                    drop=True)

            if view_mode_p1:
                for idx, row in feedback_df.iterrows():
                    st.markdown(f"### {row.get('영역', '')}")
                    st.markdown(f"**문제점:**\n{row.get('문제점', '')}")
                    st.markdown(f"**개선방안:**\n{row.get('개선방안', '')}")
                    st.markdown("---")
            else:
                st.caption("💡 팁: 칸이 좁아 보이면 더블클릭하여 전체 내용을 확인/수정하세요.")
                edited_feedback = st.data_editor(
                    feedback_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "영역":
                        st.column_config.TextColumn("영역", width=100),
                        "문제점":
                        st.column_config.TextColumn("문제점", width="large"),
                        "개선방안":
                        st.column_config.TextColumn("개선방안", width="large"),
                    },
                    key="p1_feedback_tbl")

                data['part1_general'][
                    'feedback_table'] = edited_feedback.rename(
                        columns={
                            '영역': 'area',
                            '문제점': 'problem',
                            '개선방안': 'improvement'
                        }).to_dict('records')

            st.subheader("2) 총평")
            total_review_data = part1.get('total_review_table', [])
            total_review_df = pd.DataFrame(
                total_review_data) if total_review_data else pd.DataFrame(
                    columns=['category', 'content'])

            if not total_review_df.empty and 'category' in total_review_df.columns:
                total_review_df = total_review_df.rename(columns={
                    'category': '영역',
                    'content': '내용'
                })
            else:
                total_review_df = pd.DataFrame(columns=['영역', '내용'])

            target_review_order = [
                "운영평가", "아동평가", "프로그램평가", "후원활동측면", "환류방안"
            ]
            if not total_review_df.empty and '영역' in total_review_df.columns:
                total_review_df['영역'] = pd.Categorical(
                    total_review_df['영역'],
                    categories=target_review_order,
                    ordered=True)
                total_review_df = total_review_df.sort_values(
                    '영역').reset_index(drop=True)

            if view_mode_p1:
                for idx, row in total_review_df.iterrows():
                    st.markdown(f"### {row.get('영역', '')}")
                    st.markdown(row.get('내용', ''))
                    st.markdown("---")
            else:
                st.caption("💡 총평 내용은 더블클릭하면 팝업창에서 편하게 긴 글을 수정할 수 있습니다.")
                edited_review = st.data_editor(
                    total_review_df,
                    num_rows="fixed",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "영역":
                        st.column_config.TextColumn("영역",
                                                    width=150,
                                                    disabled=True),
                        "내용":
                        st.column_config.TextColumn("내용", width=700),
                    },
                    key="p1_review_tbl")

                data['part1_general'][
                    'total_review_table'] = edited_review.rename(
                        columns={
                            '영역': 'category',
                            '내용': 'content'
                        }).to_dict('records')

        with st.expander("3. 만족도조사", expanded=True):
            satisfaction_survey = part1.get('satisfaction_survey', {})

            if satisfaction_survey and satisfaction_survey.get(
                    'survey_data'):
                st.subheader("응답자 설정")
                col_resp, col_btn = st.columns([2, 1])
                with col_resp:
                    total_respondents = st.number_input(
                        "총 응답 인원 (명)",
                        min_value=1,
                        value=satisfaction_survey.get(
                            'total_respondents', 30),
                        key="p1_total_resp")
                    data['part1_general']['satisfaction_survey'][
                        'total_respondents'] = total_respondents

                survey_data = satisfaction_survey.get('survey_data', [])
                survey_df = pd.DataFrame(survey_data)

                st.subheader("문항별 응답 분포")
                st.caption("각 문항의 척도별 응답 인원수 (수정 가능)")

                edited_survey = st.data_editor(
                    survey_df,
                    num_rows="fixed",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "문항":
                        st.column_config.TextColumn("문항", width="large"),
                        "5점":
                        st.column_config.NumberColumn("5점(명)",
                                                      min_value=0,
                                                      step=1),
                        "4점":
                        st.column_config.NumberColumn("4점(명)",
                                                      min_value=0,
                                                      step=1),
                        "3점":
                        st.column_config.NumberColumn("3점(명)",
                                                      min_value=0,
                                                      step=1),
                        "2점":
                        st.column_config.NumberColumn("2점(명)",
                                                      min_value=0,
                                                      step=1),
                        "1점":
                        st.column_config.NumberColumn("1점(명)",
                                                      min_value=0,
                                                      step=1),
                    },
                    key="p1_survey_tbl")

                data['part1_general']['satisfaction_survey'][
                    'survey_data'] = edited_survey.to_dict('records')

                def calculate_weighted_avg(row):
                    total = row['5점'] + row['4점'] + row['3점'] + row[
                        '2점'] + row['1점']
                    if total == 0:
                        return 0
                    return (5 * row['5점'] + 4 * row['4점'] + 3 * row['3점'] +
                            2 * row['2점'] + 1 * row['1점']) / total

                edited_survey['평균점수'] = edited_survey.apply(
                    calculate_weighted_avg, axis=1)
                overall_avg = edited_survey['평균점수'].mean()
                st.metric("전체 평균 만족도", f"{overall_avg:.2f}점 (5점 만점)")

                st.markdown("---")
                st.subheader("만족도 분포 차트")

                chart_data = []
                for _, row in edited_survey.iterrows():
                    question = row['문항'][:20] + '...' if len(
                        row['문항']) > 20 else row['문항']
                    for scale in ['5점', '4점', '3점', '2점', '1점']:
                        chart_data.append({
                            '문항': question,
                            '척도': scale,
                            '인원수': row[scale]
                        })
                chart_df = pd.DataFrame(chart_data)

                color_map = [
                    '#4184F3', '#7CB342', '#FF8F00', '#FF5722', '#AC4ABC'
                ]
                scale_order = ['5점', '4점', '3점', '2점', '1점']

                col_chart1, col_chart2 = st.columns([1, 1])

                with col_chart1:
                    st.caption("항목별 평균 점수")
                    avg_data = edited_survey[['문항', '평균점수']].copy()
                    avg_data['문항_short'] = avg_data['문항'].apply(
                        lambda x: x[:20] + '...' if len(x) > 20 else x)

                    avg_bar = alt.Chart(avg_data).mark_bar(
                        color='#4184F3').encode(
                            y=alt.Y('문항_short:N', sort=None, title='문항'),
                            x=alt.X('평균점수:Q',
                                    scale=alt.Scale(domain=[0, 5]),
                                    title='점수'),
                            tooltip=[
                                '문항:N',
                                alt.Tooltip('평균점수:Q', format='.2f')
                            ]).properties(height=400)

                    avg_text = avg_bar.mark_text(
                        align='left',
                        baseline='middle',
                        dx=3,
                        color='black').encode(
                            text=alt.Text('평균점수:Q', format='.2f'))

                    st.altair_chart(avg_bar + avg_text,
                                    use_container_width=True)

                with col_chart2:
                    st.caption("응답 분포 (인원수)")
                    stacked_chart = alt.Chart(chart_df).mark_bar().encode(
                        y=alt.Y('문항:N', sort=None, title='문항'),
                        x=alt.X('인원수:Q', title='인원(명)', stack='zero'),
                        color=alt.Color('척도:N',
                                        scale=alt.Scale(domain=scale_order,
                                                        range=color_map),
                                        legend=alt.Legend(title='척도',
                                                          orient='right')),
                        order=alt.Order('척도:N', sort='descending'),
                        tooltip=['문항:N', '척도:N',
                                 '인원수:Q']).properties(height=400)
                    st.altair_chart(stacked_chart,
                                    use_container_width=True)

                st.markdown("---")

                st.subheader("주관식 문항 분석")
                subjective_q = st.text_input("주관식 문항",
                                             value=satisfaction_survey.get(
                                                 'subjective_question',
                                                 '기타 건의사항 및 개선 의견'),
                                             key="p1_subj_q")
                data['part1_general']['satisfaction_survey'][
                    'subjective_question'] = subjective_q

                subjective_analysis = st.text_area(
                    "주관식 문항 요약 및 분석 (500자 이상)",
                    value=satisfaction_survey.get('subjective_analysis',
                                                  ''),
                    height=300,
                    key="p1_subj_analysis")
                data['part1_general']['satisfaction_survey'][
                    'subjective_analysis'] = subjective_analysis

                st.markdown("---")

                st.subheader("종합 분석 및 제언")
                overall_suggestion = st.text_area(
                    "종합 분석 및 제언 (500자 이상)",
                    value=satisfaction_survey.get('overall_suggestion',
                                                  ''),
                    height=300,
                    key="p1_overall_suggestion")
                data['part1_general']['satisfaction_survey'][
                    'overall_suggestion'] = overall_suggestion
            else:
                st.info("만족도 조사 데이터가 없습니다.")
                if 'satisfaction_survey' not in data['part1_general']:
                    data['part1_general']['satisfaction_survey'] = {
                        'total_respondents': 30,
                        'survey_data': [],
                        'subjective_question': '',
                        'subjective_analysis': '',
                        'overall_suggestion': ''
                    }

        with st.expander("4. 사업목적", expanded=True):
            purpose = st.text_area("사업목적을 작성하세요",
                                   value=part1.get('purpose_text', ''),
                                   height=150,
                                   key="p1_purpose_txt")
            show_char_count(purpose, 'purpose_text', p1_rules)
            data['part1_general']['purpose_text'] = purpose

        with st.expander("5. 사업목표", expanded=True):
            goals = st.text_area("사업목표를 작성하세요",
                                 value=part1.get('goals_text', ''),
                                 height=150,
                                 key="p1_goals_txt")
            show_char_count(goals, 'goals_text', p1_rules)
            data['part1_general']['goals_text'] = goals

        # [3단계] PART별 다운로드 버튼은 노출하지 않는다 (4단계에서만 노출)

    with tab2:
        st.header("PART 2: 세부 사업 계획")

        preview_mode_p2 = st.toggle("📄 문서 형태로 미리보기", key="preview_mode_p2")

        categories = ["보호", "교육", "문화", "정서지원", "지역사회연계"]

        selected_category = st.radio("영역 선택",
                                     categories,
                                     horizontal=True,
                                     key="p2_category_select")

        part2 = data.get('part2_programs', {})

        if selected_category not in part2:
            part2[selected_category] = {
                "detail_table": [],
                "eval_table": []
            }
            data['part2_programs'] = part2

        category_data = part2.get(selected_category, {
            "detail_table": [],
            "eval_table": []
        })

        st.subheader(f"📋 {selected_category} - 세부사업내용")

        detail_data = category_data.get('detail_table', [])
        detail_df = pd.DataFrame(
            detail_data) if detail_data else pd.DataFrame(columns=[
                'sub_area', 'program_name', 'expected_effect', 'target',
                'count', 'cycle', 'content'
            ])

        if not detail_df.empty and 'sub_area' in detail_df.columns:
            detail_df = detail_df.rename(
                columns={
                    'sub_area': '세부영역',
                    'program_name': '프로그램명',
                    'expected_effect': '기대효과',
                    'target': '대상',
                    'count': '인원',
                    'cycle': '주기',
                    'content': '계획내용'
                })
        else:
            detail_df = pd.DataFrame(columns=[
                '세부영역', '프로그램명', '기대효과', '대상', '인원', '주기', '계획내용'
            ])

        if preview_mode_p2:
            for _, row in detail_df.iterrows():
                st.markdown(
                    f"#### 📄 {row.get('세부영역', '')} > {row.get('프로그램명', '')}"
                )
                exp_effect = row.get('기대효과', '') or '기대효과 내용이 없습니다.'
                plan_content = row.get('계획내용', '') or '계획내용이 없습니다.'
                st.markdown(f"**🎯 기대효과:** {exp_effect}")
                st.markdown(f"**📝 계획내용:** {plan_content}")
                st.markdown(
                    f"**대상**: {row.get('대상', '')} | **인원**: {row.get('인원', '')} | **주기**: {row.get('주기', '')}"
                )
                st.markdown("---")
        else:
            st.caption("💡 팁: 칸이 좁아 보이면 더블클릭하여 전체 내용을 확인/수정하세요.")
            edited_detail = st.data_editor(
                detail_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "세부영역":
                    st.column_config.TextColumn("세부영역", width="small"),
                    "프로그램명":
                    st.column_config.TextColumn("프로그램명", width="medium"),
                    "기대효과":
                    st.column_config.TextColumn("기대효과", width="large"),
                    "대상":
                    st.column_config.TextColumn("대상", width="small"),
                    "인원":
                    st.column_config.TextColumn("인원", width="small"),
                    "주기":
                    st.column_config.TextColumn("주기", width="small"),
                    "계획내용":
                    st.column_config.TextColumn("계획내용", width="large"),
                },
                key=f"p2_detail_{selected_category}")

            data['part2_programs'][selected_category][
                'detail_table'] = edited_detail.rename(
                    columns={
                        '세부영역': 'sub_area',
                        '프로그램명': 'program_name',
                        '기대효과': 'expected_effect',
                        '대상': 'target',
                        '인원': 'count',
                        '주기': 'cycle',
                        '계획내용': 'content'
                    }).to_dict('records')

        st.subheader(f"📊 {selected_category} - 평가계획")

        eval_data = category_data.get('eval_table', [])

        # 기존 스키마 호환성: eval_tool/eval_timing → main_plan/eval_method 매핑
        if eval_data:
            for item in eval_data:
                if 'eval_tool' in item and 'main_plan' not in item:
                    item['main_plan'] = item.pop('eval_tool', '')
                if 'eval_timing' in item and 'eval_method' not in item:
                    item['eval_method'] = item.pop('eval_timing', '')
                if 'sub_area' not in item:
                    item['sub_area'] = ''
                if 'expected_effect' not in item:
                    prog_name = item.get('program_name', '')
                    for detail in detail_data:
                        if detail.get('program_name') == prog_name:
                            item['expected_effect'] = detail.get(
                                'expected_effect', '')
                            item['sub_area'] = detail.get('sub_area', '')
                            break
                    if 'expected_effect' not in item:
                        item['expected_effect'] = ''

        eval_df = pd.DataFrame(eval_data) if eval_data else pd.DataFrame(
            columns=[
                'sub_area', 'program_name', 'expected_effect', 'main_plan',
                'eval_method'
            ])

        if not eval_df.empty and 'program_name' in eval_df.columns:
            eval_df = eval_df.rename(
                columns={
                    'sub_area': '세부영역',
                    'program_name': '프로그램명',
                    'expected_effect': '기대효과',
                    'main_plan': '평가계획',
                    'eval_method': '평가방법'
                })
        else:
            eval_df = pd.DataFrame(
                columns=['세부영역', '프로그램명', '기대효과', '평가계획', '평가방법'])

        if preview_mode_p2:
            for _, row in eval_df.iterrows():
                st.markdown(
                    f"#### 📊 {row.get('세부영역', '')} > {row.get('프로그램명', '')}"
                )
                exp_effect = row.get('기대효과', '') or '기대효과 내용이 없습니다.'
                st.markdown(f"**🎯 기대효과:** {exp_effect}")
                st.markdown(f"**📋 평가계획:** {row.get('평가계획', '')}")
                st.markdown(f"**📏 평가방법:** {row.get('평가방법', '')}")
                st.markdown("---")
        else:
            edited_eval = st.data_editor(
                eval_df,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "세부영역":
                    st.column_config.TextColumn("세부영역", width="small"),
                    "프로그램명":
                    st.column_config.TextColumn("프로그램명", width="medium"),
                    "기대효과":
                    st.column_config.TextColumn("기대효과", width="large"),
                    "평가계획":
                    st.column_config.TextColumn("평가계획", width="medium"),
                    "평가방법":
                    st.column_config.TextColumn("평가방법", width="medium"),
                },
                key=f"p2_eval_{selected_category}")

            data['part2_programs'][selected_category][
                'eval_table'] = edited_eval.rename(
                    columns={
                        '세부영역': 'sub_area',
                        '프로그램명': 'program_name',
                        '기대효과': 'expected_effect',
                        '평가계획': 'main_plan',
                        '평가방법': 'eval_method'
                    }).to_dict('records')

        # [3단계] PART별 다운로드 버튼은 노출하지 않는다 (4단계에서만 노출)

    with tab3:
        st.title("PART 3: 상반기 월별 사업계획 (1월~6월)")

        is_preview_p3 = st.toggle("📄 문서 형태로 미리보기", key="toggle_p3")

        monthly_plan = data.get('part3_monthly_plan', {})
        h1_months = ["1월", "2월", "3월", "4월", "5월", "6월"]

        for month in h1_months:
            st.markdown(f"## {month} 사업계획서")

            month_programs = monthly_plan.get(month, [])
            month_df = pd.DataFrame(
                month_programs) if month_programs else pd.DataFrame(
                    columns=[
                        'big_category', 'mid_category', 'program_name',
                        'target', 'staff', 'content'
                    ])

            if not month_df.empty and 'big_category' in month_df.columns:
                month_df = month_df.rename(
                    columns={
                        'big_category': '대분류',
                        'mid_category': '중분류',
                        'program_name': '프로그램명',
                        'target': '참여자',
                        'staff': '수행인력',
                        'content': '사업내용'
                    })
            else:
                month_df = pd.DataFrame(
                    columns=['대분류', '중분류', '프로그램명', '참여자', '수행인력', '사업내용'])

            if is_preview_p3:
                if not month_df.empty:
                    st.table(month_df)
                else:
                    st.info("등록된 사업이 없습니다.")
            else:
                st.caption("💡 팁: 칸이 좁아 보이면 더블클릭하여 전체 내용을 확인/수정하세요.")
                edited_month = st.data_editor(
                    month_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "대분류":
                        st.column_config.SelectboxColumn(
                            "대분류",
                            options=["보호", "교육", "문화", "정서지원", "지역사회연계"],
                            width="small"),
                        "중분류":
                        st.column_config.TextColumn("중분류", width="small"),
                        "프로그램명":
                        st.column_config.TextColumn("프로그램명",
                                                    width="medium"),
                        "참여자":
                        st.column_config.TextColumn("참여자", width="small"),
                        "수행인력":
                        st.column_config.TextColumn("수행인력", width="small"),
                        "사업내용":
                        st.column_config.TextColumn("사업내용", width="large"),
                    },
                    key=f"month_editor_h1_{month}")

                data['part3_monthly_plan'][month] = edited_month.rename(
                    columns={
                        '대분류': 'big_category',
                        '중분류': 'mid_category',
                        '프로그램명': 'program_name',
                        '참여자': 'target',
                        '수행인력': 'staff',
                        '사업내용': 'content'
                    }).to_dict('records')

            st.markdown("---")

        # [3단계] PART별 다운로드 버튼은 노출하지 않는다 (4단계에서만 노출)

    with tab4:
        st.title("PART 4: 하반기 월별 사업계획 (7월~12월)")

        is_preview_p4 = st.toggle("📄 문서 형태로 미리보기", key="toggle_p4")

        monthly_plan = data.get('part4_monthly_plan', {})
        h2_months = ["7월", "8월", "9월", "10월", "11월", "12월"]

        for month in h2_months:
            st.markdown(f"## {month} 사업계획서")

            month_programs = monthly_plan.get(month, [])
            month_df = pd.DataFrame(
                month_programs) if month_programs else pd.DataFrame(
                    columns=[
                        'big_category', 'mid_category', 'program_name',
                        'target', 'staff', 'content'
                    ])

            if not month_df.empty and 'big_category' in month_df.columns:
                month_df = month_df.rename(
                    columns={
                        'big_category': '대분류',
                        'mid_category': '중분류',
                        'program_name': '프로그램명',
                        'target': '참여자',
                        'staff': '수행인력',
                        'content': '사업내용'
                    })
            else:
                month_df = pd.DataFrame(
                    columns=['대분류', '중분류', '프로그램명', '참여자', '수행인력', '사업내용'])

            if is_preview_p4:
                if not month_df.empty:
                    st.table(month_df)
                else:
                    st.info("등록된 사업이 없습니다.")
            else:
                st.caption("💡 팁: 칸이 좁아 보이면 더블클릭하여 전체 내용을 확인/수정하세요.")
                edited_month = st.data_editor(
                    month_df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "대분류":
                        st.column_config.SelectboxColumn(
                            "대분류",
                            options=["보호", "교육", "문화", "정서지원", "지역사회연계"],
                            width="small"),
                        "중분류":
                        st.column_config.TextColumn("중분류", width="small"),
                        "프로그램명":
                        st.column_config.TextColumn("프로그램명",
                                                    width="medium"),
                        "참여자":
                        st.column_config.TextColumn("참여자", width="small"),
                        "수행인력":
                        st.column_config.TextColumn("수행인력", width="small"),
                        "사업내용":
                        st.column_config.TextColumn("사업내용", width="large"),
                    },
                    key=f"month_editor_h2_{month}")

                data['part4_monthly_plan'][month] = edited_month.rename(
                    columns={
                        '대분류': 'big_category',
                        '중분류': 'mid_category',
                        '프로그램명': 'program_name',
                        '참여자': 'target',
                        '수행인력': 'staff',
                        '사업내용': 'content'
                    }).to_dict('records')

            st.markdown("---")

        # [3단계] PART별 다운로드 버튼은 노출하지 않는다 (4단계에서만 노출)

    # ── 검토 완료 → 4단계 이동 버튼 ──
    st.markdown("---")
    if st.button("계획서 작성 완료하기", type="primary",
                 use_container_width=True, key="abp_goto_complete"):
        st.session_state.work_step = 'COMPLETED'
        st.rerun()

    if st.button("🔄 처음부터 다시", use_container_width=True,
                 key="abp_reset_btn"):
        st.session_state.analysis_data = None
        st.session_state.uploaded_meta = []
        st.session_state.analyze_stage = 0
        st.session_state.analyze_progress = 0
        st.session_state.work_step = 'UPLOAD'
        st.rerun()


# ============================================================
# 4단계: 완성 / 다운로드 (PART1~4 Word 다운로드 - 기존 로직 유지)
# ============================================================
def _notify_download(part_label: str, file_name: str):
    """다운로드 완료 postMessage (기존 iframe 통신 유지)"""
    st.components.v1.html(f"""
        <script>
          try {{
            var target = (window.top !== window) ? window.top : window.parent;
            target.postMessage(
              {{
                type: "CHAMCHAM_ANNUALPLAN_DOWNLOAD",
                text: "{part_label} 다운로드 (Word)",
                part: "{part_label.replace(' ', '')}",
                fileName: "{file_name}"
              }},
              "*"
            );
            console.log("[CC] postMessage sent to top: {part_label}");
          }} catch (e) {{
            console.log("[CC] postMessage error", e);
          }}
        </script>
        """,
                                      height=0)


def render_completed_step():
    """4단계: 최종 완료 안내 + PART1~4 Word 다운로드"""
    data = st.session_state.analysis_data
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    st.markdown(
        """
        <div class="abp-card abp-complete-hero">
            <div class="abp-complete-icon">🎉</div>
            <p class="abp-complete-title">연간사업계획서가 완성되었습니다!</p>
            <p class="abp-complete-desc">아래 버튼으로 PART 1~4 Word 파일을 각각 다운로드하세요.</p>
        </div>
        """,
        unsafe_allow_html=True)

    h1_months = ["1월", "2월", "3월", "4월", "5월", "6월"]
    h2_months = ["7월", "8월", "9월", "10월", "11월", "12월"]

    part1_data = data.get('part1_general', {})
    part1_has_data = any([
        part1_data.get('need_1_user_desire'),
        part1_data.get('purpose_text'),
        part1_data.get('goals_text'),
        part1_data.get('feedback_table')
    ])
    part2_has_data = any(
        cat_data.get('detail_table') or cat_data.get('eval_table')
        for cat_data in data.get('part2_programs', {}).values()
        if isinstance(cat_data, dict))
    part3_has_data = any(
        data.get('part3_monthly_plan', {}).get(m) for m in h1_months)
    part4_monthly_data = any(
        data.get('part4_monthly_plan', {}).get(m) for m in h2_months)
    budget_eval = data.get('part4_budget_evaluation', {})
    part4_has_data = part4_monthly_data or budget_eval.get(
        'budget_table') or budget_eval.get('feedback_summary')

    any_part_ready = any([part1_has_data, part2_has_data, part3_has_data,
                          part4_has_data])
    if not any_part_ready:
        st.warning("먼저 참참AI 분석 시작을 눌러 내용을 생성해 주세요.")
        return

    dl1, dl2 = st.columns(2)
    dl3, dl4 = st.columns(2)

    with dl1:
        if part1_has_data:
            part1_report = generate_part1_report(data['part1_general'])
            if st.download_button(
                    label="📥 PART 1 다운로드 (Word)",
                    data=part1_report,
                    file_name=f"part1_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument"
                         ".wordprocessingml.document",
                    use_container_width=True,
                    key="abp_dl_p1"):
                _notify_download("PART 1", f"part1_{timestamp}.docx")

    with dl2:
        if part2_has_data:
            part2_report = generate_part2_report(data['part2_programs'])
            if st.download_button(
                    label="📥 PART 2 다운로드 (Word)",
                    data=part2_report,
                    file_name=f"part2_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument"
                         ".wordprocessingml.document",
                    use_container_width=True,
                    key="abp_dl_p2"):
                _notify_download("PART 2", f"part2_{timestamp}.docx")

    with dl3:
        if part3_has_data:
            h1_report = generate_monthly_program_report(
                data['part3_monthly_plan'], h1_months)
            if st.download_button(
                    label="📥 PART 3 다운로드 (Word)",
                    data=h1_report,
                    file_name=f"part3_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument"
                         ".wordprocessingml.document",
                    use_container_width=True,
                    key="abp_dl_p3"):
                _notify_download("PART 3", f"part3_{timestamp}.docx")

    with dl4:
        if part4_has_data:
            h2_report = generate_part4_full_report(
                data['part4_monthly_plan'], h2_months, budget_eval)
            if st.download_button(
                    label="📥 PART 4 다운로드 (Word)",
                    data=h2_report,
                    file_name=f"part4_{timestamp}.docx",
                    mime="application/vnd.openxmlformats-officedocument"
                         ".wordprocessingml.document",
                    use_container_width=True,
                    key="abp_dl_p4"):
                _notify_download("PART 4", f"part4_{timestamp}.docx")

    # ── 3단계 복귀 / 새로 시작 ──
    st.markdown("---")
    back_col, new_col = st.columns(2)
    with back_col:
        if st.button("← 다시 수정하기", use_container_width=True,
                     key="abp_back_to_edit"):
            st.session_state.work_step = 'EDITING'
            st.rerun()
    with new_col:
        if st.button("🔄 새로 시작하기", use_container_width=True,
                     key="abp_restart"):
            st.session_state.analysis_data = None
            st.session_state.uploaded_meta = []
            st.session_state.analyze_stage = 0
            st.session_state.analyze_progress = 0
            st.session_state.work_step = 'UPLOAD'
            st.rerun()


# ============================================================
# 메인 레이아웃 (진행표시 + 헤더 + 메인 72% / 도움말 28%)
# ============================================================

# ============================================================
# [랜딩 페이지] 최초 접속 시 랜딩 화면 표시 → 버튼으로 기존 화면 진입
# - "start": 기존 파일 업로드 화면으로 진입 (기존 기능 그대로)
# - "example": 기존 예시 데이터 로드 흐름으로 진입
# ============================================================
if st.session_state.get('show_landing', True):
    action = render_landing()
    if action == "start":
        st.session_state.show_landing = False
        st.rerun()
    elif action == "example":
        st.session_state.show_landing = False
        # 기존 render_sample_button() 과 동일한 예시 데이터 로드 흐름
        raw_data = get_default_data()
        rules = load_guideline_rules()
        adjusted_data, adjustment_logs = apply_guidelines_to_analysis(
            raw_data, rules)
        st.session_state.analysis_data = adjusted_data
        st.session_state.guideline_rules = rules
        for log in adjustment_logs:
            logger.info(log)
        st.rerun()
    st.stop()

# ── 상단: 제목/설명 → 4단계 진행표시 (모든 단계에서 항상 표시) ──
render_header()
render_step_indicator(st.session_state.work_step)

if st.session_state.get('_partial_fail'):
    st.warning("일부 내용을 가져오지 못했어요. 샘플 데이터로 보완해 주세요.")

# ── 본문: 메인(약 70%) + 오른쪽 도움말(약 30%) ──
main_col, help_col = st.columns([7, 3], gap="medium")

with main_col:
    step = st.session_state.work_step

    # ================= 1단계: 자료 업로드 =================
    if step == 'UPLOAD':
        with st.container(border=True):
            render_upload_step()

    # ================= 2단계: 분석하기 =================
    elif step == 'ANALYZING':
        with st.container(border=True):
            render_analyzing_screen()
            render_uploaded_files_card()
            # 파일 업로드가 완료된 상태 → AI 분석 자동 시작 (기존 시스템 동일)
            if st.session_state.get('is_analyzing'):
                run_analysis()
            elif st.session_state.analysis_data is None:
                # 예시 데이터 등으로 바로 진입한 경우가 아니면 업로드 단계로 복귀
                if not st.session_state.get('uploaded_meta'):
                    st.session_state.work_step = 'UPLOAD'
                    st.rerun()

    # ================= 3단계: 수정하기 =================
    elif step == 'EDITING':
        if st.session_state.analysis_data is None:
            st.session_state.work_step = 'UPLOAD'
            st.rerun()
        else:
            render_editing_step()

    # ================= 4단계: 완성 / 다운로드 =================
    elif step == 'COMPLETED':
        if st.session_state.analysis_data is None:
            st.session_state.work_step = 'UPLOAD'
            st.rerun()
        else:
            render_completed_step()

# 오른쪽 도움말 영역 (현재 단계에 맞는 안내)
with help_col:
    render_right_help(st.session_state.work_step)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "AI 연간 사업 계획 통합 에이전트 | 정보광장"
    "</div>",
    unsafe_allow_html=True)
