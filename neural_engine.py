"""
GoldFX Pro - Neural Engine
Neural network prediction display using Streamlit.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def _simple_neural_predict(df: pd.DataFrame, lookback: int = 20) -> dict:
    """
    Simplified neural-inspired prediction using weighted feature aggregation.
    Mimics a single-layer neural network with hand-crafted weights.
    """
    if df is None or len(df) < lookback:
        return {"prediction": "WAIT", "confidence": 0, "features": {}}

    close = pd.to_numeric(df["close"], errors="coerce").tail(lookback)
    high = pd.to_numeric(df["high"], errors="coerce").tail(lookback)
    low = pd.to_numeric(df["low"], errors="coerce").tail(lookback)

    price = float(close.iloc[-1])

    # Feature extraction
    # f1: price momentum (normalized)
    mom_5 = (float(close.iloc[-1]) - float(close.iloc[-6])) / float(close.iloc[-6]) if len(close) >= 6 else 0
    mom_10 = (float(close.iloc[-1]) - float(close.iloc[-11])) / float(close.iloc[-11]) if len(close) >= 11 else 0

    # f2: RSI-like feature
    deltas = close.diff().dropna()
    gains = deltas.where(deltas > 0, 0).mean()
    losses = -deltas.where(deltas < 0, 0).mean()
    rsi_feat = 1 - (losses / (gains + losses + 1e-10)) if (gains + losses) > 0 else 0.5

    # f3: volatility feature
    vol = close.pct_change().std() * 100

    # f4: range position
    h_max = float(high.max())
    l_min = float(low.min())
    range_pos = (price - l_min) / (h_max - l_min + 1e-10)

    # f5: EMA crossover signal
    ema_short = close.ewm(span=9).mean().iloc[-1]
    ema_long = close.ewm(span=21).mean().iloc[-1]
    ema_signal = (float(ema_short) - float(ema_long)) / float(ema_long) * 100

    # Neural weights (simulated)
    w = {
        "momentum_5": 0.30,
        "momentum_10": 0.20,
        "rsi_feature": 0.20,
        "volatility": -0.10,
        "range_position": 0.10,
        "ema_crossover": 0.25,
    }

    # Normalize features to [-1, 1]
    features = {
        "momentum_5": np.tanh(mom_5 * 100),
        "momentum_10": np.tanh(mom_10 * 50),
        "rsi_feature": (rsi_feat - 0.5) * 2,
        "volatility": np.tanh(vol - 0.3),
        "range_position": (range_pos - 0.5) * 2,
        "ema_crossover": np.tanh(ema_signal * 10),
    }

    # Weighted sum + activation
    raw_score = sum(features[k] * w[k] for k in w)
    activated = np.tanh(raw_score)  # Activation function

    # Prediction
    if activated > 0.2:
        prediction = "BUY"
        confidence = min(95, int(abs(activated) * 100))
    elif activated < -0.2:
        prediction = "SELL"
        confidence = min(95, int(abs(activated) * 100))
    else:
        prediction = "WAIT"
        confidence = int((1 - abs(activated)) * 50)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "score": round(float(activated), 4),
        "features": {k: round(float(v), 4) for k, v in features.items()},
        "weights": w,
        "price": price,
        "timestamp": datetime.now().isoformat(),
    }


def _render_feature_chart(features: dict):
    """Render feature importance as a bar chart."""
    import pandas as pd
    df = pd.DataFrame([
        {"Feature": k.replace("_", " ").title(), "Value": v, "Color": "green" if v > 0 else "red"}
        for k, v in features.items()
    ])
    st.bar_chart(df.set_index("Feature")["Value"], color="Color")


def render_neural_engine():
    """Render the neural engine prediction panel."""
    st.header("🧠 Neural Engine")
    st.caption("Neural network-inspired price prediction model")

    df = st.session_state.get("market_data")
    if df is None:
        st.warning("⚠️ No market data loaded. Load data from the sidebar first.")
        return

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        lookback = st.slider("Lookback Period", 10, 100, 20, key="neural_lookback")
    with col2:
        threshold = st.slider("Confidence Threshold", 10, 80, 30, key="neural_threshold")

    # Run prediction
    result = _simple_neural_predict(df, lookback=lookback)

    # Main prediction display
    pred = result["prediction"]
    conf = result["confidence"]

    if pred == "BUY":
        st.success(f"🟢 **Neural Prediction: BUY** — Confidence: {conf}%")
    elif pred == "SELL":
        st.error(f"🔴 **Neural Prediction: SELL** — Confidence: {conf}%")
    else:
        st.warning(f"🟡 **Neural Prediction: WAIT** — Confidence: {conf}%")

    # Score gauge
    score = result.get("score", 0)
    st.metric("Neural Score", f"{score:.4f}", help="Range: -1 (strong sell) to +1 (strong buy)")

    # Feature analysis
    st.subheader("📊 Feature Activations")
    features = result.get("features", {})

    col_a, col_b = st.columns(2)
    with col_a:
        for feat, val in features.items():
            bar_color = "🟢" if val > 0 else "🔴"
            st.markdown(f"{bar_color} **{feat.replace('_', ' ').title()}**: {val:.4f}")
    with col_b:
        _render_feature_chart(features)

    # Architecture info
    with st.expander("🏗️ Model Architecture"):
        st.markdown("""
        **Type**: Single-Layer Perceptron with Feature Engineering

        **Features** (5 inputs):
        - Momentum (5-bar, 10-bar rate of change)
        - RSI-like oscillator
        - Volatility (price change std dev)
        - Range Position (where price is in recent range)
        - EMA Crossover signal (9/21 EMA)

        **Activation**: tanh (hyperbolic tangent)

        **Output**: [-1, +1] → SELL / WAIT / BUY
        """)

    # Historical simulation
    if st.checkbox("Run Rolling Prediction", key="neural_rolling"):
        st.subheader("📈 Rolling Predictions (Last 20 Candles)")
        predictions = []
        for i in range(20, 0, -1):
            subset = df.iloc[:-i] if i > 1 else df
            if len(subset) >= lookback:
                r = _simple_neural_predict(subset, lookback)
                predictions.append({
                    "Candle": len(subset),
                    "Prediction": r["prediction"],
                    "Score": r["score"],
                    "Confidence": r["confidence"],
                })
        if predictions:
            st.dataframe(pd.DataFrame(predictions), use_container_width=True)
