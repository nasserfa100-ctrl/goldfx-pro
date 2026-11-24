"""
GoldFX Pro - Engine Compare UI
Streamlit interface for comparing multiple analysis engines.
"""

import streamlit as st
import pandas as pd


def render_engine_compare():
    """Render the engine comparison panel."""
    st.header("⚖️ Engine Comparison")
    st.caption("Compare multiple analysis engines side by side")

    df = st.session_state.get("market_data")
    if df is None:
        st.warning("⚠️ No market data loaded. Load data from the sidebar first.")
        return

    from engine_comparator import run_engine_comparison, generate_comparison_summary

    # Run comparison
    with st.spinner("Running all engines..."):
        results = run_engine_comparison(df)

    # Summary
    summary = generate_comparison_summary(results)
    st.code(summary, language="text")

    # Visual comparison
    st.subheader("📊 Visual Comparison")

    # Signal distribution
    signal_counts = {}
    for r in results:
        sig = r.get("signal", "UNKNOWN")
        signal_counts[sig] = signal_counts.get(sig, 0) + 1

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟢 BUY Engines", signal_counts.get("BUY", 0))
    with col2:
        st.metric("🔴 SELL Engines", signal_counts.get("SELL", 0))
    with col3:
        st.metric("🟡 WAIT Engines", signal_counts.get("WAIT", 0))

    # Detailed table
    st.subheader("📋 Detailed Results")
    table_data = []
    for r in results:
        emoji = {"BUY": "🟢", "SELL": "🔴", "WAIT": "🟡", "ERROR": "⚫"}.get(r.get("signal"), "⚪")
        table_data.append({
            "Engine": r.get("engine", "Unknown"),
            "Signal": f"{emoji} {r.get('signal', 'N/A')}",
            "Confidence": f"{r.get('confidence', 0)}%",
            "Reason": r.get("reason", ""),
        })

    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    # Confidence chart
    st.subheader("📊 Confidence Distribution")
    conf_data = pd.DataFrame([
        {"Engine": r["engine"], "Confidence": r.get("confidence", 0)}
        for r in results
    ])
    st.bar_chart(conf_data.set_index("Engine"), color="#4CAF50")

    # Consensus meter
    buy_total = sum(r.get("confidence", 0) for r in results if r.get("signal") == "BUY")
    sell_total = sum(r.get("confidence", 0) for r in results if r.get("signal") == "SELL")
    total = buy_total + sell_total + 1

    consensus_pct = (buy_total - sell_total) / total * 100

    st.subheader("🎯 Weighted Consensus")
    if consensus_pct > 20:
        st.success(f"Bullish consensus: {consensus_pct:+.1f}%")
    elif consensus_pct < -20:
        st.error(f"Bearish consensus: {consensus_pct:+.1f}%")
    else:
        st.warning(f"Neutral consensus: {consensus_pct:+.1f}%")

    st.progress(min(100, max(0, int(50 + consensus_pct / 2))))
