"""
GoldFX Pro v4.0 — AI-Powered Trading System
Main Streamlit Application Entry Point

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import re
import streamlit.components.v1 as components

# ── AI Engine (rule-based, no LLM) ──────────────────────────────────
# ── AI Engine (Rule-Based Engine) ──────────────────────────────────
# v4.1 Fix: Import from root ai_engine.py (enhanced with sl_mode)
# If not found, fallback to core.ai_engine
try:
    from ai_engine import analyze_dataframe, format_signal_block, generate_all_recommendations
except ImportError:
    from core.ai_engine import analyze_dataframe, format_signal_block, generate_all_recommendations

# ── Strategy Engines (16 engines) ───────────────────────────────────
# ملاحظة: الملفات موجودة في engines/ مباشرة (بدون technical/patterns)
from engines.ma_cross_engine import ma_cross_signal_for_backtest
from engines.macd_engine import macd_signal_for_backtest
from engines.ichimoku_engine import ichimoku_signal_for_backtest
from engines.bollinger_engine import bollinger_signal_for_backtest
from engines.pivot_engine import pivot_signal_for_backtest
from engines.market_structure import market_structure_signal_for_backtest
from engines.divergence_engine import divergence_signal_for_backtest
from engines.candlestick import candlestick_signal_for_backtest
from engines.volume import volume_signal_for_backtest
from engines.ict_engine import ict_signal_for_backtest
from engines.harmonic import harmonic_signal_for_backtest
from engines.gann_engine import gann_signal_for_backtest
from engines.smc_engine import smc_signal_for_backtest
from engines.elliott_engine import elliott_signal_for_backtest
from engines.rsi_engine import rsi_signal_for_backtest
from sentiment_engine import sentiment_signal_for_backtest

# ── Engine Comparator ───────────────────────────────────────────────
from engine_comparator import (
    run_engine_comparison,
    generate_comparison_summary,
    ENGINES,
)
from ui_engine_compare import render_engine_compare

# ── Live Recommendations (16-engine live analysis) ──────────────────
from live_recommendations import render_live_recommendations

# ── Neural Network Engine ───────────────────────────────────────────
from neural_engine import render_neural_engine

# ── Neural Recommendations Tab (شبكة عصبية + Ollama مدمج) ─────────
from ui_neural_tab import render_neural_recommendation_tab

# ── Trade Manager (Professional Order & Risk Management) ──────────
from trade_manager import (
    TradeManager, TradeOrder, OrderType, TradeStatus,
    TrailingMode, create_trade_order, render_trade_card,
    render_trade_summary_html, render_trade_panel_streamlit,
)

# Page config

# ═══ الملفات المفعلة تلقائياً (activate_valuable_files.py) ═══
# تاريخ التفعيل: 2026-05-12 20:18:13


# ── نظام التدريب والتعلم الذاتي ────────────────────────────
try:
    from self_learning.train_system import TrainSystem
    from self_learning.feedback_tracker import FeedbackTracker
    from self_learning.fine_tuner import FineTuner
    from self_learning.rag_engine import RAGEngine
    from self_learning.self_improver import SelfImprover
    HAS_SELF_LEARNING = True
except ImportError:
    HAS_SELF_LEARNING = False


# ── نظام القرار المركزي ─────────────────────────────────────
try:
    from decision.central_decision import CentralDecisionEngine
    from decision.decision_pipeline_v2 import DecisionPipelineV2
    from decision.risk_analyzer import RiskAnalyzer as DecisionRiskAnalyzer
    from decision.trade_validator import TradeValidator
    HAS_DECISION = True
except ImportError:
    HAS_DECISION = False

try:
    from decision.llm_decision_assistant import LLMDecisionAssistant
    HAS_LLM_ASSISTANT = True
except ImportError:
    HAS_LLM_ASSISTANT = False


# ── الدماغ والذكاء الاصطناعي ────────────────────────────────
try:
    from core.ai_brain import AIBrain
    HAS_AI_BRAIN = True
except ImportError:
    HAS_AI_BRAIN = False

try:
    from core.gold_master_brain import GoldMasterBrain
    HAS_GOLD_BRAIN = True
except ImportError:
    HAS_GOLD_BRAIN = False

try:
    from ai_bridge import AIBridge
    HAS_AI_BRIDGE = True
except ImportError:
    HAS_AI_BRIDGE = False


# ── نظام النماذج اللغوية ────────────────────────────────────
try:
    from core.llm_provider import LLMProvider
    from core.llm_analyst import LLMAnalyst
    from core.llm_config import LLM_CONFIG
    HAS_LLM_SYSTEM = True
except ImportError:
    HAS_LLM_SYSTEM = False

try:
    from llm.improved_ollama_engine import ImprovedOllamaEngine
    HAS_IMPROVED_OLLAMA = True
except ImportError:
    HAS_IMPROVED_OLLAMA = False


# ── محرك البيانات والميزات ──────────────────────────────────
try:
    from core.data_engine import DataEngine
    from core.feature_engine import FeatureEngine
    from core.multi_tf_manager import MultiTimeframeManager
    HAS_DATA_FEATURES = True
except ImportError:
    HAS_DATA_FEATURES = False


# ── إدارة المخاطر والأداء ───────────────────────────────────
try:
    from risk_analyzer import RiskAnalyzer
    from performance_analytics import PerformanceAnalytics
    from portfolio_manager import PortfolioManager
    HAS_RISK_PERF = True
except ImportError:
    HAS_RISK_PERF = False

try:
    from core.regime_detector import RegimeDetector
    HAS_REGIME = True
except ImportError:
    HAS_REGIME = False

try:
    from core.trade_journal import TradeJournal
    HAS_JOURNAL = True
except ImportError:
    HAS_JOURNAL = False


# ── واجهات Dashboard إضافية ─────────────────────────────────
try:
    from dashboard.ui_candlestick import render_candlestick_tab
    HAS_CANDLESTICK_TAB = True
except ImportError:
    HAS_CANDLESTICK_TAB = False

try:
    from dashboard.ui_correlation import render_correlation_tab
    HAS_CORRELATION_TAB = True
except ImportError:
    HAS_CORRELATION_TAB = False

try:
    from dashboard.ui_harmonic import render_harmonic_tab
    HAS_HARMONIC_TAB = True
except ImportError:
    HAS_HARMONIC_TAB = False

try:
    from dashboard.ui_journal import render_journal_tab
    HAS_JOURNAL_TAB = True
except ImportError:
    HAS_JOURNAL_TAB = False

try:
    from dashboard.ui_reports import render_reports_tab
    HAS_REPORTS_TAB = True
except ImportError:
    HAS_REPORTS_TAB = False

try:
    from dashboard.ui_execution import render_execution_tab
    HAS_EXECUTION_TAB = True
except ImportError:
    HAS_EXECUTION_TAB = False

try:
    from dashboard.ui_market_structure import render_market_structure_tab
    HAS_MARKET_STRUCT_TAB = True
except ImportError:
    HAS_MARKET_STRUCT_TAB = False

try:
    from dashboard.ui_price_patterns import render_price_patterns_tab
    HAS_PRICE_PATTERNS_TAB = True
except ImportError:
    HAS_PRICE_PATTERNS_TAB = False

try:
    from dashboard.ui_recommendations import render_recommendations_tab
    HAS_RECOMMENDATIONS_TAB = True
except ImportError:
    HAS_RECOMMENDATIONS_TAB = False


# ── محركات إضافية ───────────────────────────────────────────
try:
    from engines.correlation import correlation_signal_for_backtest
    from engines.sentiment_engine import sentiment_signal_for_backtest
    from engines.trend_engine import trend_signal_for_backtest
    from engines.volatility import volatility_signal_for_backtest
    from engines.volume_engine import volume_signal_for_backtest
    HAS_EXTRA_ENGINES = True
except ImportError:
    HAS_EXTRA_ENGINES = False


# ── التنفيذ وMT5 ────────────────────────────────────────────
try:
    from execution.mt5_connector import MT5Connector
    from execution_engine import ExecutionEngine
    HAS_EXECUTION = True
except ImportError:
    HAS_EXECUTION = False


# ── التقارير والإعدادات ─────────────────────────────────────
try:
    from reporting.report_engine import ReportEngine
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False

try:
    from core.settings import Settings
    HAS_SETTINGS = True
except ImportError:
    HAS_SETTINGS = False


# ── التحليل المتقدم ─────────────────────────────────────────
try:
    from core.sentiment_analyzer import SentimentAnalyzer
    from core.time_price_predictor import TimePricePredictor
    HAS_ADVANCED_ANALYSIS = True
except ImportError:
    HAS_ADVANCED_ANALYSIS = False

try:
    from core.backtest_ai import BacktestAI
    HAS_BACKTEST_AI = True
except ImportError:
    HAS_BACKTEST_AI = False


st.set_page_config(
    page_title="GoldFX Pro v4.0",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ═══ Global RTL + Font Fix ═══ */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
    .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        direction: rtl;
        text-align: right;
        unicode-bidi: embed;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', 'Cairo', sans-serif;
    }

    /* Mixed Arabic-English: force proper rendering */
    .stMarkdown p, .stMarkdown div {
        word-spacing: 2px;
        line-height: 1.8;
    }

    /* ═══ Tab Styling ═══ */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #0F1318;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #151A21;
        border-bottom: 2px solid #3B82F6;
    }

    /* ═══ Metric Cards ═══ */
    div[data-testid="stMetric"] {
        background: #0F1318;
        border: 1px solid #1C2230;
        border-radius: 8px;
        padding: 12px;
    }
    div[data-testid="stMetric"] label {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
        font-size: 12px;
        color: #6B7A8D;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        direction: ltr;
        text-align: center;
        font-family: 'SF Mono', 'Consolas', 'Fira Code', monospace;
        font-weight: 700;
        font-size: 17px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        direction: ltr;
        text-align: center;
    }

    /* ═══ Code blocks (prices/levels) ═══ */
    .stCodeBlock, .stCodeBlock code {
        font-family: 'SF Mono', 'Consolas', 'Fira Code', monospace !important;
        font-size: 13px !important;
        font-weight: 600;
        direction: ltr;
        text-align: center;
    }
    .stCodeBlock {
        background: #0F1318 !important;
        border: 1px solid #1C2230 !important;
        border-radius: 6px !important;
    }

    /* ═══ Sidebar RTL ═══ */
    .stSidebar .stMarkdown, .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown div {
        direction: rtl;
        text-align: right;
    }

    /* ═══ Caption (subtitle) ═══ */
    .stCaption, [data-testid="stCaption"] {
        direction: rtl;
        text-align: right;
        color: #6B7A8D;
        font-size: 11px;
    }

    /* ═══ Dataframe ═══ */
    .stDataFrame {
        direction: ltr;
    }

    /* ═══ Expander ═══ */
    .stExpander summary {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
    }

    /* ═══ Buttons ═══ */
    .stButton button {
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
        font-weight: 600;
    }

    /* ═══ Slider Labels ═══ */
    .stSlider label {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
    }

    /* ═══ Info/Warning/Error boxes ═══ */
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
    }

    /* ═══ Radio buttons ═══ */
    .stRadio label {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif;
    }

    /* ═══ Number input ═══ */
    .stNumberInput label {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: Mode Selector & Settings ───────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ GoldFX Pro v4.0")
    st.markdown("---")

    # Trading Mode Selector
    try:
        from core.signal_engine import TRADING_MODES, set_trading_mode, get_mode_config
    except ImportError:
        TRADING_MODES = {
            "conservative":{"name":"محافظ","name_en":"Conservative","emoji":"🛡️","desc":"إشارات عالية الثقة","min_conf":0.60,"min_rr":2.0,"market_threshold":0.55,"limit_threshold":0.45,"stop_threshold":0.50,"bias_threshold":0.40,"min_analysts_agree":6,"require_volume":True,"require_htf_align":True},
            "moderate":{"name":"متوازن","name_en":"Moderate","emoji":"⚖️","desc":"توازن","min_conf":0.35,"min_rr":1.5,"market_threshold":0.35,"limit_threshold":0.25,"stop_threshold":0.30,"bias_threshold":0.25,"min_analysts_agree":4,"require_volume":False,"require_htf_align":False},
            "aggressive":{"name":"عدواني","name_en":"Aggressive","emoji":"⚡","desc":"أقصى إشارات","min_conf":0.15,"min_rr":1.2,"market_threshold":0.15,"limit_threshold":0.10,"stop_threshold":0.12,"bias_threshold":0.10,"min_analysts_agree":2,"require_volume":False,"require_htf_align":False},
            "manual":{"name":"يدوي","name_en":"Manual","emoji":"🎛️","desc":"تحكم كامل","min_conf":0.30,"min_rr":1.5,"market_threshold":0.30,"limit_threshold":0.25,"stop_threshold":0.25,"bias_threshold":0.20,"min_analysts_agree":3,"require_volume":False,"require_htf_align":False},
        }
        def set_trading_mode(m): pass
        def get_mode_config(): return TRADING_MODES["moderate"]

    st.markdown("### 🎯 وضع التداول")
    mode_keys = list(TRADING_MODES.keys())
    mode_labels = [f"{TRADING_MODES[k]['emoji']} {TRADING_MODES[k]['name']} ({TRADING_MODES[k]['name_en']})" for k in mode_keys]

    if "trading_mode" not in st.session_state:
        st.session_state["trading_mode"] = "moderate"

    # Normalize to lowercase
    current_mode = st.session_state["trading_mode"].lower()
    if current_mode not in mode_keys:
        current_mode = "moderate"
    st.session_state["trading_mode"] = current_mode

    selected_mode_idx = st.radio(
        "اختر الوضع:",
        options=range(len(mode_keys)),
        format_func=lambda i: mode_labels[i],
        index=mode_keys.index(st.session_state["trading_mode"]),
        key="mode_radio",
    )

    selected_mode = mode_keys[selected_mode_idx]
    if selected_mode != st.session_state["trading_mode"]:
        st.session_state["trading_mode"] = selected_mode
        set_trading_mode(selected_mode)

    mode_cfg = get_mode_config()
    st.caption(f"📝 {mode_cfg['desc']}")

    # ── Manual Mode: Custom Indicator Sliders ───────────────────
    if selected_mode == "manual":
        st.markdown("---")
        st.markdown("### 🎛️ تحكم يدوي في المؤشرات")

        manual_min_conf = st.slider(
            "📊 الحد الأدنى للثقة %", 5, 90,
            int(mode_cfg["min_conf"] * 100), 5, key="manual_min_conf"
        ) / 100

        manual_min_rr = st.slider(
            "📐 الحد الأدنى لـ R:R", 1.0, 3.0,
            mode_cfg["min_rr"], 0.1, key="manual_min_rr"
        )

        manual_market = st.slider(
            "🟢 عتبة أمر الماركت %", 10, 80,
            int(mode_cfg["market_threshold"] * 100), 5, key="manual_market"
        ) / 100

        manual_limit = st.slider(
            "🔵 عتبة أمر الليمت %", 10, 80,
            int(mode_cfg["limit_threshold"] * 100), 5, key="manual_limit"
        ) / 100

        manual_stop = st.slider(
            "🟦 عتبة أمر الستوب %", 10, 80,
            int(mode_cfg["stop_threshold"] * 100), 5, key="manual_stop"
        ) / 100

        manual_bias = st.slider(
            "📈 عتبة تحديد الاتجاه %", 10, 60,
            int(mode_cfg["bias_threshold"] * 100), 5, key="manual_bias"
        ) / 100

        manual_analysts = st.slider(
            "🧠 عدد المحللين المتفقين (من 10)", 1, 10,
            mode_cfg["min_analysts_agree"], 1, key="manual_analysts"
        )

        manual_vol = st.checkbox(
            "📊 يشترط تأكيد الفوليوم",
            value=mode_cfg["require_volume"], key="manual_vol"
        )

        manual_htf = st.checkbox(
            "📈 يشترط توافق الإطار الأعلى",
            value=mode_cfg["require_htf_align"], key="manual_htf"
        )

        # Apply manual overrides
        # TRADING_MODES already loaded above
        TRADING_MODES["manual"].update({
            "min_conf":           manual_min_conf,
            "min_rr":             manual_min_rr,
            "market_threshold":   manual_market,
            "limit_threshold":    manual_limit,
            "stop_threshold":     manual_stop,
            "bias_threshold":     manual_bias,
            "min_analysts_agree": manual_analysts,
            "require_volume":     manual_vol,
            "require_htf_align":  manual_htf,
        })

        st.caption(f"✅ تم تطبيق الإعدادات المخصصة")
    else:
        st.caption(f"📊 الحد الأدنى للثقة: {mode_cfg['min_conf']:.0%} | الحد الأدنى لـ R:R: {mode_cfg['min_rr']}")

    st.markdown("---")

    from dashboard.ui_training import render_mode_selector
    render_mode_selector()

    st.markdown("---")

    # Account Settings
    st.markdown("### 💰 Account")
    st.session_state["account_size"] = st.number_input(
        "Account Size ($)", 100, 1_000_000, 10_000, 100, key="sidebar_account"
    )
    st.session_state["risk_pct"] = st.slider(
        "Risk % per Trade", 0.1, 5.0, 1.0, 0.1, key="sidebar_risk"
    )

    st.markdown("---")
    st.caption("GoldFX Pro v4.0 — AI Trading Ecosystem")
    st.caption("10 Analysts + AI Brain + Smart Modes")

    # Engine status
    st.markdown("---")
    st.markdown("### 🔧 حالة المحركات")
    st.success("🧠 Rule-Based Engine متصل")
    st.caption("16 محرك تحليل + شبكة عصبية:")
    st.caption("✖️ MA | 📉 MACD | ☁️ Ichimoku | 📊 Bollinger | 📊 RSI")
    st.caption("🔴 Pivot | 🏗️ Structure | 🔀 Divergence | 🕯️ Candlestick")
    st.caption("📈 Volume | 🎯 ICT | 🦋 Harmonic | 📐 Gann")
    st.caption("🏦 SMC | 🌊 Elliott | 🎭 المشاعر | 🧠 Neural Net")


# ── Main Tabs — مرتبة بشكل احترافي ومجمّعة ─────────────────────────
# ══════════════════════════════════════════════════════════════════════
#  1-لوحة التحكم  2-الإشارات  3-التحليل الشامل  4-الذكاء الاصطناعي
#  5-التحليل المتقدم  6-إدارة التداول  7-الإعدادات
# ══════════════════════════════════════════════════════════════════════
(
    # ── 1. لوحة التحكم ──
    tab_dashboard,
    tab_scanner,
    # ── 2. الإشارات والتوصيات ──
    tab_signals,
    # ── 3. التحليل الشامل ──
    tab_smc,
    tab_elliott,
    tab_gann,
    # ── 4. الذكاء الاصطناعي ──
    tab_ai,
    tab_smart,
    tab_brain,
    tab_ollama,
    tab_llm,
    # ── 5. التحليل المتقدم ──
    tab_predictor,
    tab_astrology,
    # ── 6. مقارنة المحركات ──
    tab_engine_compare,
    # ── 7. التوصيات اللحظية ──
    tab_live_rec,
    # ── 8. الشبكة العصبية ──
    tab_neural,
    # ── 9. AI Master Strategy ──
    tab_master_strategy,
    # ── 10. إدارة التداول ──
    tab_backtest,
    tab_training,
    tab_perf,
    tab_news,
    tab_alerts,
    # ── 8. النظام ──
    tab_mt5,
    tab_system,
    # ── 9. إدارة الصفقات الاحترافية ──
    tab_trade_mgr,
    # ── 10. تبويبات إضافية ──
    tab_training_new,
    tab_decision,
    tab_dashboard_ui,
) = st.tabs([
    # ── 1. لوحة التحكم ──
    "📊 لوحة التحكم",
    "🔭 الماسح الضوئي",
    # ── 2. الإشارات ──
    "🎯 إشارات التداول",
    # ── 3. التحليل الشامل ──
    "🏦 SMC التحليل الشامل",
    "🌊 موجات إليوت",
    "📐 جان",
    # ── 4. الذكاء الاصطناعي ──
    "🤖 رؤى الذكاء الاصطناعي",
    "🧠 التحليل الذكي",
    "🧠 الدماغ الذكي",
    "🦙 Ollama",
    "⚙️ إعدادات LLM",
    # ── 5. التحليل المتقدم ──
    "🔮 تنبؤ الاتجاه",
    "⭐ التحليل الفلكي",
    # ── 6. مقارنة المحركات ──
    "⚔️ مقارنة المحركات",
    # ── 7. التوصيات اللحظية ──
    "🎯 التوصيات اللحظية",
    # ── 8. الشبكة العصبية ──
    "🧠 الشبكة العصبية",
    # ── 9. AI Master Strategy ──
    "🧠 AI Master Strategy",
    # ── 10. إدارة التداول ──
    "📈 الاختبار الخلفي",
    "🏋️ التدريب",
    "📊 الأداء",
    "📰 الأخبار",
    "🔔 التنبيهات",
    # ── 8. النظام ──
    "🔌 MT5",
    "🏥 حالة النظام",
    # ── 9. إدارة الصفقات الاحترافية ──
    "📋 إدارة الصفقات",
    "🎓 التدريب والتحسين",
    "🎯 نظام القرار",
    "📊 تحليلات إضافية",
])


# ══════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS  (replaces old Ollama pipeline)
# ══════════════════════════════════════════════════════════════════════

def safe_html(html_content: str, height: int = None):
    """عرض HTML بشكل آمن مع دعم كامل للغة العربية وRTL

    يستخدم streamlit.components.v1.html بدلاً من st.markdown
    لتجنب مشاكل direction في Streamlit markdown renderer
    """
    # Wrap in a div with explicit RTL support
    wrapped = f'<div style="direction:rtl;unicode-bidi:plaintext;width:100%;">{html_content}</div>'
    components.html(wrapped, height=height, scrolling=False)

def price_card(label: str, value: float, color: str = "#D1D9E6", border: str = "#1C2230"):
    """عرض سعر بشكل نظيف بدل st.code"""
    return f"""
    <div style="background:#0F1318;border:1px solid {border};
    border-radius:6px;padding:8px 12px;margin-bottom:4px;
    text-align:center;direction:ltr">
        <div style="color:#4A5568;font-size:10px;margin-bottom:2px">{label}</div>
        <span style="color:{color};font-family:'SF Mono',monospace;
        font-weight:700;font-size:14px">{value}</span>
    </div>
    """


def metric_label_ar(english_label: str) -> str:
    """ترجمة الليبلات الشائعة للعربي"""
    translations = {
        "Entry": "سعر الدخول",
        "Stop Loss": "وقف الخسارة",
        "Take Profit": "جني الأرباح",
        "Trend": "الاتجاه",
        "Trend Strength": "قوة الاتجاه",
        "Confidence": "الثقة",
        "Support Levels": "مستويات الدعم",
        "Resistance Levels": "مستويات المقاومة",
    }
    return translations.get(english_label, english_label)

def display_analysis(result: dict):
    """Render multi-timeframe analysis — clean institutional layout."""

    summary = result["summary"]
    st.markdown(f"### 📊 تحليل السوق — {summary['base_timeframe']}")
    st.caption(f"آخر سعر: {summary['current_price']} | الأطر: {', '.join(summary['analyzed_timeframes'])} | إشارات: {summary['total_signals']}")

    tfs = result["timeframes"]
    signals = result["signals"]

    # ── Per-timeframe detail cards ──
    for tf_label, data in tfs.items():
        trend_color = "#22C55E" if data["trend"] == "bullish" else ("#EF4444" if data["trend"] == "bearish" else "#F59E0B")
        trend_arrow = "▲" if data["trend"] == "bullish" else ("▼" if data["trend"] == "bearish" else "●")
        rsi_val = data["rsi"]
        rsi_color = "#EF4444" if data["rsi_signal"] == "overbought" else ("#22C55E" if data["rsi_signal"] == "oversold" else "#F59E0B")

        with st.expander(f"📈 {tf_label} — {data['trend'].upper()} (RSI: {rsi_val})", expanded=True):
            # Compact metrics row
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:8px">
                <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الاتجاه</div>
                    <div style="color:{trend_color};font-size:14px;font-weight:700">{trend_arrow} {data['trend']}</div>
                </div>
                <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">RSI</div>
                    <div style="color:{rsi_color};font-size:14px;font-weight:700">{rsi_val}</div>
                </div>
                <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">ATR</div>
                    <div style="color:#D1D9E6;font-size:14px;font-weight:700">{data['atr']:.4f}</div>
                </div>
                <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">قوة الاتجاه</div>
                    <div style="color:#D1D9E6;font-size:14px;font-weight:700">{data['trend_strength']:.0%}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # S/R — compact inline
            if data["support_levels"] or data["resistance_levels"]:
                sups_str = " · ".join(f"{s:.4f}" for s in data["support_levels"][:3]) or "—"
                ress_str = " · ".join(f"{r:.4f}" for r in data["resistance_levels"][:3]) or "—"
                st.markdown(f"""
            <div style="display:flex;gap:8px;margin-bottom:8px">
                <div style="flex:1;background:#22C55E0A;border:1px solid #22C55E20;border-radius:6px;padding:6px 10px;text-align:center;direction:ltr">
                    <span style="color:#4A5568;font-size:10px">SUPPORT </span>
                    <span style="color:#22C55E;font-family:monospace;font-weight:600;font-size:12px">{sups_str}</span>
                </div>
                <div style="flex:1;background:#EF44440A;border:1px solid #EF444420;border-radius:6px;padding:6px 10px;text-align:center;direction:ltr">
                    <span style="color:#4A5568;font-size:10px">RESIST </span>
                    <span style="color:#EF4444;font-family:monospace;font-weight:600;font-size:12px">{ress_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Signal for this timeframe
            sig = data.get("signal")
            if sig:
                is_buy = "Buy" in sig["trade_type"]
                sig_color = "#22C55E" if is_buy else "#EF4444"
                sig_arrow = "▲" if is_buy else "▼"
                conf_pct = int(sig["confidence"] * 100)
                conf_color = "#22C55E" if conf_pct >= 60 else ("#F59E0B" if conf_pct >= 35 else "#EF4444")

                st.markdown(f"""
                <div style="background:#0F1318;border:1px solid #1C2230;border-right:3px solid {sig_color};
                border-radius:6px;padding:12px 16px;margin-top:8px">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                        <div style="display:flex;align-items:center;gap:6px">
                            <span style="color:{sig_color};font-size:14px">{sig_arrow}</span>
                            <span style="color:{sig_color};font-size:14px;font-weight:700">{sig['trade_type']}</span>
                        </div>
                        <span style="color:{conf_color};font-size:12px;font-weight:600">{conf_pct}%</span>
                    </div>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px">
                        <div style="text-align:center">
                            <div style="color:#4A5568;font-size:9px;text-transform:uppercase">الدخول</div>
                            <div style="color:#D1D9E6;font-family:monospace;font-size:13px;font-weight:700">{sig['entry_price']:.4f}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="color:#4A5568;font-size:9px;text-transform:uppercase">الوقف</div>
                            <div style="color:#EF4444;font-family:monospace;font-size:13px;font-weight:700">{sig['stop_loss']:.4f}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="color:#4A5568;font-size:9px;text-transform:uppercase">الهدف</div>
                            <div style="color:#22C55E;font-family:monospace;font-size:13px;font-weight:700">{sig['take_profit']:.4f}</div>
                        </div>
                    </div>
                    <div style="color:#6B7A8D;font-size:11px;margin-top:6px">{sig.get('reason', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption("🚫 لا توجد فرصة واضحة لهذا الإطار")

    # ── Signal summary table ──
    if signals:
        st.markdown("### 📋 ملخص الإشارات")
        rows = []
        for s in signals:
            rows.append({
                "الفريم": s["timeframe"],
                "الاستراتيجية": s["strategy"],
                "النوع": s["trade_type"],
                "الدخول": f"{s['entry_price']:.4f}",
                "SL": f"{s['stop_loss']:.4f}",
                "TP": f"{s['take_profit']:.4f}",
                "الثقة": f"{int(s['confidence'] * 100)}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("🚫 لا توجد إشارات تداول حالياً")


def display_all_recommendations(result: dict):
    """Render comprehensive recommendations — clean institutional layout."""

    tf = result.get("timeframe", "H1")
    st.markdown(f"## 🎯 جميع التوصيات — {tf}")

    recs = result.get("recommendations", [])
    if not recs:
        st.warning("لا توجد توصيات حالياً")
        return

    # ── Context Bar — single compact row ──
    trend = result["trend"]
    trend_color = "#22C55E" if trend == "bullish" else ("#EF4444" if trend == "bearish" else "#F59E0B")
    trend_arrow = "▲" if trend == "bullish" else ("▼" if trend == "bearish" else "●")
    rsi_val = result.get("rsi", 0)
    rsi_signal = result.get("rsi_signal", "")
    rsi_color = "#EF4444" if rsi_signal == "overbought" else "#22C55E" if rsi_signal == "oversold" else "#F59E0B"

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:12px">
        <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
            <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الاتجاه</div>
            <div style="color:{trend_color};font-size:15px;font-weight:700">{trend_arrow} {trend.upper()}</div>
        </div>
        <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
            <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">RSI</div>
            <div style="color:{rsi_color};font-size:15px;font-weight:700">{rsi_val} ({rsi_signal})</div>
        </div>
        <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
            <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">ATR</div>
            <div style="color:#D1D9E6;font-size:15px;font-weight:700">{result['atr']:.4f}</div>
        </div>
        <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
            <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">قوة الاتجاه</div>
            <div style="color:#D1D9E6;font-size:15px;font-weight:700">{result['trend_strength']:.0%}</div>
        </div>
        <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
            <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">السعر</div>
            <div style="color:#D1D9E6;font-size:15px;font-weight:700">{result['current_price']:.4f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # S/R — compact inline
    if result.get("support_levels") or result.get("resistance_levels"):
        sups_str = " · ".join(f"{s:.4f}" for s in result.get("support_levels", [])[:3]) or "—"
        ress_str = " · ".join(f"{r:.4f}" for r in result.get("resistance_levels", [])[:3]) or "—"
        st.markdown(f"""
    <div style="display:flex;gap:8px;margin-bottom:12px">
        <div style="flex:1;background:#22C55E0A;border:1px solid #22C55E20;border-radius:6px;padding:6px 10px;text-align:center;direction:ltr">
            <span style="color:#4A5568;font-size:10px">SUPPORT </span>
            <span style="color:#22C55E;font-family:monospace;font-weight:600;font-size:12px">{sups_str}</span>
        </div>
        <div style="flex:1;background:#EF44440A;border:1px solid #EF444420;border-radius:6px;padding:6px 10px;text-align:center;direction:ltr">
            <span style="color:#4A5568;font-size:10px">RESIST </span>
            <span style="color:#EF4444;font-family:monospace;font-weight:600;font-size:12px">{ress_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Recommendation Cards — clean ──
    for rec in recs:
        icon = rec["icon"]
        rtype = rec["type"]
        conf = rec["confidence"]
        conf_pct = int(conf * 100)

        if "BUY" in rtype:
            card_color = "#22C55E"
            arrow = "▲"
        elif "SELL" in rtype:
            card_color = "#EF4444"
            arrow = "▼"
        else:
            card_color = "#F59E0B"
            arrow = "●"

        bar_color = "#22C55E" if conf_pct >= 60 else ("#F59E0B" if conf_pct >= 40 else "#EF4444")

        st.markdown(f"""
        <div style="background:#0F1318;border:1px solid #1C2230;border-right:3px solid {card_color};
        border-radius:8px;padding:16px 20px;margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="font-size:16px;color:{card_color}">{arrow}</span>
                    <span style="color:{card_color};font-size:16px;font-weight:700">{rtype}</span>
                    <span style="color:#4A5568;font-size:12px">{icon}</span>
                </div>
                <div style="background:{bar_color}18;border:1px solid {bar_color}30;border-radius:4px;padding:4px 10px">
                    <span style="color:{bar_color};font-size:13px;font-weight:700">{conf_pct}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if rec["entry"] is not None:
            risk = abs(rec["entry"] - rec["sl"]) if rec["sl"] else 0
            rr1 = round(abs(rec["tp1"] - rec["entry"]) / max(risk, 0.0001), 2) if rec["tp1"] else 0
            rr2 = round(abs(rec["tp2"] - rec["entry"]) / max(risk, 0.0001), 2) if rec["tp2"] else 0
            rr3 = round(abs(rec["tp3"] - rec["entry"]) / max(risk, 0.0001), 2) if rec["tp3"] else 0

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:8px">
                <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الدخول</div>
                    <div style="color:#D1D9E6;font-family:monospace;font-size:14px;font-weight:700">{rec['entry']:.5f}</div>
                </div>
                <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الوقف</div>
                    <div style="color:#EF4444;font-family:monospace;font-size:14px;font-weight:700">{rec['sl']:.5f}</div>
                </div>
                <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP1</div>
                    <div style="color:#22C55E;font-family:monospace;font-size:14px;font-weight:700">{rec['tp1']:.5f}</div>
                </div>
                <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP2</div>
                    <div style="color:#22C55E;font-family:monospace;font-size:14px;font-weight:700">{rec['tp2']:.5f}</div>
                </div>
                <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                    <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP3</div>
                    <div style="color:#22C55E;font-family:monospace;font-size:14px;font-weight:700">{rec['tp3']:.5f}</div>
                </div>
            </div>
            <div style="display:flex;gap:16px;direction:ltr">
                <span style="color:#6B7A8D;font-size:11px">R:R → <b style="color:#D1D9E6">1:{rr1}</b> · <b style="color:#D1D9E6">1:{rr2}</b> · <b style="color:#D1D9E6">1:{rr3}</b></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="color:#6B7A8D;font-size:12px;padding:8px 0">⏳ لا يوجد سعر دخول — الوضع محايد</div>
            """, unsafe_allow_html=True)

        # Reason
        st.markdown(f"""
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid #1C2230">
            <span style="color:#6B7A8D;font-size:11px">{rec['reason']}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    #  PLAN B
    # ══════════════════════════════════════════════════════════════
    _render_plan_b_from_recs(recs, result)


def _render_plan_b_from_recs(recs, result):
    """Plan B — compact alternative scenario."""
    if not recs:
        return

    main_rec = next((r for r in recs if r.get("entry") is not None), None)
    if not main_rec:
        return

    price = result.get("current_price", 0)
    atr = result.get("atr", 0)
    supports = result.get("support_levels", []) or []
    resistances = result.get("resistance_levels", []) or []

    rtype = main_rec["type"]
    is_buy = "BUY" in rtype

    if is_buy:
        rev_dir = "SELL"
        rev_color = "#EF4444"
        sl_level = main_rec["sl"]
        entry_b = sl_level + atr * 0.2 if sl_level else price
        sl_b = entry_b + atr * 1.5
        tp1_b = entry_b - atr * 2.0
        tp2_b = entry_b - atr * 3.5
        tp3_b = entry_b - atr * 5.0
    else:
        rev_dir = "BUY"
        rev_color = "#22C55E"
        sl_level = main_rec["sl"]
        entry_b = sl_level - atr * 0.2 if sl_level else price
        sl_b = entry_b - atr * 1.5
        tp1_b = entry_b + atr * 2.0
        tp2_b = entry_b + atr * 3.5
        tp3_b = entry_b + atr * 5.0

    if not sl_level:
        return

    entry_b = float(f"{entry_b:.4f}")
    sl_b = float(f"{sl_b:.4f}")
    tp1_b = float(f"{tp1_b:.4f}")
    tp2_b = float(f"{tp2_b:.4f}")
    tp3_b = float(f"{tp3_b:.4f}")
    risk_b = abs(entry_b - sl_b)
    rr1 = round(abs(tp1_b - entry_b) / max(risk_b, 0.01), 2)
    rr2 = round(abs(tp2_b - entry_b) / max(risk_b, 0.01), 2)
    rr3 = round(abs(tp3_b - entry_b) / max(risk_b, 0.01), 2)

    # Reversal type
    if is_buy:
        nearest_support = min(supports, key=lambda s: abs(s - sl_level)) if supports else None
        if nearest_support and abs(nearest_support - sl_level) < atr * 0.5:
            reversal_desc = f"كسر الدعم {sl_level:.4f} → إعادة اختبار كمقاومة"
        else:
            reversal_desc = f"كسر بقوة تحت {sl_level:.4f} → تغير هيكل هبوطي"
    else:
        nearest_resist = min(resistances, key=lambda r: abs(r - sl_level)) if resistances else None
        if nearest_resist and abs(nearest_resist - sl_level) < atr * 0.5:
            reversal_desc = f"كسر المقاومة {sl_level:.4f} → إعادة اختبار كدعم"
        else:
            reversal_desc = f"كسر بقوة فوق {sl_level:.4f} → تغير هيكل صعودي"

    st.markdown(f"""
    <div style="background:#0F1318;border:1px solid #1C2230;border-right:3px solid {rev_color};
    border-radius:8px;padding:16px 20px;margin:12px 0">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:8px">
                <span style="color:{rev_color};font-size:14px">{'▼' if rev_dir=='SELL' else '▲'}</span>
                <span style="color:{rev_color};font-size:14px;font-weight:700">Plan B: {rev_dir}</span>
                <span style="color:#4A5568;font-size:11px">(عكس Plan A)</span>
            </div>
            <span style="color:#F59E0B;font-size:12px;font-weight:600">35%</span>
        </div>
        <div style="color:#6B7A8D;font-size:11px;margin-bottom:10px">{reversal_desc}</div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:6px">
            <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الدخول</div>
                <div style="color:#D1D9E6;font-family:monospace;font-size:13px;font-weight:700">{entry_b}</div>
            </div>
            <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">الوقف</div>
                <div style="color:#EF4444;font-family:monospace;font-size:13px;font-weight:700">{sl_b}</div>
            </div>
            <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP1</div>
                <div style="color:#22C55E;font-family:monospace;font-size:13px;font-weight:700">{tp1_b}</div>
            </div>
            <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP2</div>
                <div style="color:#22C55E;font-family:monospace;font-size:13px;font-weight:700">{tp2_b}</div>
            </div>
            <div style="background:#151A21;border:1px solid #1C2230;border-radius:6px;padding:8px;text-align:center">
                <div style="color:#4A5568;font-size:9px;text-transform:uppercase;margin-bottom:3px">TP3</div>
                <div style="color:#22C55E;font-family:monospace;font-size:13px;font-weight:700">{tp3_b}</div>
            </div>
        </div>
        <div style="display:flex;gap:16px;margin-top:6px;direction:ltr">
            <span style="color:#6B7A8D;font-size:10px">R:R → <b style="color:#D1D9E6">1:{rr1}</b> · <b style="color:#D1D9E6">1:{rr2}</b> · <b style="color:#D1D9E6">1:{rr3}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


#  TAB RENDERERS
# ══════════════════════════════════════════════════════════════════════

with tab_dashboard:
    from dashboard.ui_upload import render_upload
    from dashboard.ui_dashboard import render_dashboard

    # Upload section (collapsed by default if data exists)
    if st.session_state.get("uploaded_data") is None:
        render_upload()
    else:
        with st.expander("📁 Upload / Manage Data", expanded=False):
            render_upload()
        render_dashboard()

    # ── AI Market Analysis (Rule-Based Engine) ──────────────────
    st.markdown("---")
    st.markdown("### 🤖 توصيات التداول — محرك التحليل")
    st.caption("RSI + Trend + Support/Resistance + ATR — بدون LLM")

    csv_file = st.file_uploader("ارفع ملف CSV (OHLCV)", type=["csv"], key="engine_csv_upload")

    if csv_file is not None:
        ai_df = pd.read_csv(csv_file)
        # ✅ FIX: لا نحول الأعمدة لصغيرة — ai_engine فيه _normalize_columns يعالجها
        st.dataframe(ai_df.tail(10), use_container_width=True)

        lookback = st.slider(
            "عدد الشموع للتحليل", 20, 200, 60, 5, key="engine_lookback"
        )

        if st.button("🔍 تحليل السوق", key="engine_analyze_btn"):
            with st.spinner("جاري التحليل..."):
                sl_mode = st.session_state.get("sl_mode", "hybrid")
            result = analyze_dataframe(ai_df, lookback=lookback, sl_mode=sl_mode)
            tf_label = "H1"
            trend = result.get("trend", {})
            sr = result.get("support_resistance", {})
            sig_data = None
            if result.get("signal") and result["signal"] != "WAIT":
                sig_data = {
                    "trade_type": "Buy" if result["signal"] == "BUY" else "Sell",
                    "confidence": result.get("confidence", 50) / 100,
                    "entry_price": result.get("entry", 0),
                    "stop_loss": result.get("sl", 0),
                    "take_profit": result.get("tp1", 0),
                    "reason": " | ".join(result.get("reasons", [])),
                    "timeframe": tf_label,
                    "strategy": "AI Engine",
                }
            wrapped = {
                "summary": {
                    "base_timeframe": tf_label,
                    "current_price": result.get("current_price", 0),
                    "analyzed_timeframes": [tf_label],
                    "total_signals": 1 if sig_data else 0,
                },
                "timeframes": {
                    tf_label: {
                        "trend": trend.get("trend", "neutral").lower(),
                        "rsi": result.get("rsi", 0),
                        "rsi_signal": "overbought" if result.get("rsi", 50) > 70 else ("oversold" if result.get("rsi", 50) < 30 else "neutral"),
                        "atr": result.get("atr", 0),
                        "trend_strength": trend.get("strength", 0) / 100,
                        "support_levels": sr.get("support", []),
                        "resistance_levels": sr.get("resistance", []),
                        "signal": sig_data,
                    },
                },
                "signals": [sig_data] if sig_data else [],
            }
            display_analysis(wrapped)

            # ── Comprehensive Recommendations ───────────────────
            st.markdown("---")
            rec_result = generate_all_recommendations(ai_df.tail(lookback), sl_mode=sl_mode)
            display_all_recommendations(rec_result)

            # ════════════════════════════════════════════════════════
            #  MULTI-ENGINE ANALYSIS — تشغيل جميع المحركات الـ14
            # ════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### ⚔️ تحليل شامل — جميع المحركات (14 محرك)")
            st.caption("كل محرك يحلل البيانات بشكل مستقل — النتيجة تجمع بينهم لقرار أقوى")

            engine_window = ai_df.tail(lookback).copy()
            engine_window.columns = [c.strip().capitalize() for c in engine_window.columns]
            for col in ("Open", "High", "Low", "Close"):
                if col in engine_window.columns:
                    engine_window[col] = pd.to_numeric(engine_window[col], errors="coerce")
            engine_window.dropna(subset=["Open", "High", "Low", "Close"], inplace=True)

            # All 16 engines
            all_engines = {
                "ma_cross":     {"func": ma_cross_signal_for_backtest,     "name": "تقاطع المتوسطات",   "icon": "✖️"},
                "macd":         {"func": macd_signal_for_backtest,         "name": "MACD",              "icon": "📉"},
                "ichimoku":     {"func": ichimoku_signal_for_backtest,     "name": "إيشيموكو",          "icon": "☁️"},
                "bollinger":    {"func": bollinger_signal_for_backtest,    "name": "بولينجر باندز",     "icon": "📊"},
                "pivot":        {"func": pivot_signal_for_backtest,        "name": "نقاط البيفوت",      "icon": "🔴"},
                "market_structure": {"func": market_structure_signal_for_backtest, "name": "هيكل السوق", "icon": "🏗️"},
                "divergence":   {"func": divergence_signal_for_backtest,   "name": "الديفرجنس",         "icon": "🔀"},
                "candlestick":  {"func": candlestick_signal_for_backtest,  "name": "أنماط الشموع",      "icon": "🕯️"},
                "volume":       {"func": volume_signal_for_backtest,       "name": "تحليل الفوليوم",    "icon": "📈"},
                "ict":          {"func": ict_signal_for_backtest,          "name": "ICT",               "icon": "🎯"},
                "harmonic":     {"func": harmonic_signal_for_backtest,     "name": "هارمونيك",          "icon": "🦋"},
                "gann":         {"func": gann_signal_for_backtest,         "name": "جان",               "icon": "📐"},
                "smc":          {"func": smc_signal_for_backtest,          "name": "SMC",               "icon": "🏦"},
                "elliott":      {"func": elliott_signal_for_backtest,      "name": "موجات إليوت",       "icon": "🌊"},
                "rsi":          {"func": rsi_signal_for_backtest,          "name": "RSI",               "icon": "📊"},
                "sentiment":    {"func": sentiment_signal_for_backtest,    "name": "مؤشر المشاعر",      "icon": "🎭"},
            }

            if st.button("🚀 تحليل جميع المحركات", key="all_engines_btn", type="primary", use_container_width=True):
                results = []
                buy_votes = 0
                sell_votes = 0
                neutral_votes = 0
                total_conf = 0.0

                for eng_key, eng_info in all_engines.items():
                    try:
                        r = eng_info["func"](engine_window, tf="H1")
                        sig = r.get("signal", 0)
                        conf = r.get("confidence", 0.0)
                        atr = r.get("atr", 0.0)
                        price = r.get("last_close", 0.0)

                        if sig == 1:
                            buy_votes += 1
                            direction = "🟢 شراء"
                            direction_color = "#22C55E"
                        elif sig == -1:
                            sell_votes += 1
                            direction = "🔴 بيع"
                            direction_color = "#EF4444"
                        else:
                            neutral_votes += 1
                            direction = "⚪ محايد"
                            direction_color = "#6B7A8D"

                        total_conf += conf

                        results.append({
                            "المحرك": f"{eng_info['icon']} {eng_info['name']}",
                            "key": eng_key,
                            "الإشارة": direction,
                            "direction_color": direction_color,
                            "signal": sig,
                            "الثقة": f"{int(conf * 100)}%",
                            "conf_val": conf,
                            "ATR": f"{atr:.5f}" if atr else "—",
                            "السعر": f"{price:.5f}" if price else "—",
                        })
                    except Exception as e:
                        results.append({
                            "المحرك": f"{eng_info['icon']} {eng_info['name']}",
                            "key": eng_key,
                            "الإشارة": "⚠️ خطأ",
                            "direction_color": "#F97316",
                            "signal": 0,
                            "الثقة": "—",
                            "conf_val": 0,
                            "ATR": "—",
                            "السعر": "—",
                        })

                # ── Vote Summary — compact ──
                st.markdown("#### 🗳️ ملخص التصويت")

                total_engines = len(results)
                avg_conf = total_conf / max(total_engines, 1)

                st.markdown(f"""
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:12px">
                    <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
                        <div style="color:#22C55E;font-size:20px;font-weight:700">{buy_votes}</div>
                        <div style="color:#4A5568;font-size:10px">شراء</div>
                    </div>
                    <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
                        <div style="color:#EF4444;font-size:20px;font-weight:700">{sell_votes}</div>
                        <div style="color:#4A5568;font-size:10px">بيع</div>
                    </div>
                    <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
                        <div style="color:#F59E0B;font-size:20px;font-weight:700">{neutral_votes}</div>
                        <div style="color:#4A5568;font-size:10px">محايد</div>
                    </div>
                    <div style="background:#0F1318;border:1px solid #1C2230;border-radius:6px;padding:10px;text-align:center">
                        <div style="color:#D1D9E6;font-size:20px;font-weight:700">{int(avg_conf * 100)}%</div>
                        <div style="color:#4A5568;font-size:10px">متوسط الثقة</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Overall verdict
                if buy_votes > sell_votes and buy_votes >= 5:
                    st.success(f"▲ قرار جماعي: شراء — {buy_votes}/{total_engines}")
                    overall = "BUY"
                elif sell_votes > buy_votes and sell_votes >= 5:
                    st.error(f"▼ قرار جماعي: بيع — {sell_votes}/{total_engines}")
                    overall = "SELL"
                elif buy_votes > sell_votes:
                    st.info(f"● قرار ضعيف: شراء — {buy_votes} vs {sell_votes}")
                    overall = "WEAK_BUY"
                elif sell_votes > buy_votes:
                    st.info(f"● قرار ضعيف: بيع — {sell_votes} vs {buy_votes}")
                    overall = "WEAK_SELL"
                else:
                    st.warning("● قرار: محايد — لا أغلبية واضحة")
                    overall = "NEUTRAL"

                # ── Results Table — clean rows ──
                st.markdown("#### 📋 نتائج المحركات")

                for r in results:
                    conf_bar = r["conf_val"]
                    bar_bg = "#22C55E" if r["signal"] == 1 else ("#EF4444" if r["signal"] == -1 else "#1C2230")
                    bar_width = int(conf_bar * 100)

                    st.markdown(f"""
                    <div style="background:#0F1318;border:1px solid #1C2230;
                    border-radius:6px;padding:8px 14px;margin-bottom:4px;
                    display:flex;justify-content:space-between;align-items:center">
                        <span style="font-size:13px;min-width:180px;color:#D1D9E6">{r['المحرك']}</span>
                        <span style="color:{r['direction_color']};font-weight:600;min-width:80px;text-align:center;font-size:12px">{r['الإشارة']}</span>
                        <div style="flex:1;margin:0 12px;height:5px;background:#1C2230;border-radius:3px;overflow:hidden">
                            <div style="width:{bar_width}%;height:100%;background:{bar_bg};border-radius:3px"></div>
                        </div>
                        <span style="min-width:40px;text-align:center;font-weight:600;color:#D1D9E6;font-size:12px">{r['الثقة']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # ── Engine vote breakdown chart ────────────────────
                st.markdown("#### 📊 توزيع الأصوات")

                vote_data = pd.DataFrame({
                    "الفئة": ["شراء 🟢", "بيع 🔴", "محايد ⚪"],
                    "العدد": [buy_votes, sell_votes, neutral_votes],
                })
                st.bar_chart(vote_data, x="الفئة", y="العدد", color="#3B82F6", use_container_width=True)


with tab_scanner:
    from dashboard.ui_scanner import render_scanner
    render_scanner()

with tab_signals:
    from dashboard.ui_signals import render_signals
    render_signals()

with tab_ai:
    from dashboard.ui_ai_insights import render_ai_insights
    render_ai_insights()

with tab_smart:
    from core.smart_analysis import render_smart_analysis
    render_smart_analysis()

with tab_predictor:
    from dashboard.ui_trend_predictor import render_trend_predictor
    render_trend_predictor()

with tab_elliott:
    from dashboard.ui_elliott import render_elliott
    render_elliott()

with tab_gann:
    from dashboard.ui_gann import render_gann
    render_gann()

with tab_astrology:
    from dashboard.ui_astrology import render_astrology
    render_astrology()

with tab_ollama:
    from ui_ollama_ai import render_ollama_ai
    render_ollama_ai()

with tab_training:
    from dashboard.ui_training import render_training
    render_training()

with tab_backtest:
    from dashboard.ui_backtest import render_backtest
    render_backtest()

with tab_smc:
    from dashboard.ui_smc import render_smc
    render_smc()

with tab_news:
    from dashboard.ui_news import render_news
    render_news()

with tab_brain:
    from dashboard.ui_ai_brain import render_ai_brain
    render_ai_brain()

with tab_alerts:
    from dashboard.ui_alerts import render_alerts
    render_alerts()

with tab_perf:
    from dashboard.ui_performance import render_performance
    render_performance()

with tab_mt5:
    from dashboard.ui_mt5 import render_mt5
    render_mt5()

with tab_engine_compare:
    render_engine_compare()

with tab_live_rec:
    render_live_recommendations()

with tab_neural:
    render_neural_recommendation_tab()

with tab_master_strategy:
    from dashboard.ui_master_strategy import render_master_strategy
    render_master_strategy()

with tab_system:
    from dashboard.ui_system_status import render_system_status
    render_system_status()

with tab_llm:
    from dashboard.ui_llm_settings import render_llm_settings
    render_llm_settings()


# ══════════════════════════════════════════════════════════════════════
#  TAB: إدارة الصفقات الاحترافية (Professional Trade Management)
# ══════════════════════════════════════════════════════════════════════

# ═══ 🎓 التدريب والتحسين الذاتي ═══
with tab_training_new:
    st.header("🎓 نظام التدريب والتحسين الذاتي")

    # ── CSV Upload for Training Data ──
    import os, json as _json
    _td = "train_data"
    _tf = os.path.join(_td, "trade_records.jsonl")
    os.makedirs(_td, exist_ok=True)

    st.markdown("### 📤 رفع بيانات التدريب")
    _csv_upload = st.file_uploader(
        "ارفع ملف CSV يحتوي على صفقات التداول",
        type=["csv"],
        key="sl_self_learning_data_csv",
        help="الأعمدة المطلوبة: pair, trade_type, entry_price, stop_loss, take_profit, result"
    )

    if _csv_upload is not None:
        import pandas as _pd
        _df = _pd.read_csv(_csv_upload)
        st.dataframe(_df.head(10), use_container_width=True)
        st.caption(f"📊 {_df.shape[0]} صفقة | {_df.shape[1]} عمود")

        # Column mapping
        st.markdown("#### 🔗 ربط الأعمدة")
        _cols = list(_df.columns)
        _c1, _c2, _c3 = st.columns(3)
        with _c1:
            _col_pair = st.selectbox("الزوج (pair)", _cols, index=_cols.index("pair") if "pair" in _cols else 0, key="map_pair")
            _col_type = st.selectbox("النوع (trade_type)", _cols, index=_cols.index("trade_type") if "trade_type" in _cols else 0, key="map_type")
            _col_entry = st.selectbox("سعر الدخول (entry)", _cols, index=_cols.index("entry_price") if "entry_price" in _cols else 0, key="map_entry")
        with _c2:
            _col_sl = st.selectbox("وقف الخسارة (sl)", _cols, index=_cols.index("stop_loss") if "stop_loss" in _cols else 0, key="map_sl")
            _col_tp = st.selectbox("جني الأرباح (tp)", _cols, index=_cols.index("take_profit") if "take_profit" in _cols else 0, key="map_tp")
            _col_result = st.selectbox("النتيجة (result)", _cols, index=_cols.index("result") if "result" in _cols else 0, key="map_result")
        with _c3:
            _col_tf = st.selectbox("الإطار الزمني (timeframe)", ["—"] + _cols, index=(_cols.index("timeframe") + 1) if "timeframe" in _cols else 0, key="map_tf")
            _col_conf = st.selectbox("الثقة (confidence)", ["—"] + _cols, index=(_cols.index("confidence") + 1) if "confidence" in _cols else 0, key="map_conf")
            _col_strat = st.selectbox("الاستراتيجية (strategy)", ["—"] + _cols, index=(_cols.index("strategy") + 1) if "strategy" in _cols else 0, key="map_strat")

        if st.button("✅ تحويل وحفظ البيانات", key="convert_csv_to_jsonl", type="primary", use_container_width=True):
            from datetime import datetime as _dt
            import re as _re

            def _safe_float(val, default=0.0):
                """Convert value to float safely, handling date strings and non-numeric values."""
                try:
                    s = str(val).strip()
                    # Skip date-like strings (e.g. 2026.01.05)
                    if _re.match(r'^\d{4}\.\d{1,2}\.\d{1,2}$', s):
                        return default
                    # Skip time-like strings (e.g. 21:00)
                    if _re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', s):
                        return default
                    return float(s)
                except (ValueError, TypeError):
                    return default

            _records = []
            _errors = []
            for _idx, _row in _df.iterrows():
                # Validate entry_price is numeric
                _entry_val = _safe_float(_row[_col_entry], None)
                if _entry_val is None:
                    _errors.append(f"صف {_idx+1}: قيمة entry_price غير صالحة ('{_row[_col_entry]}') — تم تخطيها")
                    continue
                _sl_val = _safe_float(_row[_col_sl], None)
                if _sl_val is None:
                    _errors.append(f"صف {_idx+1}: قيمة stop_loss غير صالحة ('{_row[_col_sl]}') — تم تخطيها")
                    continue
                _tp_val = _safe_float(_row[_col_tp], None)
                if _tp_val is None:
                    _errors.append(f"صف {_idx+1}: قيمة take_profit غير صالحة ('{_row[_col_tp]}') — تم تخطيها")
                    continue

                _rec = {
                    "trade_id": f"T{_idx+1:03d}",
                    "timestamp": _dt.now().isoformat(),
                    "pair": str(_row[_col_pair]),
                    "timeframe": str(_row[_col_tf]) if _col_tf != "—" else "H1",
                    "trade_type": str(_row[_col_type]).upper(),
                    "entry_price": _entry_val,
                    "stop_loss": _sl_val,
                    "take_profit": _tp_val,
                    "result": str(_row[_col_result]).lower(),
                    "exit_price": _tp_val if str(_row[_col_result]).lower() == "win" else _sl_val,
                    "profit_pips": 0.0,
                    "confidence": _safe_float(_row[_col_conf], 0.5) if _col_conf != "—" else 0.5,
                    "strategy": str(_row[_col_strat]) if _col_strat != "—" else "unknown",
                    "notes": ""
                }
                _records.append(_rec)

            if _errors:
                st.warning(f"⚠️ تم تخطي {len(_errors)} صف بسبب قيم غير صالحة:")
                for _e in _errors[:10]:
                    st.text(f"  • {_e}")
                if len(_errors) > 10:
                    st.text(f"  ... و{len(_errors)-10} أخطاء أخرى")

            with open(_tf, "w", encoding="utf-8") as _f:
                for _r in _records:
                    _f.write(_json.dumps(_r, ensure_ascii=False) + "\n")

            st.success(f"✅ تم تحويل وحفظ {len(_records)} صفقة في {_tf}")
            st.rerun()

    st.markdown("---")
    if HAS_SELF_LEARNING:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 تتبع الملاحظات")
            try:
                feedback = FeedbackTracker()
                feedback.render()
            except Exception as e:
                st.warning(f"Feedback Tracker: {e}")
        with col2:
            st.subheader("🔧 الضبط الدقيق")
            try:
                tuner = FineTuner()
                tuner.render()
            except Exception as e:
                st.warning(f"Fine Tuner: {e}")
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("📚 محرك RAG")
            try:
                rag = RAGEngine()
                rag.render()
            except Exception as e:
                st.warning(f"RAG Engine: {e}")
        with col4:
            st.subheader("🚀 التحسين الذاتي")
            try:
                improver = SelfImprover()
                improver.render()
            except Exception as e:
                st.warning(f"Self Improver: {e}")
        st.divider()
        st.subheader("🎯 مدرب النماذج")
        try:
            train_sys = TrainSystem()
            train_sys.render()
        except Exception as e:
            st.warning(f"Train System: {e}")
    else:
        st.info("📝 نظام التدريب الذاتي غير متوفر — تأكد من وجود مجلد self_learning/")



# ═══ 🎯 نظام القرار المركزي ═══
with tab_decision:
    st.header("🎯 نظام القرار المركزي")
    if HAS_DECISION:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔍 محلل المخاطر")
            try:
                risk = DecisionRiskAnalyzer()
                risk.render()
            except Exception as e:
                st.warning(f"Risk Analyzer: {e}")
        with col2:
            st.subheader("✅ محقق الصفقات")
            try:
                validator = TradeValidator()
                validator.render()
            except Exception as e:
                st.warning(f"Trade Validator: {e}")
        st.divider()
        st.subheader("🎯 محرك القرار المركزي")
        try:
            decision = CentralDecisionEngine()
            decision.render()
        except Exception as e:
            st.warning(f"Central Decision: {e}")
        st.divider()
        st.subheader("🔀 خط أنابيب القرار v2")
        try:
            pipeline = DecisionPipelineV2()
            pipeline.render()
        except Exception as e:
            st.warning(f"Decision Pipeline: {e}")
    else:
        st.info("📝 نظام القرار المركزي غير متوفر — تأكد من وجود مجلد decision/")
    
    if HAS_LLM_ASSISTANT:
        st.divider()
        st.subheader("🤖 مساعد القرار بالذكاء الاصطناعي")
        try:
            llm_assist = LLMDecisionAssistant()
            llm_assist.render()
        except Exception as e:
            st.warning(f"LLM Decision Assistant: {e}")



# ═══ 📊 تحليلات إضافية ═══
with tab_dashboard_ui:
    st.header("📊 تحليلات إضافية")
    
    sub_tabs = st.tabs([
        "🕯️ الشموع", "🔗 الارتباط", "🦋 هارمونيك",
        "📔 يومية", "📋 التقارير", "⚡ التنفيذ",
        "🏗️ هيكل السوق", "📐 أنماط السعر", "🎯 توصيات"
    ])
    
    with sub_tabs[0]:
        if HAS_CANDLESTICK_TAB:
            try:
                render_candlestick_tab(df if 'df' in dir() else pd.DataFrame())
            except Exception as e:
                st.warning(f"الشموع: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[1]:
        if HAS_CORRELATION_TAB:
            try:
                render_correlation_tab(df if 'df' in dir() else pd.DataFrame())
            except Exception as e:
                st.warning(f"الارتباط: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[2]:
        if HAS_HARMONIC_TAB:
            try:
                render_harmonic_tab(df if 'df' in dir() else pd.DataFrame())
            except Exception as e:
                st.warning(f"هارمونيك: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[3]:
        if HAS_JOURNAL_TAB:
            try:
                render_journal_tab()
            except Exception as e:
                st.warning(f"اليومية: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[4]:
        if HAS_REPORTS_TAB:
            try:
                render_reports_tab()
            except Exception as e:
                st.warning(f"التقارير: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[5]:
        if HAS_EXECUTION_TAB:
            try:
                render_execution_tab()
            except Exception as e:
                st.warning(f"التنفيذ: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[6]:
        if HAS_MARKET_STRUCT_TAB:
            try:
                render_market_structure_tab(df if 'df' in dir() else pd.DataFrame())
            except Exception as e:
                st.warning(f"هيكل السوق: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[7]:
        if HAS_PRICE_PATTERNS_TAB:
            try:
                render_price_patterns_tab(df if 'df' in dir() else pd.DataFrame())
            except Exception as e:
                st.warning(f"أنماط السعر: {e}")
        else:
            st.info("غير متوفر")
    
    with sub_tabs[8]:
        if HAS_RECOMMENDATIONS_TAB:
            try:
                render_recommendations_tab()
            except Exception as e:
                st.warning(f"التوصيات: {e}")
        else:
            st.info("غير متوفر")


with tab_trade_mgr:
    # ── Professional Header ──
    st.markdown("""
    <div style="direction:rtl;text-align:right;padding:20px 0 10px 0">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,#FFD600,#FF9100);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px">
                📋
            </div>
            <div>
                <div style="font-size:24px;font-weight:bold;color:#E0E0E0">إدارة الصفقات الاحترافية</div>
                <div style="color:#888;font-size:13px">أوامر ماركت / ستوب / ليميت — بلان بي — تريلنج ستوب</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize TradeManager
    if "trade_manager" not in st.session_state:
        st.session_state["trade_manager"] = TradeManager(filepath="trades.json")
    tm = st.session_state["trade_manager"]

    # Get current price from session state or uploaded data
    current_price = st.session_state.get("current_price", 0.0)
    uploaded = st.session_state.get("uploaded_data")
    if uploaded is not None and hasattr(uploaded, "columns"):
        try:
            cols = [c.strip().lower() for c in uploaded.columns]
            if "close" in cols:
                close_col = uploaded.columns[cols.index("close")]
                current_price = float(uploaded[close_col].iloc[-1])
        except Exception:
            pass

    # ── Tabs ────────────────────────────────────────────────────
    sub_tab_new, sub_tab_active, sub_tab_history = st.tabs([
        "➕ صفقة جديدة", "📊 الصفقات النشطة", "📜 السجل"
    ])

    # ══════════════════════════════════════════════════════════════
    #  SUB-TAB: New Trade
    # ══════════════════════════════════════════════════════════════
    with sub_tab_new:
        st.markdown("### ➕ إنشاء صفقة جديدة")

        col1, col2, col3 = st.columns(3)
        with col1:
            new_symbol = st.text_input("📊 الرمز", st.session_state.get("symbol", "EURUSD"), key="tm_symbol")
            new_tf = st.selectbox("⏰ الإطار", ["M5", "M15", "H1", "H4", "D1"], index=2, key="tm_tf")
            new_direction = st.radio("📐 الاتجاه", ["BUY", "SELL"], horizontal=True, key="tm_dir")

        with col2:
            new_order_type = st.selectbox("📋 نوع الأمر", [
                ("🟢 شراء ماركت", "buy_market"),
                ("🔴 بيع ماركت", "sell_market"),
                ("🟡 شراء ستوب", "buy_stop"),
                ("🟡 بيع ستوب", "sell_stop"),
                ("🔵 شراء ليميت", "buy_limit"),
                ("🔵 بيع ليميت", "sell_limit"),
            ], format_func=lambda x: x[0], key="tm_order_type")[1]

            new_entry = st.number_input("🎯 سعر الدخول", value=current_price or 0.0, step=0.1, key="tm_entry")
            new_sl = st.number_input("🛑 وقف الخسارة", value=0.0, step=0.1, key="tm_sl")

        with col3:
            new_tp1 = st.number_input("🎯 TP1", value=0.0, step=0.1, key="tm_tp1")
            new_tp2 = st.number_input("🎯 TP2", value=0.0, step=0.1, key="tm_tp2")
            new_tp3 = st.number_input("🎯 TP3", value=0.0, step=0.1, key="tm_tp3")

        col4, col5, col6 = st.columns(3)
        with col4:
            new_atr = st.number_input("📏 ATR", value=10.0, step=0.1, key="tm_atr")
            new_conf = st.slider("🎯 الثقة %", 0, 100, 65, key="tm_conf")
        with col5:
            new_balance = st.number_input("💰 رصيد الحساب", value=10000, step=1000, key="tm_balance")
            new_risk = st.slider("⚠️ المخاطرة %", 0.1, 5.0, 1.0, 0.1, key="tm_risk")
        with col6:
            new_reason = st.text_area("📝 السبب", "", key="tm_reason", height=80)
            new_strategy = st.text_input("🧠 الاستراتيجية", "Manual", key="tm_strategy")

        # Plan B toggle
        enable_plan_b = st.checkbox("↩️ تفعيل بلان بي (عكس الصفقة عند الوقف)", value=True, key="tm_plan_b")

        # Trailing Stop
        trailing_mode = st.selectbox("🔄 تريلنج ستوب", [
            ("🔴 بدون", "none"),
            ("📏 ATR-based", "atr"),
            ("📊 نسبة مئوية", "percent"),
        ], format_func=lambda x: x[0], key="tm_trailing")[1]

        if st.button("✅ إنشاء الصفقة", key="tm_create", type="primary", use_container_width=True):
            if new_sl == 0:
                st.error("⚠️ يجب تحديد وقف الخسارة")
            elif new_tp1 == 0:
                st.error("⚠️ يجب تحديد TP1 على الأقل")
            elif new_direction == "BUY" and new_sl >= new_entry:
                st.error("⚠️ BUY: الوقف يجب أن يكون أقل من الدخول")
            elif new_direction == "SELL" and new_sl <= new_entry:
                st.error("⚠️ SELL: الوقف يجب أن يكون أعلى من الدخول")
            else:
                # Auto-fill TP2/TP3 if not set
                if new_tp2 == 0:
                    new_tp2 = new_tp1 + (abs(new_tp1 - new_entry) * 0.7) if new_direction == "BUY" else new_tp1 - (abs(new_entry - new_tp1) * 0.7)
                if new_tp3 == 0:
                    new_tp3 = new_tp2 + (abs(new_tp2 - new_entry) * 0.5) if new_direction == "BUY" else new_tp2 - (abs(new_entry - new_tp2) * 0.5)

                trade = create_trade_order(
                    symbol=new_symbol, timeframe=new_tf,
                    direction=new_direction, current_price=current_price or new_entry,
                    entry_price=new_entry, stop_loss=new_sl,
                    tp1=new_tp1, tp2=new_tp2, tp3=new_tp3,
                    atr=new_atr, confidence=new_conf,
                    reason=new_reason, strategy=new_strategy,
                    account_balance=new_balance, risk_percent=new_risk,
                )

                # Override trailing mode
                trade.trailing.mode = TrailingMode(trailing_mode)
                if trailing_mode != "none":
                    trade.trailing.activation_price = new_tp1

                # Override Plan B
                trade.plan_b.enabled = enable_plan_b

                trade_id = tm.add_trade(trade)
                st.success(f"✅ تم إنشاء الصفقة: **{trade_id}**")
                st.json(trade.to_dict())

    # ══════════════════════════════════════════════════════════════
    #  SUB-TAB: Active Trades
    # ══════════════════════════════════════════════════════════════
    with sub_tab_active:
        # Price update input
        price_col1, price_col2 = st.columns([3, 1])
        with price_col1:
            update_price = st.number_input(
                "💰 السعر الحالي (حدّث للإدارة)", value=current_price or 0.0,
                step=0.1, key="tm_update_price"
            )
        with price_col2:
            if st.button("🔄 تحديث", key="tm_refresh"):
                st.rerun()

        # Auto-refresh active trades
        active = tm.get_active_trades()
        if active:
            for trade in active:
                result = tm.update_price(trade.trade_id, update_price)
                events = result.get("events", [])
                for evt in events:
                    if evt == "sl_hit":
                        st.error(f"❌ {trade.trade_id}: وقف خسارة!")
                        if trade.plan_b.enabled and not trade.plan_b.activated:
                            reverse = tm.activate_plan_b(trade.trade_id)
                            if reverse:
                                st.warning(f"↩️ بلان بي: تم إنشاء صفقة عكسية {reverse.trade_id}")
                    elif "tp" in evt:
                        st.success(f"🎯 {trade.trade_id}: {evt}")

    # ══════════════════════════════════════════════════════════════
    #  SUB-TAB: History
    # ══════════════════════════════════════════════════════════════
    with sub_tab_history:
        summary = tm.get_trade_summary()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("إجمالي", summary["total_trades"])
        c2.metric("فوز", summary["wins"])
        c3.metric("خسارة", summary["losses"])
        c4.metric("النسبة", f"{summary['win_rate']}%")

        st.markdown("---")
        all_trades = list(tm.trades.values())
        if all_trades:
            for t in reversed(all_trades):
                with st.expander(
                    f"{t.order_type.emoji} {t.trade_id} — {t.symbol} {t.direction} | {t.status.arabic}",
                    expanded=False
                ):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"🎯 دخول: {t.entry_price}")
                    c2.write(f"🛑 وقف: {t.stop_loss}")
                    c3.write(f"💰 P&L: {t.pnl}$")

                    if t.actions:
                        st.markdown("**📜 الأحداث:**")
                        for a in t.actions:
                            st.caption(f"  {a['time']} — {a['action']}: {a['details']}")
        else:
            st.info("لا يوجد سجل صفقات بعد")
