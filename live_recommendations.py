"""
GoldFX Pro - Live Recommendations Panel
Streamlit UI for real-time trading recommendations.
"""

import streamlit as st
import pandas as pd
from datetime import datetime


def render_live_recommendations():
    """Render the live recommendations panel in Streamlit."""
    st.header("📡 Live Recommendations")
    st.caption("Real-time trading signals based on AI analysis")

    # Check if data is available
    df = st.session_state.get("market_data")
    if df is None:
        st.warning("⚠️ No market data loaded. Please load data from the sidebar first.")
        return

    from ai_engine import analyze_dataframe, format_signal_block

    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        sl_mode = st.selectbox("SL Mode", ["hybrid", "atr", "fixed"], key="live_sl_mode")
    with col2:
        lookback = st.slider("Lookback", 20, 200, 60, key="live_lookback")
    with col3:
        auto_refresh = st.toggle("Auto Refresh", value=False, key="live_auto_refresh")

    # Analyze
    signal = analyze_dataframe(df, lookback=lookback, sl_mode=sl_mode)

    # Display signal
    if signal.get("signal") == "BUY":
        st.success(f"🟢 **BUY SIGNAL** — Confidence: {signal['confidence']}%")
    elif signal.get("signal") == "SELL":
        st.error(f"🔴 **SELL SIGNAL** — Confidence: {signal['confidence']}%")
    else:
        st.warning(f"🟡 **WAIT** — Confidence: {signal['confidence']}%")

    # Signal details
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📋 Trade Setup")
        st.metric("Entry", f"{signal.get('entry', 0):.5f}")
        st.metric("Stop Loss", f"{signal.get('sl', 0):.5f}")
        st.metric("Take Profit 1", f"{signal.get('tp1', 0):.5f}")
        st.metric("Take Profit 2", f"{signal.get('tp2', 0):.5f}")
        st.metric("Take Profit 3", f"{signal.get('tp3', 0):.5f}")

    with col_b:
        st.subheader("📊 Indicators")
        st.metric("RSI", f"{signal.get('rsi', 0):.1f}")
        st.metric("ATR", f"{signal.get('atr', 0):.5f}")
        trend = signal.get("trend", {})
        st.metric("Trend", trend.get("trend", "N/A"))
        st.metric("Trend Strength", f"{trend.get('strength', 0)}")

    # Reasons
    st.subheader("🔑 Analysis Reasons")
    for reason in signal.get("reasons", []):
        st.markdown(f"• {reason}")

    # Support/Resistance
    sr = signal.get("support_resistance", {})
    if sr:
        st.subheader("📐 Key Levels")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Resistance**")
            for r in sr.get("resistance", []):
                st.markdown(f"🔴 {r:.5f}")
        with c2:
            st.metric("Pivot", f"{sr.get('pivot', 0):.5f}")
        with c3:
            st.markdown("**Support**")
            for s in sr.get("support", []):
                st.markdown(f"🟢 {s:.5f}")

    # Signal text block
    with st.expander("📄 Full Signal Report"):
        st.code(format_signal_block(signal), language="text")

    # Multi-timeframe recommendations
    from ai_engine import generate_all_recommendations
    if st.checkbox("Show Multi-Timeframe Analysis", key="live_mtf"):
        recs = generate_all_recommendations(df, sl_mode=sl_mode)
        st.subheader("⏰ Multi-Timeframe")
        for tf, rec in recs.items():
            emoji = {"BUY": "🟢", "SELL": "🔴"}.get(rec.get("signal"), "🟡")
            st.markdown(f"**{tf}**: {emoji} {rec['signal']} ({rec['confidence']}%) — SL: {rec.get('sl', 'N/A')}")

    # Auto refresh hint
    if auto_refresh:
        st.caption("🔄 Auto-refresh enabled — data updates on rerun")
