import streamlit as st
import json
import re
import base64
from datetime import date
from google import genai
from questions import QUESTIONS, calculate_attachment_type

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FateLink — 운명의 상대",
    page_icon="🔮",
    layout="centered",
)

# ─────────────────────────────────────────────
# 커스텀 CSS (다크 + 보라/남색 그라데이션)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

    /* ── 오로라 + 별빛 애니메이션 ── */
    @keyframes aurora {
        0%   { background-position: 0% 50%; }
        25%  { background-position: 50% 100%; }
        50%  { background-position: 100% 50%; }
        75%  { background-position: 50% 0%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    @keyframes twinkle2 {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 0.1; }
    }
    @keyframes float1 {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    @keyframes float2 {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(10px); }
    }
    @keyframes bubble {
        0%   { transform: translateY(0) scale(1); opacity: 0; }
        10%  { opacity: 0.8; }
        75%  { opacity: 0.4; }
        100% { transform: translateY(-100vh) scale(0.4); opacity: 0; }
    }

    /* ── 기본 리셋 ── */
    .stApp {
        background: #0a0a0f;
        color: #ffffff;
        font-family: 'Noto Sans KR', sans-serif;
    }
    .stApp [data-testid="stHeader"] { background: transparent !important; }

    /* ── 오로라 오버레이 ── */
    .bg-aurora {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(ellipse 80% 50% at 20% 40%, rgba(177,74,237,0.13) 0%, transparent 60%),
            radial-gradient(ellipse 60% 60% at 80% 20%, rgba(255,45,120,0.09) 0%, transparent 55%),
            radial-gradient(ellipse 70% 40% at 50% 80%, rgba(0,240,255,0.08) 0%, transparent 50%),
            radial-gradient(ellipse 50% 50% at 70% 60%, rgba(177,74,237,0.07) 0%, transparent 50%);
        background-size: 200% 200%;
        animation: aurora 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    /* ── 별빛 오버레이 ── */
    .bg-stars {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .bg-stars .star {
        position: absolute;
        border-radius: 50%;
        background: white;
    }
    .bg-stars .star.s1 { width:4px; height:4px; top:8%;  left:12%; animation: twinkle 3s ease-in-out infinite; }
    .bg-stars .star.s2 { width:2px; height:2px; top:15%; left:28%; animation: twinkle2 5s ease-in-out infinite 0.5s; }
    .bg-stars .star.s3 { width:4px; height:4px; top:5%;  left:45%; animation: twinkle 4s ease-in-out infinite 1s; background: rgba(177,74,237,0.8); }
    .bg-stars .star.s4 { width:2px; height:2px; top:22%; left:62%; animation: twinkle2 3.5s ease-in-out infinite 0.3s; }
    .bg-stars .star.s5 { width:4px; height:4px; top:10%; left:78%; animation: twinkle 5.5s ease-in-out infinite 2s; background: rgba(0,240,255,0.7); }
    .bg-stars .star.s6 { width:2px; height:2px; top:30%; left:90%; animation: twinkle2 4s ease-in-out infinite 1.5s; }
    .bg-stars .star.s7 { width:4px; height:4px; top:40%; left:8%;  animation: twinkle 3.8s ease-in-out infinite 0.8s; }
    .bg-stars .star.s8 { width:2px; height:2px; top:35%; left:35%; animation: twinkle2 6s ease-in-out infinite 2.5s; background: rgba(255,45,120,0.6); }
    .bg-stars .star.s9 { width:4px; height:4px; top:50%; left:55%; animation: twinkle 4.5s ease-in-out infinite 1.2s; }
    .bg-stars .star.s10{ width:2px; height:2px; top:45%; left:72%; animation: twinkle2 3.2s ease-in-out infinite 0.7s; }
    .bg-stars .star.s11{ width:4px; height:4px; top:55%; left:18%; animation: twinkle 5s ease-in-out infinite 1.8s; background: rgba(177,74,237,0.6); }
    .bg-stars .star.s12{ width:2px; height:2px; top:60%; left:42%; animation: twinkle2 4.2s ease-in-out infinite 0.4s; }
    .bg-stars .star.s13{ width:4px; height:4px; top:65%; left:85%; animation: twinkle 3.5s ease-in-out infinite 2.2s; background: rgba(0,240,255,0.5); }
    .bg-stars .star.s14{ width:2px; height:2px; top:70%; left:5%;  animation: twinkle2 5.8s ease-in-out infinite 1.1s; }
    .bg-stars .star.s15{ width:4px; height:4px; top:75%; left:30%; animation: twinkle 4.8s ease-in-out infinite 0.6s; }
    .bg-stars .star.s16{ width:2px; height:2px; top:80%; left:60%; animation: twinkle2 3.6s ease-in-out infinite 1.9s; background: rgba(255,45,120,0.5); }
    .bg-stars .star.s17{ width:4px; height:4px; top:85%; left:48%; animation: twinkle 5.2s ease-in-out infinite 2.8s; }
    .bg-stars .star.s18{ width:2px; height:2px; top:90%; left:75%; animation: twinkle2 4.6s ease-in-out infinite 0.9s; }
    .bg-stars .star.s19{ width:4px; height:4px; top:25%; left:50%; animation: twinkle 6s ease-in-out infinite 3s; background: rgba(177,74,237,0.5); }
    .bg-stars .star.s20{ width:2px; height:2px; top:95%; left:20%; animation: twinkle2 3.9s ease-in-out infinite 1.4s; }

    /* ── 떠다니는 글로우 오브 ── */
    .bg-stars .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(60px);
        opacity: 0.4;
    }
    .bg-stars .orb1 {
        width: 200px; height: 200px;
        top: 10%; left: 5%;
        background: rgba(177,74,237,0.2);
        animation: float1 12s ease-in-out infinite;
    }
    .bg-stars .orb2 {
        width: 150px; height: 150px;
        top: 60%; right: 5%;
        background: rgba(255,45,120,0.15);
        animation: float2 15s ease-in-out infinite 3s;
    }
    .bg-stars .orb3 {
        width: 180px; height: 180px;
        top: 35%; left: 50%;
        background: rgba(0,240,255,0.1);
        animation: float1 18s ease-in-out infinite 6s;
    }

    /* ── 빛 버블 ── */
    .bg-stars .bubble {
        position: absolute;
        bottom: -30px;
        border-radius: 50%;
        opacity: 0;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3), rgba(177,74,237,0.15), transparent 70%);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .bg-stars .b1 {
        width: 33px; height: 33px; left: 8%;
        animation: bubble 14s ease-in-out infinite 0s;
    }
    .bg-stars .b2 {
        width: 24px; height: 24px; left: 22%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(0,240,255,0.15), transparent 70%);
        animation: bubble 18s ease-in-out infinite 3s;
    }
    .bg-stars .b3 {
        width: 45px; height: 45px; left: 38%;
        animation: bubble 16s ease-in-out infinite 6s;
    }
    .bg-stars .b4 {
        width: 21px; height: 21px; left: 52%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2), rgba(255,45,120,0.15), transparent 70%);
        animation: bubble 20s ease-in-out infinite 2s;
    }
    .bg-stars .b5 {
        width: 30px; height: 30px; left: 68%;
        animation: bubble 15s ease-in-out infinite 8s;
    }
    .bg-stars .b6 {
        width: 39px; height: 39px; left: 82%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(0,240,255,0.12), transparent 70%);
        animation: bubble 17s ease-in-out infinite 5s;
    }
    .bg-stars .b7 {
        width: 23px; height: 23px; left: 92%;
        animation: bubble 22s ease-in-out infinite 10s;
    }
    .bg-stars .b8 {
        width: 36px; height: 36px; left: 45%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.25), rgba(177,74,237,0.18), transparent 70%);
        animation: bubble 19s ease-in-out infinite 12s;
    }

    [data-testid="stSidebar"] { display: none; }
    hr { border-color: rgba(177, 74, 237, 0.15); margin: 2rem 0; }

    /* ── 제목: 네온 그라데이션 ── */
    h1, h2, h3 {
        background: linear-gradient(135deg, #b14aed, #ff2d78, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -0.5px;
    }

    /* ── 버튼: 네온 글로우 ── */
    .stButton > button {
        background: linear-gradient(135deg, #b14aed, #ff2d78);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(177, 74, 237, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 0 30px rgba(177, 74, 237, 0.5), 0 0 60px rgba(255, 45, 120, 0.2);
    }

    /* ── 네온 카드 (기본) ── */
    .neon-card {
        background: rgba(16, 16, 28, 0.85);
        border: 1px solid rgba(177, 74, 237, 0.2);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1rem 0;
        backdrop-filter: blur(12px);
        transition: border-color 0.3s;
    }
    .neon-card:hover {
        border-color: rgba(177, 74, 237, 0.5);
    }

    /* ── 카드 색상 변형 ── */
    .neon-card.purple { border-color: rgba(177, 74, 237, 0.4); box-shadow: 0 0 20px rgba(177, 74, 237, 0.08); }
    .neon-card.blue { border-color: rgba(0, 240, 255, 0.4); box-shadow: 0 0 20px rgba(0, 240, 255, 0.08); }
    .neon-card.pink { border-color: rgba(255, 45, 120, 0.4); box-shadow: 0 0 20px rgba(255, 45, 120, 0.08); }
    .neon-card.gold { border-color: rgba(255, 200, 55, 0.4); box-shadow: 0 0 20px rgba(255, 200, 55, 0.08); }
    .neon-card.green { border-color: rgba(52, 211, 153, 0.4); box-shadow: 0 0 20px rgba(52, 211, 153, 0.08); }

    /* ── 히어로 태그라인 ── */
    .hero-tagline {
        text-align: center;
        padding: 2.5rem 1.5rem;
        margin: 1.5rem 0;
        background: linear-gradient(135deg, rgba(177,74,237,0.15), rgba(255,45,120,0.1));
        border: 1px solid rgba(177, 74, 237, 0.3);
        border-radius: 24px;
        box-shadow: 0 0 40px rgba(177, 74, 237, 0.1);
    }
    .hero-tagline .label {
        font-size: 0.85rem;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 0.5rem;
    }
    .hero-tagline .tagline-text {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #b14aed, #ff2d78, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(177, 74, 237, 0.3);
    }
    .hero-tagline .sub-info {
        font-size: 0.95rem;
        color: #8b85a0;
        margin-top: 0.8rem;
    }

    /* ── 섹션 헤더 ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 2rem 0 1rem 0;
    }
    .section-header .icon {
        font-size: 1.5rem;
    }
    .section-header .title {
        font-size: 1.3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #b14aed, #ff2d78);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header .subtitle {
        font-size: 0.8rem;
        color: #6b6580;
        margin-left: auto;
    }

    /* ── 사주 테이블 ── */
    .saju-table {
        width: 100%;
        text-align: center;
        border-collapse: collapse;
    }
    .saju-table th {
        padding: 0.8rem;
        color: #a78bfa;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(177, 74, 237, 0.2);
    }
    .saju-table td {
        padding: 0.8rem;
        font-size: 1.1rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
    }

    /* ── 원형 프로그레스 (궁합) ── */
    .score-circle-wrap {
        text-align: center;
        margin: 1rem 0;
    }
    .score-circle {
        position: relative;
        width: 130px;
        height: 130px;
        margin: 0 auto;
    }
    .score-circle svg {
        transform: rotate(-90deg);
    }
    .score-circle .track {
        fill: none;
        stroke: rgba(255,255,255,0.06);
        stroke-width: 8;
    }
    .score-circle .fill {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dashoffset 1s ease;
    }
    .score-circle .score-num {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2rem;
        font-weight: 900;
    }
    .score-label {
        font-size: 0.85rem;
        color: #8b85a0;
        margin-top: 0.3rem;
    }

    /* ── 카톡 채팅 ── */
    .chat-wrap {
        max-width: 380px;
        margin: 1rem auto;
        padding: 1rem;
        background: rgba(16, 16, 28, 0.6);
        border-radius: 20px;
    }
    .chat-bubble {
        max-width: 75%;
        padding: 0.7rem 1rem;
        border-radius: 16px;
        margin: 0.4rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        word-break: keep-all;
    }
    .chat-bubble.other {
        background: rgba(177, 74, 237, 0.15);
        border: 1px solid rgba(177, 74, 237, 0.2);
        border-top-left-radius: 4px;
        margin-right: auto;
    }
    .chat-bubble.me {
        background: rgba(255, 45, 120, 0.15);
        border: 1px solid rgba(255, 45, 120, 0.2);
        border-top-right-radius: 4px;
        margin-left: auto;
    }
    .chat-name {
        font-size: 0.75rem;
        color: #8b85a0;
        margin-bottom: 0.2rem;
    }

    /* ── 프로필 카드 ── */
    .profile-card-new {
        background: linear-gradient(135deg, rgba(177,74,237,0.1), rgba(255,45,120,0.05));
        border: 1px solid rgba(177, 74, 237, 0.25);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    .profile-img-wrap {
        width: 180px;
        height: 180px;
        margin: 0 auto 1.2rem auto;
        border-radius: 50%;
        border: 3px solid rgba(177, 74, 237, 0.4);
        box-shadow: 0 0 30px rgba(177, 74, 237, 0.15);
        overflow: hidden;
    }
    .profile-img-wrap img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .profile-detail {
        text-align: left;
        margin: 1rem 0;
    }
    .profile-detail .row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .profile-detail .row .label {
        font-size: 0.85rem;
        color: #8b85a0;
        min-width: 60px;
    }
    .profile-detail .row .value {
        font-size: 1rem;
        color: #ffffff;
    }

    /* ── 키워드 태그 뱃지 ── */
    .tag-badge {
        display: inline-block;
        background: rgba(177, 74, 237, 0.15);
        border: 1px solid rgba(177, 74, 237, 0.3);
        border-radius: 50px;
        padding: 0.35rem 1rem;
        font-size: 0.85rem;
        color: #c4b5fd;
        margin: 0.2rem;
    }

    /* ── 타임라인 ── */
    .timeline-item {
        display: flex;
        gap: 1rem;
        margin: 0.8rem 0;
        padding: 1.2rem;
        background: rgba(16, 16, 28, 0.85);
        border-radius: 16px;
        border-left: 3px solid;
        transition: transform 0.2s;
    }
    .timeline-item:hover { transform: translateX(4px); }
    .timeline-item.green { border-left-color: #34d399; }
    .timeline-item.yellow { border-left-color: #fbbf24; }
    .timeline-item.red { border-left-color: #f87171; }
    .timeline-year {
        font-size: 1.3rem;
        font-weight: 900;
        color: #a78bfa;
        min-width: 50px;
    }
    .timeline-desc {
        font-size: 0.95rem;
        line-height: 1.7;
        color: #c8c3d4;
    }

    /* ── 경고 카드 ── */
    .warning-card {
        background: rgba(255, 200, 55, 0.06);
        border: 1px solid rgba(255, 200, 55, 0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .warning-card .warning-title {
        font-size: 1rem;
        font-weight: 700;
        color: #fbbf24;
        margin-bottom: 0.5rem;
    }

    /* ── 프로그레스 바 (스텝) ── */
    .step-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin: 1rem 0 2rem 0;
    }
    .step-dot {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 700;
        transition: all 0.3s;
    }
    .step-dot.active {
        background: linear-gradient(135deg, #b14aed, #ff2d78);
        color: white;
        box-shadow: 0 0 15px rgba(177, 74, 237, 0.4);
    }
    .step-dot.done {
        background: rgba(177, 74, 237, 0.3);
        color: #c4b5fd;
    }
    .step-dot.pending {
        background: rgba(255,255,255,0.06);
        color: #4a4558;
    }
    .step-line {
        width: 40px;
        height: 2px;
        background: rgba(255,255,255,0.08);
    }
    .step-line.done {
        background: linear-gradient(90deg, #b14aed, #ff2d78);
    }

    /* ── 궁합 작은 카드 ── */
    .compat-mini {
        text-align: center;
        padding: 1.2rem 0.5rem;
        background: rgba(16, 16, 28, 0.85);
        border: 1px solid rgba(177, 74, 237, 0.15);
        border-radius: 16px;
    }
    .compat-mini .num {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #b14aed, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .compat-mini .label {
        font-size: 0.8rem;
        color: #8b85a0;
        margin-top: 0.3rem;
    }

    /* ── 랜딩 페이지 ── */
    .landing-wrap {
        text-align: center;
        padding: 3rem 1rem;
    }
    .landing-title {
        font-size: 110px !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #b14aed, #ff2d78, #00f0ff) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        letter-spacing: 8px;
        margin-bottom: 0.3rem;
        text-shadow: 0 0 40px rgba(177,74,237,0.4), 0 0 80px rgba(255,45,120,0.2);
        filter: drop-shadow(0 0 30px rgba(177,74,237,0.3));
        line-height: 1;
    }
    .landing-underline {
        width: 360px;
        height: 9px;
        margin: 0 auto 1.5rem auto;
        background: linear-gradient(90deg, transparent, #b14aed, #ff2d78, #00f0ff, transparent);
        border-radius: 4px;
        box-shadow: 0 0 20px rgba(177,74,237,0.5);
    }
    .landing-sub {
        font-size: 1.2rem;
        color: #8b85a0;
        line-height: 1.8;
    }
    .landing-tags {
        display: flex;
        justify-content: center;
        gap: 0.8rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    .landing-tag {
        background: rgba(177, 74, 237, 0.1);
        border: 1px solid rgba(177, 74, 237, 0.25);
        border-radius: 50px;
        padding: 0.5rem 1.2rem;
        font-size: 0.9rem;
        color: #c4b5fd;
    }

    /* ── 라디오 / 입력 ── */
    .stRadio > div {
        background: rgba(16, 16, 28, 0.6);
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid rgba(177, 74, 237, 0.1);
    }
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        background: rgba(16, 16, 28, 0.8) !important;
        border: 1px solid rgba(177, 74, 237, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    .stTextInput label, .stDateInput label,
    .stSelectbox label, .stRadio label {
        color: #ffffff !important;
    }

    /* ── 스크롤바 ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: rgba(177, 74, 237, 0.3); border-radius: 3px; }

    /* ── 결과카드 하위호환 ── */
    .result-card { /* 기존 클래스 fallback */ }
    .score-big {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #b14aed, #ff2d78, #00f0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 배경 오로라 + 별빛 오버레이
# ─────────────────────────────────────────────
st.markdown("""
<div class="bg-aurora"></div>
<div class="bg-stars">
    <div class="star s1"></div><div class="star s2"></div><div class="star s3"></div>
    <div class="star s4"></div><div class="star s5"></div><div class="star s6"></div>
    <div class="star s7"></div><div class="star s8"></div><div class="star s9"></div>
    <div class="star s10"></div><div class="star s11"></div><div class="star s12"></div>
    <div class="star s13"></div><div class="star s14"></div><div class="star s15"></div>
    <div class="star s16"></div><div class="star s17"></div><div class="star s18"></div>
    <div class="star s19"></div><div class="star s20"></div>
    <div class="orb orb1"></div>
    <div class="orb orb2"></div>
    <div class="orb orb3"></div>
    <div class="bubble b1"></div>
    <div class="bubble b2"></div>
    <div class="bubble b3"></div>
    <div class="bubble b4"></div>
    <div class="bubble b5"></div>
    <div class="bubble b6"></div>
    <div class="bubble b7"></div>
    <div class="bubble b8"></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session State 초기화
# ─────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0  # 0: 랜딩, 1: 기본정보, 2: MBTI, 3: 애착유형, 4: 로딩/결과

if "user_data" not in st.session_state:
    st.session_state.user_data = {}

if "result" not in st.session_state:
    st.session_state.result = None


# ─────────────────────────────────────────────
# Gemini API 호출
# ─────────────────────────────────────────────
def call_gemini(user_data: dict) -> dict:
    """사용자 정보를 기반으로 Gemini에 배우자 예측 요청"""
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

    # 연애 상태에 따른 분석 방향 분기
    is_dating = user_data.get("is_dating", False)
    if is_dating:
        analysis_context = "현재 연애 중인 사용자입니다. 현재 연인이 운명의 상대인지 분석하고, 현재 관계의 방향성과 조언을 중심으로 답해주세요. 배우자 프로필은 '현재 연인에게 가장 어울리는 이상적 파트너상'으로 해석해주세요."
        meeting_context = "meeting_prediction의 timing은 '현재 연인과의 관계가 한 단계 발전하는 시기', place는 '관계 전환점이 되는 장소', first_meet_scenario는 '현재 연인과의 관계에서 가장 결정적인 순간 시나리오'로 작성해주세요."
    else:
        analysis_context = "현재 싱글인 사용자입니다. 미래에 만날 운명의 배우자를 예측해주세요."
        meeting_context = "meeting_prediction은 미래 배우자와의 첫 만남을 예측해주세요."

    dating_warning_context = "연애 중인 사람에게 맞는 조언을 해줘." if is_dating else "솔로에게 맞는 조언을 해줘."
    timing_label = "관계 발전 시기" if is_dating else "만나는 시기"
    place_label = "전환점이 되는 장소" if is_dating else "만나는 장소"
    scenario_label = "결정적 순간 시나리오" if is_dating else "첫 만남 시나리오"

    prompt = f"""당신은 동양 사주학, MBTI 성격유형론, 애착유형 심리학을 결합한 AI 운명 분석가입니다.
아래 사용자 정보를 바탕으로 분석해주세요. 반드시 구체적이고 개인화된 결과를 제공하세요.

{analysis_context}
{meeting_context}

## 사용자 정보
- 이름: {user_data['name']}
- 생년월일: {user_data['birth_date']}
- 태어난 시간: {user_data['birth_time']}
- 성별: {user_data['gender']}
- MBTI: {user_data['mbti']}
- 애착유형: {user_data['attachment_type']}
- 불안 점수: {user_data['anxiety_score']}/60
- 회피 점수: {user_data['avoidance_score']}/60
- 연애 상태: {"연애 중" if is_dating else "싱글"}

## 반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이 JSON만):
{{
    "love_tagline": "사용자의 연애 DNA를 한 마디로 표현. 예: '불꽃형 집착러', '쿨한 척 전문가', '모태솔로 감성장인'. 재미있고 캡처하고 싶은 5~10자 이내 캐치프레이즈.",
    "saju_detail": {{
        "year_cheongan": "년주 천간 한자(한글)",
        "year_jiji": "년주 지지 한자(한글)",
        "month_cheongan": "월주 천간 한자(한글)",
        "month_jiji": "월주 지지 한자(한글)",
        "day_cheongan": "일주 천간 한자(한글)",
        "day_jiji": "일주 지지 한자(한글)",
        "hour_cheongan": "시주 천간 한자(한글) (모르면 추정)",
        "hour_jiji": "시주 지지 한자(한글) (모르면 추정)",
        "ilgan_analysis": "일간 오행 성격 분석 (3~4문장. 연애 성향 중심으로)",
        "yongsin": "용신 설명 (어떤 상대를 만나야 밸런스가 맞는지 1~2문장)"
    }},
    "mbti_analysis": "MBTI 유형 분석. 이 유형이 연애에서 어떤 특성을 보이는지, 강점과 약점을 구체적으로 설명. 3~4문장.",
    "attachment_analysis": "애착유형 분석. 이 유형이 연애에서 어떤 패턴을 보이는지, 불안 점수와 회피 점수를 반영하여 구체적으로 설명. 3~4문장.",
    "comprehensive_profile": "사주+MBTI+애착유형을 종합하여 '너는 이런 사람이야'라고 설명. 반말로 친근하게 써줘. 구체적인 연애 상황 예시를 2~3개 포함해서 소름 돋게 맞춰줘. 예: '넌 좋아하는 사람 생기면 카톡 읽씹 당하면 바로 불안해지는 타입이야. 근데 막상 상대가 다가오면 갑자기 부담스러워서 한 발 빼지.' 이런 식으로 7~10문장.",
    "dating_warning": "연애할 때 주의해야 할 점. 반말로 친근하게 경고해줘. 구체적인 상황 예시와 함께 조언. {dating_warning_context} 3~5문장.",
    "love_timeline": [
        {{
            "year": "2026",
            "emoji": "🟡 또는 🟢 또는 🔴",
            "description": "해당 연도 애정운 설명 (2~3문장. 구체적인 시기와 상황 포함)"
        }},
        {{
            "year": "2027",
            "emoji": "이모지",
            "description": "설명"
        }},
        {{
            "year": "2028",
            "emoji": "이모지",
            "description": "설명"
        }}
    ],
    "spouse_profile": {{
        "mbti": "배우자 예측 MBTI",
        "attachment_type": "배우자 예측 애착유형",
        "age_range": "배우자 예상 나이대 (1살 차이 범위로 좁게 예측. 예: '26~27세', '30~31세'. 반드시 최솟값과 최댓값 차이가 1이어야 함)",
        "jobs": "배우자 예측 직업군 (한 가지로 한정짓지 말고 2~3가지 가능성 제시. 예: '스타트업 기획자, UX 디자이너, 또는 프리랜서 작가 계열')",
        "appearance": "외형 특징 (키, 체형, 헤어스타일, 인상, 분위기 등 상세하게 3~4문장)",
        "personality": "성격 특징 (어떤 성격인지 구체적으로 3~4문장. 예: '평소엔 조용한데 친한 사람 앞에서는 말 많아지는 타입. 감정 표현은 서툴지만 행동으로 보여주는 스타일.')",
        "why_match": "왜 이 사용자와 어울리는지 구체적으로 설명. 사주, MBTI, 애착유형 근거를 들어 3~4문장으로.",
        "appearance_prompt": "배우자 외모를 영어로 묘사. 실사풍 인물 사진 생성용. 예: 'Korean woman, 165cm, long black hair, soft smile, wearing casual outfit, warm brown eyes, slim build'. 반드시 영어로, 1~2문장으로.",
        "personality_keywords": ["성격 키워드1", "성격 키워드2", "성격 키워드3"]
    }},
    "meeting_prediction": {{
        "timing": "{timing_label} (예: 2027년 여름)",
        "place": "{place_label} 설명",
        "first_meet_scenario": "{scenario_label} (소설형, 4~5문장)",
        "first_conversation": "운명의 상대와의 예상 첫 대화. 반드시 아래 형식으로 작성해줘. 각 대사는 반드시 줄바꿈(\\n)으로 구분하고, '상대:' 또는 '나:'로 시작해야 해. 3~4턴의 대화를 써줘. 형식 예시:\\n상대: 혹시 이 자리 비어있나요?\\n나: 네, 앉으세요!\\n상대: 감사합니다. 여기 자주 오세요?\\n나: 아뇨, 오늘 처음이에요."
    }},
    "compatibility": {{
        "total_score": 85,
        "personality_score": 90,
        "communication_score": 80,
        "conflict_resolution_score": 75,
        "caution_period": "주의해야 할 시기와 이유 (2~3문장)"
    }}
}}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=0,
            top_k=1,
            top_p=0.01,
        ),
    )

    # JSON 파싱
    text = response.text.strip()
    # 코드블록 제거
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def generate_spouse_image(appearance_prompt: str, gender: str, birth_date: str) -> bytes | None:
    """Gemini 이미지 생성 (배우자 외형)"""
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        # 나이 계산
        birth = date.fromisoformat(birth_date)
        today = date.today()
        user_age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        # 배우자 예상 나이대: 사용자 나이 ±3세 범위
        spouse_age_min = user_age - 3
        spouse_age_max = user_age + 3
        spouse_age_range = f"{spouse_age_min}-{spouse_age_max}"

        opposite = "여성" if gender == "남성" else "남성"
        opposite_en = "woman" if gender == "남성" else "man"

        full_prompt = (
            f"A photorealistic portrait of a Korean {opposite_en} "
            f"in their {spouse_age_range} years old, "
            f"{appearance_prompt} "
            f"Soft warm lighting, gentle expression, natural background. "
            f"Do not include any text in the image."
        )

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[full_prompt],
            config=genai.types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        for part in response.parts:
            if part.inline_data is not None:
                return part.inline_data.data

        return None
    except Exception as e:
        st.warning(f"이미지 생성에 실패했습니다: {e}")
        return None


# ─────────────────────────────────────────────
# STEP 0: 랜딩 페이지
# ─────────────────────────────────────────────
def render_step_bar(current_step):
    """스텝 프로그레스 바 (1~4)"""
    labels = ["정보", "MBTI", "애착", "결과"]
    dots_html = ""
    for i in range(4):
        step_num = i + 1
        if step_num < current_step:
            cls = "done"
        elif step_num == current_step:
            cls = "active"
        else:
            cls = "pending"
        dots_html += f'<div class="step-dot {cls}">{labels[i]}</div>'
        if i < 3:
            line_cls = "done" if step_num < current_step else ""
            dots_html += f'<div class="step-line {line_cls}"></div>'
    st.markdown(f'<div class="step-bar">{dots_html}</div>', unsafe_allow_html=True)


def render_landing():
    st.markdown("""
    <div class="landing-wrap">
        <p class="landing-title">FateLink</p>
        <div class="landing-underline"></div>
        <p class="landing-sub">
            사주 × MBTI × 애착유형<br>
            AI가 찾아주는 <b style="color:#ff2d78;">운명의 상대</b>
        </p>
        <div class="landing-tags">
            <span class="landing-tag">🌙 사주팔자</span>
            <span class="landing-tag">🧠 MBTI</span>
            <span class="landing-tag">💕 애착유형</span>
            <span class="landing-tag">🔮 AI 분석</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ 운명의 상대 찾기", use_container_width=True):
            st.session_state.step = 1
            st.rerun()


# ─────────────────────────────────────────────
# STEP 1: 기본 정보 입력
# ─────────────────────────────────────────────
def render_basic_info():
    render_step_bar(1)
    st.markdown("## 📝 기본 정보를 알려주세요")
    st.markdown("*사주 분석을 위해 정확한 정보를 입력해주세요*")
    st.markdown("---")

    name = st.text_input("이름", placeholder="홍길동")

    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input(
            "생년월일",
            value=date.today(),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="YYYY/MM/DD",
        )
    with col2:
        birth_time = st.selectbox(
            "태어난 시간",
            [
                "모름",
                "자시 (23:00~01:00)",
                "축시 (01:00~03:00)",
                "인시 (03:00~05:00)",
                "묘시 (05:00~07:00)",
                "진시 (07:00~09:00)",
                "사시 (09:00~11:00)",
                "오시 (11:00~13:00)",
                "미시 (13:00~15:00)",
                "신시 (15:00~17:00)",
                "유시 (17:00~19:00)",
                "술시 (19:00~21:00)",
                "해시 (21:00~23:00)",
            ],
        )

    gender = st.radio("성별", ["남성", "여성"], horizontal=True)

    st.markdown("---")
    is_dating = st.radio(
        "현재 연애 중이신가요? 💕",
        ["아니요, 솔로예요", "네, 연애 중이에요"],
        horizontal=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("다음 →", use_container_width=True):
            if not name:
                st.warning("이름을 입력해주세요!")
                return
            st.session_state.user_data["name"] = name
            st.session_state.user_data["birth_date"] = str(birth_date)
            st.session_state.user_data["birth_time"] = birth_time
            st.session_state.user_data["gender"] = gender
            st.session_state.user_data["is_dating"] = (is_dating == "네, 연애 중이에요")
            st.session_state.step = 2
            st.rerun()


# ─────────────────────────────────────────────
# STEP 2: MBTI 선택
# ─────────────────────────────────────────────
def render_mbti():
    render_step_bar(2)
    st.markdown("## 🧠 MBTI를 선택해주세요")
    st.markdown("*본인의 MBTI 유형을 선택해주세요*")
    st.markdown("---")

    mbti_types = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ",
    ]

    # 4x4 그리드로 표시
    selected_mbti = None
    for row in range(4):
        cols = st.columns(4)
        for col_idx in range(4):
            idx = row * 4 + col_idx
            with cols[col_idx]:
                if st.button(mbti_types[idx], key=f"mbti_{idx}", use_container_width=True):
                    selected_mbti = mbti_types[idx]

    if selected_mbti:
        st.session_state.user_data["mbti"] = selected_mbti
        st.session_state.step = 3
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 이전"):
            st.session_state.step = 1
            st.rerun()


# ─────────────────────────────────────────────
# STEP 3: 애착유형 테스트
# ─────────────────────────────────────────────
def render_attachment_test():
    render_step_bar(3)
    st.markdown("## 💕 애착유형 테스트")
    st.markdown("*각 상황에서 자신과 가장 가까운 반응을 골라주세요*")
    st.markdown("---")

    answers = []
    current_category = None

    for i, q in enumerate(QUESTIONS):
        # 카테고리 헤더
        if q["category"] != current_category:
            current_category = q["category"]
            st.markdown(f"### {current_category}")

        # 선택지 텍스트만 표시 (점수는 숨김)
        option_texts = [opt[0] for opt in q["options"]]
        choice = st.radio(
            q["question"],
            option_texts,
            index=None,
            key=f"q_{i}",
        )

        if choice is not None:
            answers.append(option_texts.index(choice))
        else:
            answers.append(None)

        st.markdown("")  # 간격

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 이전"):
            st.session_state.step = 2
            st.rerun()
    with col3:
        if st.button("결과 보기 🔮", use_container_width=True):
            if None in answers:
                st.warning("모든 문항에 답해주세요! 🙏")
                return
            # 채점
            attachment_type, anxiety, avoidance = calculate_attachment_type(answers)
            st.session_state.user_data["attachment_type"] = attachment_type
            st.session_state.user_data["anxiety_score"] = anxiety
            st.session_state.user_data["avoidance_score"] = avoidance
            st.session_state.step = 4
            st.rerun()


# ─────────────────────────────────────────────
# STEP 4: 결과 페이지
# ─────────────────────────────────────────────
def render_result():
    # API 호출 (한 번만)
    if st.session_state.result is None:
        with st.spinner("🔮 사주를 분석하고 있습니다..."):
            try:
                st.session_state.result = call_gemini(st.session_state.user_data)
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
                if st.button("다시 시도"):
                    st.rerun()
                return

    # 이미지 생성 (한 번만)
    if "spouse_image" not in st.session_state:
        with st.spinner("💜 운명의 상대 모습을 그리고 있습니다..."):
            spouse = st.session_state.result["spouse_profile"]
            st.session_state.spouse_image = generate_spouse_image(
                spouse.get("appearance_prompt", ""),
                st.session_state.user_data["gender"],
                st.session_state.user_data["birth_date"],
            )

    result = st.session_state.result
    user = st.session_state.user_data
    is_dating = user.get("is_dating", False)

    # ══════════════════════════════════════
    # 히어로 태그라인
    # ══════════════════════════════════════
    dating_badge = "💑 연애 중" if is_dating else "💫 솔로"
    tagline = result.get("love_tagline", "")
    st.markdown(f"""
    <div class="hero-tagline">
        <p class="label">✦ 당신의 연애 DNA ✦</p>
        <p class="tagline-text">{tagline}</p>
        <p class="sub-info">{user['name']} · {user['mbti']} · {user['attachment_type']} · {dating_badge}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 1. 사주 상세 분석
    # ══════════════════════════════════════
    st.markdown('<div class="section-header"><span class="icon">🌙</span><span class="title">사주 상세 분석</span></div>', unsafe_allow_html=True)
    saju = result["saju_detail"]

    st.markdown(f"""
    <div class="neon-card purple">
        <table class="saju-table">
            <tr><th></th><th>천간</th><th>지지</th></tr>
            <tr><td>🟣 년주</td><td>{saju['year_cheongan']}</td><td>{saju['year_jiji']}</td></tr>
            <tr><td>🔵 월주</td><td>{saju['month_cheongan']}</td><td>{saju['month_jiji']}</td></tr>
            <tr><td>🟢 일주</td><td>{saju['day_cheongan']}</td><td>{saju['day_jiji']}</td></tr>
            <tr><td>🟡 시주</td><td>{saju['hour_cheongan']}</td><td>{saju['hour_jiji']}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="neon-card purple">
        <p style="line-height: 1.9;">{saju['ilgan_analysis']}</p>
        <br>
        <p style="color: #b14aed;"><b>💎 용신</b>: {saju['yongsin']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 2. MBTI 분석
    # ══════════════════════════════════════
    st.markdown(f'<div class="section-header"><span class="icon">🧠</span><span class="title">MBTI 분석</span><span class="subtitle">{user["mbti"]}</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="neon-card blue">
        <p style="line-height: 1.9;">{result['mbti_analysis']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 3. 애착유형 분석
    # ══════════════════════════════════════
    st.markdown(f'<div class="section-header"><span class="icon">💕</span><span class="title">애착유형 분석</span><span class="subtitle">{user["attachment_type"]}</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="neon-card pink">
        <p style="line-height: 1.9;">{result['attachment_analysis']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 4. 종합 프로필 + 연애 주의점
    # ══════════════════════════════════════
    st.markdown('<div class="section-header"><span class="icon">🔮</span><span class="title">너는 이런 사람이야</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="neon-card purple">
        <p style="font-size: 1.05rem; line-height: 2.0;">{result['comprehensive_profile']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="warning-card">
        <p class="warning-title">⚠️ 연애할 때 이것만은 조심해</p>
        <p style="line-height: 1.9; color: #c8c3d4;">{result['dating_warning']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 5. 애정운 타임라인
    # ══════════════════════════════════════
    st.markdown('<div class="section-header"><span class="icon">📅</span><span class="title">애정운 타임라인</span></div>', unsafe_allow_html=True)
    for item in result["love_timeline"]:
        emoji = item['emoji']
        color_cls = "green" if "🟢" in emoji else ("red" if "🔴" in emoji else "yellow")
        st.markdown(f"""
        <div class="timeline-item {color_cls}">
            <div class="timeline-year">{item['year']}</div>
            <div class="timeline-desc">{item['description']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 6. 만남 예측 + 카톡 대화
    # ══════════════════════════════════════
    meeting_title = "관계 전환점 예측" if is_dating else "만남 예측"
    st.markdown(f'<div class="section-header"><span class="icon">📅</span><span class="title">{meeting_title}</span></div>', unsafe_allow_html=True)
    meeting = result["meeting_prediction"]

    timing_label = "🕐 관계 발전 시기" if is_dating else "🕐 만나는 시기"
    place_label = "📍 전환점 장소" if is_dating else "📍 만나는 장소"
    scenario_label = "결정적 순간" if is_dating else "첫 만남 시나리오"

    st.markdown(f"""
    <div class="neon-card green">
        <p>{timing_label}: <b style="color:#34d399;">{meeting['timing']}</b></p>
        <p>{place_label}: <b style="color:#34d399;">{meeting['place']}</b></p>
        <br>
        <p style="color: #34d399; font-weight: 700;">💫 {scenario_label}</p>
        <p style="font-style: italic; line-height: 1.9; color: #c8c3d4;">{meeting['first_meet_scenario']}</p>
    </div>
    """, unsafe_allow_html=True)

    # 카톡 스타일 첫 대화
    first_convo = meeting.get("first_conversation", "")
    if first_convo:
        st.markdown('<div class="section-header"><span class="icon">💬</span><span class="title">예상 첫 대화</span></div>', unsafe_allow_html=True)
        # 대화를 파싱해서 말풍선으로 변환
        chat_html = '<div class="chat-wrap">'
        # 줄바꿈 또는 / 로 구분된 대화를 파싱
        lines = re.split(r'\n|/(?=\s*(?:상대|나)\s*:)', first_convo)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r'^(상대|그녀?)\s*:', line):
                text = re.sub(r'^(상대|그녀?)\s*:\s*', '', line)
                chat_html += f'<div class="chat-name">운명의 상대 💜</div>'
                chat_html += f'<div class="chat-bubble other">{text}</div>'
            elif re.match(r'^나\s*:', line):
                text = re.sub(r'^나\s*:\s*', '', line)
                chat_html += f'<div class="chat-name" style="text-align:right;">나 ✨</div>'
                chat_html += f'<div class="chat-bubble me">{text}</div>'
            else:
                # 구분자 없는 경우 상대방 대사로 처리
                chat_html += f'<div class="chat-bubble other">{line}</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 7. 운명의 상대 프로필 + 이미지
    # ══════════════════════════════════════
    spouse_title = "이상적 파트너상" if is_dating else "운명의 상대"
    st.markdown(f'<div class="section-header"><span class="icon">💍</span><span class="title">{spouse_title}</span></div>', unsafe_allow_html=True)
    spouse = result["spouse_profile"]

    # 이미지 (원형)
    if st.session_state.spouse_image:
        img_b64 = base64.b64encode(st.session_state.spouse_image).decode()
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <div class="profile-img-wrap">
                <img src="data:image/png;base64,{img_b64}" alt="운명의 상대">
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 프로필 상세
    st.markdown(f"""
    <div class="profile-card-new">
        <div class="profile-detail">
            <div class="row"><span class="label">🎂 나이</span><span class="value">{spouse.get('age_range', '')}</span></div>
            <div class="row"><span class="label">🧠 MBTI</span><span class="value">{spouse['mbti']}</span></div>
            <div class="row"><span class="label">💕 애착</span><span class="value">{spouse['attachment_type']}</span></div>
            <div class="row"><span class="label">💼 직업</span><span class="value">{spouse.get('jobs', spouse.get('job', ''))}</span></div>
            <div class="row"><span class="label">✨ 외형</span><span class="value">{spouse['appearance']}</span></div>
            <div class="row"><span class="label">🎭 성격</span><span class="value">{spouse.get('personality', '')}</span></div>
        </div>
        <div style="margin-top: 1rem;">
            {"".join(f'<span class="tag-badge">{kw}</span>' for kw in spouse["personality_keywords"])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 왜 어울리는지
    why_match = spouse.get("why_match", "")
    if why_match:
        st.markdown(f"""
        <div class="neon-card pink">
            <p style="font-weight: 700; color: #ff2d78; margin-bottom: 0.5rem;">💘 왜 이 사람이 운명인가?</p>
            <p style="line-height: 1.9;">{why_match}</p>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 8. 궁합 분석 (원형 프로그레스)
    # ══════════════════════════════════════
    st.markdown('<div class="section-header"><span class="icon">💯</span><span class="title">궁합 분석</span></div>', unsafe_allow_html=True)
    compat = result["compatibility"]
    total = compat['total_score']
    circumference = 2 * 3.14159 * 54
    offset = circumference - (circumference * total / 100)

    st.markdown(f"""
    <div class="score-circle-wrap">
        <div class="score-circle">
            <svg width="130" height="130" viewBox="0 0 130 130">
                <circle class="track" cx="65" cy="65" r="54"/>
                <circle class="fill" cx="65" cy="65" r="54"
                    stroke="url(#scoreGrad)" stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"/>
                <defs>
                    <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#b14aed"/>
                        <stop offset="50%" stop-color="#ff2d78"/>
                        <stop offset="100%" stop-color="#00f0ff"/>
                    </linearGradient>
                </defs>
            </svg>
            <div class="score-num" style="background: linear-gradient(135deg, #b14aed, #ff2d78); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total}%</div>
        </div>
        <p class="score-label">전체 궁합 점수</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="compat-mini">
            <p class="num">{compat['personality_score']}%</p>
            <p class="label">성격 궁합</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="compat-mini">
            <p class="num">{compat['communication_score']}%</p>
            <p class="label">대화 궁합</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="compat-mini">
            <p class="num">{compat['conflict_resolution_score']}%</p>
            <p class="label">갈등 해결력</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="warning-card" style="margin-top: 1rem;">
        <p class="warning-title">⚠️ 주의 시기</p>
        <p style="line-height: 1.9; color: #c8c3d4;">{compat['caution_period']}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 다시하기 ──
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 다시 시작하기", use_container_width=True):
            st.session_state.step = 0
            st.session_state.user_data = {}
            st.session_state.result = None
            if "spouse_image" in st.session_state:
                del st.session_state["spouse_image"]
            st.rerun()



# ─────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────
step = st.session_state.step

if step == 0:
    render_landing()
elif step == 1:
    render_basic_info()
elif step == 2:
    render_mbti()
elif step == 3:
    render_attachment_test()
elif step == 4:
    render_result()
