"""
GoldFX Pro - Sentiment Engine
Market sentiment analysis for backtesting integration.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def sentiment_signal_for_backtest(df: pd.DataFrame, tf: str = "H1") -> Dict[str, Any]:
    """
    Generate a sentiment-based signal for backtesting.

    Uses price action patterns, momentum, and volatility to infer market sentiment.

    Args:
        df: OHLCV DataFrame
        tf: timeframe label (e.g., "H1", "H4", "D1")

    Returns:
        dict with signal (1=buy, -1=sell, 0=neutral), confidence, atr, last_close, reason
    """
    if df is None or len(df) < 30:
        return {"signal": 0, "confidence": 0.0, "atr": 0.0, "last_close": 0.0, "reason": "Insufficient data"}

    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    volume = pd.to_numeric(df.get("volume", pd.Series(0)), errors="coerce").fillna(0)

    price = float(close.iloc[-1])

    # ATR calculation
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    atr = float(tr.rolling(14).mean().iloc[-1])

    # ── Sentiment factors ──

    # 1. Price momentum (multi-period)
    mom_scores = []
    for period in [5, 10, 20]:
        if len(close) >= period + 1:
            mom = (float(close.iloc[-1]) - float(close.iloc[-period - 1])) / float(close.iloc[-period - 1])
            mom_scores.append(np.tanh(mom * 100))

    avg_momentum = np.mean(mom_scores) if mom_scores else 0

    # 2. Candle body analysis (bullish vs bearish candles)
    recent = df.tail(20)
    bodies = pd.to_numeric(recent["close"], errors="coerce") - pd.to_numeric(recent["open"], errors="coerce")
    bullish_ratio = (bodies > 0).sum() / len(bodies) if len(bodies) > 0 else 0.5
    candle_score = (bullish_ratio - 0.5) * 2  # [-1, 1]

    # 3. Higher highs / lower lows pattern
    hh_ll_score = 0.0
    if len(high) >= 10 and len(low) >= 10:
        recent_highs = high.tail(10).values
        recent_lows = low.tail(10).values
        higher_highs = sum(1 for i in range(1, len(recent_highs)) if recent_highs[i] > recent_highs[i-1])
        lower_lows = sum(1 for i in range(1, len(recent_lows)) if recent_lows[i] < recent_lows[i-1])
        hh_ll_score = (higher_highs - lower_lows) / 9  # [-1, 1]

    # 4. Close position within range
    if len(df) >= 20:
        range_high = float(high.tail(20).max())
        range_low = float(low.tail(20).min())
        range_size = range_high - range_low
        if range_size > 0:
            position = (price - range_low) / range_size  # 0 to 1
            range_score = (position - 0.5) * 2  # [-1, 1]
        else:
            range_score = 0
    else:
        range_score = 0

    # 5. Volume sentiment (if available)
    vol_score = 0.0
    if volume.sum() > 0:
        recent_vol = volume.tail(10)
        avg_vol = volume.tail(50).mean() if len(volume) >= 50 else volume.mean()
        if avg_vol > 0:
            vol_ratio = float(recent_vol.mean()) / float(avg_vol)
            vol_score = np.tanh((vol_ratio - 1) * 2)

    # ── Weighted combination ──
    weights = {
        "momentum": 0.30,
        "candle_body": 0.20,
        "hh_ll": 0.20,
        "range_position": 0.20,
        "volume": 0.10,
    }

    combined = (
        avg_momentum * weights["momentum"] +
        candle_score * weights["candle_body"] +
        hh_ll_score * weights["hh_ll"] +
        range_score * weights["range_position"] +
        vol_score * weights["volume"]
    )

    # Determine signal
    confidence = min(95.0, abs(combined) * 100)

    if combined > 0.15:
        signal = 1
        reason = f"Bullish sentiment (momentum: {avg_momentum:.2f}, candles: {candle_score:.2f})"
    elif combined < -0.15:
        signal = -1
        reason = f"Bearish sentiment (momentum: {avg_momentum:.2f}, candles: {candle_score:.2f})"
    else:
        signal = 0
        reason = f"Neutral sentiment (score: {combined:.3f})"

    return {
        "signal": signal,
        "confidence": round(confidence, 1),
        "atr": round(atr, 5),
        "last_close": round(price, 5),
        "reason": reason,
        "tf": tf,
        "factors": {
            "momentum": round(float(avg_momentum), 4),
            "candle_body": round(float(candle_score), 4),
            "hh_ll": round(float(hh_ll_score), 4),
            "range_position": round(float(range_score), 4),
            "volume": round(float(vol_score), 4),
            "combined": round(float(combined), 4),
        },
    }
