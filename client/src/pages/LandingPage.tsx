import type { ReactNode } from "react";
import { useLocation } from "wouter";
import { useAppStore, createInitialAnnualPlan } from "@/lib/store";
import "./LandingPage.css";

/**
 * 연간사업계획서 랜딩 페이지
 * - "/annual-business-plan" 진입 시 표시
 * - "작성하기" → 기존 작성 화면(/)으로 이동
 * - "예시로 살펴보기" → 예시 데이터로 기존 작성 흐름(/annual/part1) 진입
 */
export function LandingPage() {
  const [, navigate] = useLocation();
  const { setExtractedPrograms, setAnnualPlan, setCurrentStep, reset } =
    useAppStore();

  /** 연간사업계획서 작성하기 → 기존 작성화면(업로드 단계)으로 */
  const handleStart = () => {
    reset();
    setCurrentStep(1);
    navigate("/");
  };

  /** 예시로 살펴보기 → 예시 데이터로 기존 작성 흐름 진입 */
  const handleExample = () => {
    reset();
    const programs = [
      {
        id: "example-1",
        category: "보호",
        subCategory: "기초생활",
        programName: "아동 건강지킴이",
        targetChildren: "초등 전학년",
        executionDate: "매주 월·수",
        personnel: "사회복지사 1명",
        serviceContent:
          "아동의 건강한 성장을 위한 기초생활 지원 및 상담 프로그램입니다.",
      },
      {
        id: "example-2",
        category: "교육",
        subCategory: "학습지원",
        programName: "꿈을 키우는 학습클래스",
        targetChildren: "초등 3~6학년",
        executionDate: "매주 화·목",
        personnel: "교사 2명",
        serviceContent:
          "학업 동기 강화와 자기주도학습 역량을 키우는 학습지원 프로그램입니다.",
      },
      {
        id: "example-3",
        category: "정서지원",
        subCategory: "심리상담",
        programName: "마음음악 심리지원",
        targetChildren: "중등 1~3학년",
        executionDate: "격주 금요일",
        personnel: "심리상담사 1명",
        serviceContent: "음악 활동을 통한 정서 지원 및 심리 안정 프로그램입니다.",
      },
    ];

    setExtractedPrograms(programs as any);
    setAnnualPlan(createInitialAnnualPlan(programs as any));
    setCurrentStep(3);
    navigate("/annual/part1");
  };

  return (
    <div className="abp-landing">
      {/* 배경 장식 - 폭죽 도트 */}
      <span className="abp-dot" style={{ top: "8%", left: "22%", background: "#F272A8" }} />
      <span className="abp-dot" style={{ top: "15%", left: "8%", background: "#35C4C8" }} />
      <span className="abp-dot" style={{ top: "40%", left: "3%", background: "#F5D442" }} />
      <span className="abp-dot" style={{ top: "70%", left: "6%", background: "#B5D96B" }} />
      <span className="abp-dot" style={{ top: "10%", right: "6%", background: "#F272A8" }} />
      <span className="abp-dot" style={{ top: "35%", right: "4%", background: "#35C4C8" }} />
      <span className="abp-dot" style={{ top: "55%", right: "10%", background: "#F5D442" }} />
      <span className="abp-dot" style={{ top: "82%", right: "3%", background: "#B5D96B" }} />

      <div className="abp-container">
        {/* 상단 리본 */}
        <div className="abp-top-ribbon">
          <span>AI와 함께 쉽고 빠르게!</span>
        </div>

        {/* 하늘색 메인 제목 박스 */}
        <div className="abp-hero-box">
          <h1 className="abp-title">연간사업계획서</h1>
          <p className="abp-subtitle">우리 기관의 비전과 계획을 한눈에!</p>
          <p className="abp-subtitle">AI가 연간·월간 사업계획서 작성을 도와드립니다.</p>
        </div>

        {/* 중앙 캐릭터와 책상 */}
        <div className="abp-scene">
          {/* 왼쪽 장식 - 클로버(느낌표), 노트북, 연필 */}
          <div className="abp-side abp-side-left">
            <CloverWithExclamation />
            <LaptopDeco />
            <PencilDeco rotation={-35} />
          </div>

          {/* 캐릭터 + 책상 */}
          <div className="abp-desk-scene">
            <div className="abp-characters">
              <BoyWithBook />
              <GirlWaving />
            </div>
            <div className="abp-desk">
              <div className="abp-desk-top" />
              <div className="abp-desk-front" />
              <div className="abp-desk-books">
                <BookStack />
              </div>
            </div>
          </div>

          {/* 오른쪽 장식 - 연필, 책, 클로버 */}
          <div className="abp-side abp-side-right">
            <PencilDeco rotation={30} />
            <OpenBookDeco />
            <CloverSparkle />
          </div>
        </div>

        {/* 이렇게 진행돼요! + 단계 카드 */}
        <div className="abp-process-row">
          <div className="abp-process-panel">
            <div className="abp-process-ribbon">이렇게 진행돼요!</div>
            <div className="abp-steps">
              <StepCard
                num="01"
                color="#2BB8B8"
                icon={<UploadIcon />}
                title="자료 업로드"
                desc="기존 사업보고서나 관련 자료를 올려주세요."
              />
              <span className="abp-arrow">➜</span>
              <StepCard
                num="02"
                color="#F5A623"
                icon={<RobotIcon />}
                title="AI 분석·작성"
                desc="AI가 내용을 분석하여 계획 초안을 작성해드려요."
              />
              <span className="abp-arrow">➜</span>
              <StepCard
                num="03"
                color="#2BB8B8"
                icon={<DocChartIcon />}
                title="연간 계획 완성"
                desc="연간 사업계획서를 한눈에 확인하고 수정해요."
              />
              <span className="abp-arrow">➜</span>
              <StepCard
                num="04"
                color="#F5A623"
                icon={<CalendarIcon />}
                title="월간 계획 생성"
                desc="월간 사업계획서(12개월)를 자동으로 만들어드려요."
              />
            </div>
          </div>

          {/* 준비 자료 */}
          <div className="abp-materials">
            <div className="abp-materials-tab">준비 자료</div>
            <DocumentsIcon />
            <p className="abp-materials-title">PDF, DOCX 등</p>
            <p className="abp-materials-desc">
              사업보고서, 계획서, 평가서, 참고자료 등 다양한 형식 가능!
            </p>
          </div>
        </div>

        {/* 하단 버튼 */}
        <div className="abp-buttons">
          <button
            type="button"
            className="abp-btn abp-btn-primary"
            onClick={handleStart}
          >
            <span className="abp-btn-line">✏️ 연간사업계획서 작성하기</span>
            <span className="abp-btn-sub">지금 바로 시작해요!</span>
          </button>
          <button
            type="button"
            className="abp-btn abp-btn-secondary"
            onClick={handleExample}
          >
            <span className="abp-btn-line">📖 예시로 살펴보기</span>
            <span className="abp-btn-sub">작성 예시를 확인해보세요.</span>
          </button>
        </div>

        {/* 하단 안내 문구 */}
        <div className="abp-notice">
          💡 처음이신가요? 걱정 마세요! 따라하기 쉽도록 안내해드릴게요. 😊
        </div>
      </div>
    </div>
  );
}

