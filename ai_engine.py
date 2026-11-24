"""
GoldFX Pro - AI Analysis Engine
Core technical analysis: RSI, ATR, Support/Resistance, Trend detection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period).mean()


def _find_support_resistance(df: pd.DataFrame, lookback: int = 60) -> Dict[str, float]:
    recent = df.tail(lookback)
    highs = recent["high"].values
    lows = recent["low"].values

    # Pivot points method
    pivot = (highs[-1] + lows[-1] + recent["close"].values[-1]) / 3
    r1 = 2 * pivot - lows[-1]
    s1 = 2 * pivot - highs[-1]
    r2 = pivot + (highs[-1] - lows[-1])
    s2 = pivot - (highs[-1] - lows[-1])

    # Local extrema
    window = min(10, len(recent) // 3)
    resistance_levels = []
    support_levels = []

    for i in range(window, len(recent) - window):
        if highs[i] == max(highs[i - window:i + window + 1]):
            resistance_levels.append(highs[i])
        if lows[i] == min(lows[i - window:i + window + 1]):
            support_levels.append(lows[i])

    # Cluster nearby levels
    def cluster_levels(levels, threshold_pct=0.002):
        if not levels:
            return []
        levels = sorted(levels)
        clusters = [[levels[0]]]
        for lvl in levels[1:]:
            if abs(lvl - clusters[-1][-1]) / clusters[-1][-1] < threshold_pct:
                clusters[-1].append(lvl)
            else:
                clusters.append([lvl])
        return [np.mean(c) for c in clusters]

    resistance_levels = cluster_levels(resistance_levels)
    support_levels = cluster_levels(support_levels)

    # Combine with pivot
    all_resistance = sorted(set(resistance_levels + [r1, r2]), reverse=True)[:3]
    all_support = sorted(set(support_levels + [s1, s2]))[:3]

    return {
        "resistance": all_resistance,
        "support": all_support,
        "pivot": round(pivot, 5),
    }


def _detect_trend(df: pd.DataFrame, lookback: int = 60) -> Dict[str, Any]:
    recent = df.tail(lookback)
    close = recent["close"]

    # EMA crossover
    ema_short = close.ewm(span=9).mean()
    ema_mid = close.ewm(span=21).mean()
    ema_long = close.ewm(span=50).mean()

    current_price = close.iloc[-1]
    slope = (close.iloc[-1] - close.iloc[-5]) / 5 if len(close) >= 5 else 0

    # Trend determination
    if current_price > ema_short.iloc[-1] > ema_mid.iloc[-1]:
        trend = "BULLISH"
        strength = min(100, int(((current_price - ema_mid.iloc[-1]) / current_price) * 10000))
    elif current_price < ema_short.iloc[-1] < ema_mid.iloc[-1]:
        trend = "BEARISH"
        strength = min(100, int(((ema_mid.iloc[-1] - current_price) / current_price) * 10000))
    else:
        trend = "NEUTRAL"
        strength = 30

    return {
        "trend": trend,
        "strength": strength,
        "ema_short": round(float(ema_short.iloc[-1]), 5),
        "ema_mid": round(float(ema_mid.iloc[-1]), 5),
        "ema_long": round(float(ema_long.iloc[-1]), 5),
        "slope": round(float(slope), 5),
    }


def analyze_dataframe(df: pd.DataFrame, lookback: int = 60, sl_mode: str = "hybrid") -> Dict[str, Any]:
    """
    Main analysis engine. Returns a signal dict with all indicators and trade recommendation.

    Args:
        df: OHLCV DataFrame with columns: open, high, low, close, volume
        lookback: number of candles to analyze
        sl_mode: "atr" | "fixed" | "hybrid" - stop loss calculation mode

    Returns:
        Signal dict with rsi, atr, trend, support/resistance, recommendation, etc.
    """
    if df is None or len(df) < 20:
        return {"error": "Insufficient data", "signal": "WAIT"}

    df = df.copy()
    # Normalize column names to lowercase (handles "Close" → "close", etc.)
    df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    recent = df.tail(lookback)

    # RSI
    rsi_series = _rsi(recent["close"])
    rsi_val = round(float(rsi_series.iloc[-1]), 2)

    # ATR
    atr_series = _atr(recent["high"], recent["low"], recent["close"])
    atr_val = round(float(atr_series.iloc[-1]), 5)

    # Support/Resistance
    sr = _find_support_resistance(df, lookback)

    # Trend
    trend_info = _detect_trend(df, lookback)

    # Current price
    current_price = float(recent["close"].iloc[-1])

    # Signal generation
    signal = "WAIT"
    confidence = 0
    entry = current_price
    sl = 0.0
    tp1 = 0.0
    tp2 = 0.0
    tp3 = 0.0
    reasons = []

    # RSI signals
    if rsi_val < 30:
        reasons.append(f"RSI oversold ({rsi_val})")
        confidence += 25
    elif rsi_val > 70:
        reasons.append(f"RSI overbought ({rsi_val})")
        confidence += 25
    elif rsi_val < 40:
        reasons.append(f"RSI approaching oversold ({rsi_val})")
        confidence += 10
    elif rsi_val > 60:
        reasons.append(f"RSI approaching overbought ({rsi_val})")
        confidence += 10

    # Trend signals
    if trend_info["trend"] == "BULLISH":
        reasons.append(f"Bullish trend (strength: {trend_info['strength']})")
        confidence += 20
    elif trend_info["trend"] == "BEARISH":
        reasons.append(f"Bearish trend (strength: {trend_info['strength']})")
        confidence += 20

    # Support/resistance proximity
    for s in sr["support"]:
        if abs(current_price - s) / current_price < 0.002:
            reasons.append(f"Near support ({s:.5f})")
            confidence += 15
            break
    for r in sr["resistance"]:
        if abs(current_price - r) / current_price < 0.002:
            reasons.append(f"Near resistance ({r:.5f})")
            confidence += 15
            break

    # Determine direction
    buy_score = 0
    sell_score = 0

    if rsi_val < 40:
        buy_score += 2
    elif rsi_val > 60:
        sell_score += 2

    if trend_info["trend"] == "BULLISH":
        buy_score += 3
    elif trend_info["trend"] == "BEARISH":
        sell_score += 3

    if buy_score > sell_score and confidence >= 30:
        signal = "BUY"
    elif sell_score > buy_score and confidence >= 30:
        signal = "SELL"
    else:
        signal = "WAIT"
        confidence = max(confidence, 20)

    # SL/TP calculation
    if sl_mode == "atr":
        sl_dist = atr_val * 1.5
    elif sl_mode == "fixed":
        sl_dist = current_price * 0.005  # 0.5%
    else:  # hybrid
        sl_dist = max(atr_val * 1.5, current_price * 0.003)

    if signal == "BUY":
        sl = round(entry - sl_dist, 5)
        tp1 = round(entry + sl_dist * 1.5, 5)
        tp2 = round(entry + sl_dist * 2.5, 5)
        tp3 = round(entry + sl_dist * 4.0, 5)
    elif signal == "SELL":
        sl = round(entry + sl_dist, 5)
        tp1 = round(entry - sl_dist * 1.5, 5)
        tp2 = round(entry - sl_dist * 2.5, 5)
        tp3 = round(entry - sl_dist * 4.0, 5)

    result = {
        "signal": signal,
        "confidence": min(confidence, 95),
        "entry": round(entry, 5),
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "rsi": rsi_val,
        "atr": atr_val,
        "atr_pips": round(atr_val * 10000, 1),
        "trend": trend_info,
        "support_resistance": sr,
        "reasons": reasons,
        "sl_mode": sl_mode,
        "current_price": round(current_price, 5),
        "timestamp": pd.Timestamp.now().isoformat(),
    }

    return result


def format_signal_block(signal: Dict[str, Any]) -> str:
    """Format a signal dict into a readable text block."""
    if "error" in signal:
        return f"⚠️ {signal['error']}"

    lines = []
    lines.append("=" * 50)
    lines.append(f"📊 SIGNAL: {signal['signal']}  |  Confidence: {signal['confidence']}%")
    lines.append("=" * 50)
    lines.append(f"💰 Entry:   {signal['entry']}")
    lines.append(f"🛑 SL:      {signal['sl']}")
    lines.append(f"🎯 TP1:     {signal['tp1']}")
    lines.append(f"🎯 TP2:     {signal['tp2']}")
    lines.append(f"🎯 TP3:     {signal['tp3']}")
    lines.append("-" * 50)
    lines.append(f"📈 RSI:     {signal['rsi']}")
    lines.append(f"📐 ATR:     {signal['atr']} ({signal['atr_pips']} pips)")
    lines.append(f"📊 Trend:   {signal['trend']['trend']} (strength: {signal['trend']['strength']})")
    lines.append("-" * 50)
    lines.append("🔑 Reasons:")
    for r in signal.get("reasons", []):
        lines.append(f"   • {r}")
    lines.append("=" * 50)
    return "\n".join(lines)


def generate_all_recommendations(df: pd.DataFrame, sl_mode: str = "hybrid") -> Dict[str, Dict]:
    """
    Generate recommendations for multiple timeframes.
    Expects df to have enough data for analysis.
    Returns dict keyed by timeframe label.
    """
    result = {}

    # Analyze with different lookback periods as proxy for timeframes
    lookbacks = {
        "M5_scalp": 30,
        "M15_short": 60,
        "H1_swing": 120,
        "H4_position": 200,
    }

    for label, lb in lookbacks.items():
        if len(df) >= lb:
            result[label] = analyze_dataframe(df, lookback=lb, sl_mode=sl_mode)
        else:
            result[label] = analyze_dataframe(df, lookback=min(lb, len(df)), sl_mode=sl_mode)

    return result
