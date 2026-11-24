"""
GoldFX Pro - Engine Comparator
Compare multiple analysis engines on the same data.
"""

import pandas as pd
from typing import Dict, List, Any, Callable


def _engine_rsi_only(df: pd.DataFrame) -> Dict[str, Any]:
    """Pure RSI-based engine."""
    from ai_engine import _rsi
    close = pd.to_numeric(df["close"], errors="coerce")
    rsi = _rsi(close, 14)
    val = float(rsi.iloc[-1])
    if val < 30:
        return {"signal": "BUY", "confidence": 70, "reason": f"RSI oversold ({val:.1f})"}
    elif val > 70:
        return {"signal": "SELL", "confidence": 70, "reason": f"RSI overbought ({val:.1f})"}
    return {"signal": "WAIT", "confidence": 30, "reason": f"RSI neutral ({val:.1f})"}


def _engine_trend_follow(df: pd.DataFrame) -> Dict[str, Any]:
    """EMA trend following engine."""
    close = pd.to_numeric(df["close"], errors="coerce")
    ema9 = close.ewm(span=9).mean()
    ema21 = close.ewm(span=21).mean()
    ema50 = close.ewm(span=50).mean()
    price = float(close.iloc[-1])

    if price > ema9.iloc[-1] > ema21.iloc[-1] > ema50.iloc[-1]:
        return {"signal": "BUY", "confidence": 75, "reason": "All EMAs aligned bullish"}
    elif price < ema9.iloc[-1] < ema21.iloc[-1] < ema50.iloc[-1]:
        return {"signal": "SELL", "confidence": 75, "reason": "All EMAs aligned bearish"}
    elif ema9.iloc[-1] > ema21.iloc[-1]:
        return {"signal": "BUY", "confidence": 45, "reason": "Short-term bullish crossover"}
    elif ema9.iloc[-1] < ema21.iloc[-1]:
        return {"signal": "SELL", "confidence": 45, "reason": "Short-term bearish crossover"}
    return {"signal": "WAIT", "confidence": 25, "reason": "No clear trend"}


def _engine_breakout(df: pd.DataFrame) -> Dict[str, Any]:
    """Support/resistance breakout engine."""
    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")

    lookback = min(20, len(df) - 1)
    recent_high = float(high.tail(lookback).max())
    recent_low = float(low.tail(lookback).min())
    price = float(close.iloc[-1])
    mid = (recent_high + recent_low) / 2

    if price >= recent_high * 0.998:
        return {"signal": "BUY", "confidence": 65, "reason": f"Breakout above {recent_high:.5f}"}
    elif price <= recent_low * 1.002:
        return {"signal": "SELL", "confidence": 65, "reason": f"Breakdown below {recent_low:.5f}"}
    elif price > mid:
        return {"signal": "BUY", "confidence": 40, "reason": "Price in upper range"}
    else:
        return {"signal": "SELL", "confidence": 40, "reason": "Price in lower range"}


def _engine_momentum(df: pd.DataFrame) -> Dict[str, Any]:
    """Momentum / rate of change engine."""
    close = pd.to_numeric(df["close"], errors="coerce")
    roc_5 = (float(close.iloc[-1]) - float(close.iloc[-6])) / float(close.iloc[-6]) * 100 if len(close) >= 6 else 0
    roc_10 = (float(close.iloc[-1]) - float(close.iloc[-11])) / float(close.iloc[-11]) * 100 if len(close) >= 11 else 0

    if roc_5 > 0.3 and roc_10 > 0.5:
        return {"signal": "BUY", "confidence": 60, "reason": f"Momentum positive (5-bar: {roc_5:.2f}%)"}
    elif roc_5 < -0.3 and roc_10 < -0.5:
        return {"signal": "SELL", "confidence": 60, "reason": f"Momentum negative (5-bar: {roc_5:.2f}%)"}
    return {"signal": "WAIT", "confidence": 30, "reason": f"Momentum flat (5-bar: {roc_5:.2f}%)"}


def _engine_volatility(df: pd.DataFrame) -> Dict[str, Any]:
    """ATR-based volatility engine."""
    from ai_engine import _atr, _rsi
    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")

    atr = _atr(high, low, close)
    atr_val = float(atr.iloc[-1])
    price = float(close.iloc[-1])
    atr_pct = atr_val / price * 100

    rsi = _rsi(close)
    rsi_val = float(rsi.iloc[-1])

    if atr_pct > 0.5 and rsi_val < 35:
        return {"signal": "BUY", "confidence": 55, "reason": f"High vol + oversold (ATR: {atr_pct:.2f}%)"}
    elif atr_pct > 0.5 and rsi_val > 65:
        return {"signal": "SELL", "confidence": 55, "reason": f"High vol + overbought (ATR: {atr_pct:.2f}%)"}
    return {"signal": "WAIT", "confidence": 35, "reason": f"Volatility: {atr_pct:.2f}%, RSI: {rsi_val:.1f}"}


def _engine_hybrid(df: pd.DataFrame) -> Dict[str, Any]:
    """Hybrid multi-factor engine (default ai_engine)."""
    from ai_engine import analyze_dataframe
    result = analyze_dataframe(df)
    return {
        "signal": result.get("signal", "WAIT"),
        "confidence": result.get("confidence", 30),
        "reason": "; ".join(result.get("reasons", ["No clear signal"])),
    }


ENGINES: Dict[str, Callable[[pd.DataFrame], Dict[str, Any]]] = {
    "RSI Only": _engine_rsi_only,
    "Trend Follow": _engine_trend_follow,
    "Breakout": _engine_breakout,
    "Momentum": _engine_momentum,
    "Volatility": _engine_volatility,
    "Hybrid Multi-Factor": _engine_hybrid,
}


def run_engine_comparison(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Run all engines on the same dataframe and return results."""
    results = []
    for name, engine_fn in ENGINES.items():
        try:
            result = engine_fn(df)
            result["engine"] = name
            results.append(result)
        except Exception as e:
            results.append({
                "engine": name,
                "signal": "ERROR",
                "confidence": 0,
                "reason": str(e),
            })
    return results


def generate_comparison_summary(results: List[Dict[str, Any]]) -> str:
    """Generate a human-readable comparison summary."""
    buy_count = sum(1 for r in results if r.get("signal") == "BUY")
    sell_count = sum(1 for r in results if r.get("signal") == "SELL")
    wait_count = sum(1 for r in results if r.get("signal") == "WAIT")
    total = len(results)

    avg_confidence = sum(r.get("confidence", 0) for r in results) / max(total, 1)

    if buy_count > sell_count and buy_count > wait_count:
        consensus = "BULLISH"
    elif sell_count > buy_count and sell_count > wait_count:
        consensus = "BEARISH"
    else:
        consensus = "NEUTRAL"

    lines = [
        "=" * 50,
        "📊 ENGINE COMPARISON SUMMARY",
        "=" * 50,
        f"Total Engines: {total}",
        f"BUY signals:  {buy_count}/{total}",
        f"SELL signals: {sell_count}/{total}",
        f"WAIT signals: {wait_count}/{total}",
        f"Avg Confidence: {avg_confidence:.1f}%",
        f"Consensus: {consensus}",
        "-" * 50,
    ]

    for r in results:
        emoji = {"BUY": "🟢", "SELL": "🔴", "WAIT": "🟡", "ERROR": "⚫"}.get(r.get("signal"), "⚪")
        lines.append(f"  {emoji} {r['engine']:20s} → {r.get('signal', '?'):5s} ({r.get('confidence', 0)}%) - {r.get('reason', '')}")

    lines.append("=" * 50)
    return "\n".join(lines)