/* =========================
   단계 카드
========================= */

function StepCard({
  num,
  color,
  icon,
  title,
  desc,
}: {
  num: string;
  color: string;
  icon: ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <div className="abp-step">
      <div className="abp-step-icon">
        <span className="abp-step-badge" style={{ background: color }}>
          {num}
        </span>
        {icon}
      </div>
      <p className="abp-step-title">{title}</p>
      <p className="abp-step-desc">{desc}</p>
    </div>
  );
}

/* =========================
   아이콘 (SVG)
========================= */

function UploadIcon() {
  return (
    <svg viewBox="0 0 80 80" className="abp-icon" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path
          d="M14 26 L26 12 H62 L70 26 V62 a4 4 0 0 1 -4 4 H18 a4 4 0 0 1 -4 -4 Z"
          fill="#F7CE55"
        />
        <path d="M14 26 H70" fill="none" />
        <circle cx="40" cy="48" r="14" fill="#FFFFFF" />
        <path
          d="M40 55 V42 M34 47 L40 41 L46 47"
          fill="none"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

function RobotIcon() {
  return (
    <svg viewBox="0 0 80 80" className="abp-icon" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path d="M40 14 V8" fill="none" strokeLinecap="round" />
        <circle cx="40" cy="7" r="3.5" fill="#F272A8" />
        <rect x="18" y="14" width="44" height="34" rx="10" fill="#FFFFFF" />
        <circle cx="30" cy="29" r="4" fill="#3A3A3A" stroke="none" />
        <circle cx="50" cy="29" r="4" fill="#3A3A3A" stroke="none" />
        <path
          d="M32 38 Q40 43 48 38"
          fill="none"
          strokeLinecap="round"
        />
        <rect x="32" y="48" width="16" height="10" rx="4" fill="#BDE3F5" />
        <path d="M12 26 V40" fill="none" strokeLinecap="round" />
        <circle cx="12" cy="43" r="3.5" fill="#F7CE55" />
        <path d="M68 26 V40" fill="none" strokeLinecap="round" />
        <circle cx="68" cy="43" r="3.5" fill="#F7CE55" />
        <path
          d="M22 52 V62 M58 52 V62"
          fill="none"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

function DocChartIcon() {
  return (
    <svg viewBox="0 0 80 80" className="abp-icon" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path
          d="M18 8 H50 L64 22 V70 a3 3 0 0 1 -3 3 H18 a3 3 0 0 1 -3 -3 V11 a3 3 0 0 1 3 -3 Z"
          fill="#FFFFFF"
        />
        <path d="M50 8 V22 H64" fill="#EDEAE0" />
        <path d="M42 22 H56 L50 14 Z" fill="none" />
        <path d="M42 22 V14 L56 26" fill="none" opacity="0" />
        <circle cx="34" cy="44" r="12" fill="#F7CE55" />
        <path
          d="M34 32 V44 H46"
          fill="none"
          strokeLinecap="round"
        />
        <path d="M24 64 H56 M24 70 H44" fill="none" strokeLinecap="round" />
      </g>
    </svg>
  );
}

function CalendarIcon() {
  return (
    <svg viewBox="0 0 80 80" className="abp-icon" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <rect x="12" y="16" width="56" height="56" rx="6" fill="#FFFFFF" />
        <path d="M12 30 H68" fill="none" />
        <path d="M12 16 a6 6 0 0 1 6 -6 H62 a6 6 0 0 1 6 6 V30 H12 Z" fill="#F5A623" />
        <path d="M26 8 V20 M54 8 V20" fill="none" strokeLinecap="round" />
        <circle cx="40" cy="52" r="11" fill="#8FCB6B" />
        <path
          d="M34 52 L39 57 L47 47"
          fill="none"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

function DocumentsIcon() {
  return (
    <svg viewBox="0 0 80 70" className="abp-materials-icon" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path
          d="M22 12 a3 3 0 0 1 3 -3 H44 L58 23 V57 a3 3 0 0 1 -3 3 H25 a3 3 0 0 1 -3 -3 Z"
          fill="#FFFFFF"
        />
        <path d="M44 9 V23 H58" fill="#EDEAE0" />
        <path
          d="M28 32 H52 M28 40 H52 M28 48 H44"
          fill="none"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

/* =========================
   장식 컴포넌트 (SVG)
========================= */

function CloverWithExclamation() {
  return (
    <svg viewBox="0 0 100 100" className="abp-deco abp-deco-clover-excl" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <ellipse cx="34" cy="34" rx="17" ry="17" fill="#8FCB6B" />
        <ellipse cx="66" cy="34" rx="17" ry="17" fill="#8FCB6B" />
        <ellipse cx="34" cy="66" rx="17" ry="17" fill="#8FCB6B" />
        <ellipse cx="66" cy="66" rx="17" ry="17" fill="#8FCB6B" />
        <ellipse cx="50" cy="50" rx="4" ry="4" fill="#FFFFFF" />
        <path
          d="M50 36 V50 M50 58 v2"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="5"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

function CloverSparkle() {
  return (
    <svg viewBox="0 0 100 100" className="abp-deco abp-deco-clover-sparkle" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <ellipse cx="34" cy="34" rx="16" ry="16" fill="#B5D96B" />
        <ellipse cx="66" cy="34" rx="16" ry="16" fill="#B5D96B" />
        <ellipse cx="34" cy="66" rx="16" ry="16" fill="#B5D96B" />
        <ellipse cx="66" cy="66" rx="16" ry="16" fill="#B5D96B" />
        <ellipse cx="50" cy="50" rx="4" ry="4" fill="#FFFFFF" />
      </g>
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinecap="round">
        <path d="M14 8 L14 0 M10 4 H18" fill="none" />
        <path d="M88 92 L88 84 M84 88 H92" fill="none" />
      </g>
    </svg>
  );
}

function LaptopDeco() {
  return (
    <svg viewBox="0 0 120 100" className="abp-deco abp-deco-laptop" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path d="M24 16 a4 4 0 0 1 4 -4 H92 a4 4 0 0 1 4 4 V70 H24 Z" fill="#6B7280" />
        <rect x="31" y="20" width="58" height="42" rx="2" fill="#BDE3F5" />
        <path d="M14 70 H106 L112 80 a3 3 0 0 1 -3 4 H11 a3 3 0 0 1 -3 -4 Z" fill="#9CA3AF" />
        <path d="M50 76 H70" fill="none" strokeLinecap="round" />
      </g>
    </svg>
  );
}

function PencilDeco({ rotation }: { rotation: number }) {
  return (
    <svg
      viewBox="0 0 40 140"
      className="abp-deco abp-deco-pencil"
      style={{ transform: `rotate(${rotation}deg)` }}
      aria-hidden="true"
    >
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <rect x="10" y="26" width="20" height="86" fill="#F7CE55" />
        <path d="M10 26 V112" fill="none" />
        <path d="M10 112 H30 L20 134 Z" fill="#F7CE55" />
        <path d="M10 112 V118 M30 112 V118" fill="none" />
        <rect x="10" y="10" width="20" height="16" rx="4" fill="#F272A8" />
      </g>
    </svg>
  );
}

function OpenBookDeco() {
  return (
    <svg viewBox="0 0 110 80" className="abp-deco abp-deco-book" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <path
          d="M55 18 C44 10 28 8 12 12 V62 C28 58 44 60 55 68 Z"
          fill="#FBD9C0"
        />
        <path
          d="M55 18 C66 10 82 8 98 12 V62 C82 58 66 60 55 68 Z"
          fill="#FBD9C0"
        />
        <path d="M55 18 V68" fill="none" />
        <path
          d="M20 24 C30 21 40 22 48 27 M20 34 C30 31 40 32 48 37 M20 44 C30 41 40 42 48 47"
          fill="none"
          stroke="#C89B7B"
          strokeWidth="2"
          strokeLinecap="round"
        />
        <path
          d="M90 24 C80 21 70 22 62 27 M90 34 C80 31 70 32 62 37 M90 44 C80 41 70 42 62 47"
          fill="none"
          stroke="#C89B7B"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

function BookStack() {
  return (
    <svg viewBox="0 0 90 60" className="abp-desk-books-svg" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="2.5" strokeLinejoin="round">
        <rect x="8" y="34" width="74" height="16" rx="3" fill="#E56B9F" />
        <rect x="14" y="18" width="62" height="16" rx="3" fill="#8FCB6B" />
        <path d="M24 40 H66 M30 24 H60" fill="none" strokeLinecap="round" stroke="#FFFFFF" strokeWidth="2" />
      </g>
    </svg>
  );
}

/* =========================
   캐릭터 (SVG)
========================= */

function BoyWithBook() {
  return (
    <svg viewBox="0 0 200 220" className="abp-character" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="3" strokeLinejoin="round">
        {/* 몸통 */}
        <path
          d="M60 130 C60 108 78 96 100 96 C122 96 140 108 140 130 V190 H60 Z"
          fill="#5B9BD5"
        />
        {/* 팔 - 책을 받치고 */}
        <path d="M62 140 C48 150 42 164 44 178" fill="none" strokeWidth="10" stroke="#5B9BD5" strokeLinecap="round" />
        <path d="M138 140 C152 150 158 164 156 178" fill="none" strokeWidth="10" stroke="#5B9BD5" strokeLinecap="round" />
        <circle cx="44" cy="180" r="8" fill="#FFE3CF" />
        <circle cx="156" cy="180" r="8" fill="#FFE3CF" />
        {/* 목 */}
        <rect x="90" y="112" width="20" height="18" fill="#FFE3CF" />
        {/* 머리 */}
        <ellipse cx="100" cy="72" rx="46" ry="42" fill="#FFE3CF" />
        {/* 머리카락 */}
        <path
          d="M54 72 C54 42 74 28 100 28 C126 28 146 42 146 72 C146 60 138 52 128 50 C120 44 108 42 100 42 C92 42 80 44 72 50 C62 52 54 60 54 72 Z"
          fill="#4A3B32"
        />
        {/* 눈(웃는 눈) */}
        <path d="M80 74 q6 -8 12 0" fill="none" strokeWidth="3.5" strokeLinecap="round" />
        <path d="M108 74 q6 -8 12 0" fill="none" strokeWidth="3.5" strokeLinecap="round" />
        {/* 볼 */}
        <ellipse cx="74" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none" />
        <ellipse cx="126" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none" />
        {/* 입 */}
        <path d="M92 90 q8 8 16 0" fill="none" strokeWidth="3.5" strokeLinecap="round" />
        {/* 책 */}
        <path
          d="M64 186 C50 178 38 178 30 182 V196 C38 192 50 192 64 200 Z"
          fill="#E05252"
        />
        <path
          d="M136 186 C150 178 162 178 170 182 V196 C162 192 150 192 136 200 Z"
          fill="#E05252"
        />
        <path
          d="M64 186 V200 C50 192 38 192 30 196 V182 C38 178 50 178 64 186 Z M136 186 V200 C150 192 162 192 170 196 V182 C162 178 150 178 136 186 Z"
          fill="none"
        />
        <path d="M100 190 C92 184 84 182 78 182 M100 190 C108 184 116 182 122 182" fill="none" strokeWidth="3" />
      </g>
    </svg>
  );
}

function GirlWaving() {
  return (
    <svg viewBox="0 0 200 220" className="abp-character" aria-hidden="true">
      <g stroke="#3A3A3A" strokeWidth="3" strokeLinejoin="round">
        {/* 몸통 */}
        <path
          d="M60 130 C60 108 78 96 100 96 C122 96 140 108 140 130 V190 H60 Z"
          fill="#F08080"
        />
        {/* 팔 - 양팔을 들고 환영 */}
        <path d="M64 138 C46 126 34 108 32 90" fill="none" strokeWidth="10" stroke="#F08080" strokeLinecap="round" />
        <path d="M136 138 C154 126 166 108 168 90" fill="none" strokeWidth="10" stroke="#F08080" strokeLinecap="round" />
        <circle cx="32" cy="86" r="8" fill="#FFE3CF" />
        <circle cx="168" cy="86" r="8" fill="#FFE3CF" />
        {/* 목 */}
        <rect x="90" y="112" width="20" height="18" fill="#FFE3CF" />
        {/* 머리 */}
        <ellipse cx="100" cy="72" rx="46" ry="42" fill="#FFE3CF" />
        {/* 머리카락 */}
        <path
          d="M52 66 C52 36 74 24 100 24 C126 24 148 36 148 66 L150 108 C150 114 144 116 140 110 L138 84 C130 74 116 68 100 68 C84 68 70 74 62 84 L60 110 C56 116 50 114 50 108 Z"
          fill="#A9764F"
        />
        {/* 눈(웃는 눈) */}
        <path d="M80 74 q6 -8 12 0" fill="none" strokeWidth="3.5" strokeLinecap="round" />
        <path d="M108 74 q6 -8 12 0" fill="none" strokeWidth="3.5" strokeLinecap="round" />
        {/* 볼 */}
        <ellipse cx="74" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none" />
        <ellipse cx="126" cy="86" rx="7" ry="5" fill="#FBBBC9" stroke="none" />
        {/* 입(벌린 웃음) */}
        <path d="M90 88 q10 12 20 0 Z" fill="#B55A5A" strokeWidth="2.5" />
      </g>
    </svg>
  );
}

export default LandingPage;
