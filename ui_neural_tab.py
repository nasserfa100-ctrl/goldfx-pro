"""
GoldFX Pro - Neural Recommendation Tab UI
Streamlit tab combining neural engine with traditional analysis.
"""

import streamlit as st
import pandas as pd


def render_neural_recommendation_tab():
    """Render the neural recommendation tab with combined analysis."""
    st.header("🧠 Neural Recommendations")
    st.caption("Combined neural network + traditional analysis")

    df = st.session_state.get("market_data")
    if df is None:
        st.warning("⚠️ No market data loaded. Load data from the sidebar first.")
        return

    from neural_engine import _simple_neural_predict
    from ai_engine import analyze_dataframe

    # Get both analyses
    neural_result = _simple_neural_predict(df)
    traditional = analyze_dataframe(df)

    # Side by side comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 Neural Signal")
        pred = neural_result["prediction"]
        conf = neural_result["confidence"]
        emoji = {"BUY": "🟢", "SELL": "🔴"}.get(pred, "🟡")
        st.markdown(f"### {emoji} {pred}")
        st.metric("Confidence", f"{conf}%")
        st.metric("Score", f"{neural_result.get('score', 0):.4f}")

        with st.expander("Feature Details"):
            for feat, val in neural_result.get("features", {}).items():
                bar = "█" * int(abs(val) * 20)
                sign = "+" if val > 0 else "-"
                st.text(f"{feat:20s} {sign}{bar} ({val:.4f})")

    with col2:
        st.subheader("📊 Traditional Signal")
        sig = traditional.get("signal", "WAIT")
        t_conf = traditional.get("confidence", 0)
        t_emoji = {"BUY": "🟢", "SELL": "🔴"}.get(sig, "🟡")
        st.markdown(f"### {t_emoji} {sig}")
        st.metric("Confidence", f"{t_conf}%")
        st.metric("RSI", f"{traditional.get('rsi', 0):.1f}")

        with st.expander("Indicators"):
            trend = traditional.get("trend", {})
            st.text(f"Trend: {trend.get('trend', 'N/A')} ({trend.get('strength', 0)})")
            st.text(f"ATR: {traditional.get('atr', 0):.5f}")
            for r in traditional.get("reasons", []):
                st.text(f"• {r}")

    # Combined signal
    st.divider()
    st.subheader("🎯 Combined Signal")

    # Weighted combination: 40% neural, 60% traditional
    signal_map = {"BUY": 1, "SELL": -1, "WAIT": 0}
    neural_score = signal_map.get(neural_result["prediction"], 0) * neural_result["confidence"] / 100
    trad_score = signal_map.get(traditional["signal"], 0) * traditional["confidence"] / 100

    combined = neural_score * 0.4 + trad_score * 0.6
    combined_conf = (neural_result["confidence"] * 0.4 + traditional["confidence"] * 0.6)

    if combined > 0.15:
        final_signal = "BUY"
        st.success(f"🟢 **BUY** — Combined Confidence: {combined_conf:.0f}%")
    elif combined < -0.15:
        final_signal = "SELL"
        st.error(f"🔴 **SELL** — Combined Confidence: {combined_conf:.0f}%")
    else:
        final_signal = "WAIT"
        st.warning(f"🟡 **WAIT** — Combined Confidence: {combined_conf:.0f}%")

    # Trade setup
    if final_signal in ("BUY", "SELL"):
        st.subheader("📋 Combined Trade Setup")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Entry", f"{traditional.get('entry', 0):.5f}")
        with c2:
            st.metric("Stop Loss", f"{traditional.get('sl', 0):.5f}")
        with c3:
            st.metric("TP1", f"{traditional.get('tp1', 0):.5f}")
        with c4:
            st.metric("TP2", f"{traditional.get('tp2', 0):.5f}")

    # Agreement indicator
    agrees = neural_result["prediction"] == traditional["signal"]
    if agrees:
        st.success("✅ Neural and Traditional engines **AGREE** on direction")
    else:
        st.warning("⚠️ Neural and Traditional engines **DISAGREE** — exercise caution")
