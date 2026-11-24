"""
GoldFX Pro - Risk Analyzer
Position sizing, risk/reward analysis, and exposure management.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class RiskAnalyzer:
    """Analyze risk for trading positions."""

    def __init__(self):
        self.account_balance = 10000.0
        self.max_risk_pct = 2.0
        self.max_positions = 5
        self.max_daily_loss_pct = 5.0

    def calculate_position_size(self, entry: float, sl: float, balance: float, risk_pct: float = 2.0) -> Dict[str, float]:
        """Calculate position size based on risk percentage."""
        if sl == 0 or entry == 0:
            return {"lots": 0, "risk_amount": 0, "sl_distance": 0}

        sl_distance = abs(entry - sl)
        risk_amount = balance * (risk_pct / 100)
        # For gold: 1 lot = 100 oz, pip value ≈ $1 per 0.01 move per 0.01 lot
        lots = risk_amount / (sl_distance * 100 * 100)
        lots = round(max(0.01, min(lots, 100.0)), 2)

        return {
            "lots": lots,
            "risk_amount": round(risk_amount, 2),
            "sl_distance": round(sl_distance, 5),
            "potential_loss": round(lots * sl_distance * 100 * 100, 2),
            "potential_profit_tp1": round(lots * sl_distance * 1.5 * 100 * 100, 2),
        }

    def risk_reward_ratio(self, entry: float, sl: float, tp1: float, tp2: float = 0, tp3: float = 0) -> Dict[str, float]:
        """Calculate risk/reward ratios."""
        risk = abs(entry - sl)
        if risk == 0:
            return {"rr1": 0, "rr2": 0, "rr3": 0}

        rr1 = abs(tp1 - entry) / risk if tp1 else 0
        rr2 = abs(tp2 - entry) / risk if tp2 else 0
        rr3 = abs(tp3 - entry) / risk if tp3 else 0

        return {
            "rr1": round(rr1, 2),
            "rr2": round(rr2, 2),
            "rr3": round(rr3, 2),
            "risk_pips": round(risk * 10000, 1),
            "reward_pips_tp1": round(abs(tp1 - entry) * 10000, 1) if tp1 else 0,
        }

    def analyze_drawdown(self, equity_curve: list) -> Dict[str, float]:
        """Analyze drawdown from equity curve."""
        if not equity_curve:
            return {"max_drawdown": 0, "max_drawdown_pct": 0, "current_drawdown": 0}

        peak = equity_curve[0]
        max_dd = 0
        max_dd_pct = 0

        for val in equity_curve:
            if val > peak:
                peak = val
            dd = peak - val
            dd_pct = dd / peak * 100 if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct

        current_dd = peak - equity_curve[-1] if equity_curve else 0
        current_dd_pct = current_dd / peak * 100 if peak > 0 else 0

        return {
            "max_drawdown": round(max_dd, 2),
            "max_drawdown_pct": round(max_dd_pct, 2),
            "current_drawdown": round(current_dd, 2),
            "current_drawdown_pct": round(current_dd_pct, 2),
            "peak_equity": round(peak, 2),
        }

    def render(self):
        """Render the risk analyzer UI in Streamlit."""
        st.header("⚠️ Risk Analyzer")
        st.caption("Position sizing and risk management")

        # Account settings
        col1, col2, col3 = st.columns(3)
        with col1:
            balance = st.number_input("Account Balance ($)", 100.0, 1000000.0, 10000.0, 100.0, key="risk_balance")
        with col2:
            risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 2.0, 0.1, key="risk_pct")
        with col3:
            max_positions = st.number_input("Max Positions", 1, 20, 5, key="risk_max_pos")

        # Get signal from session
        df = st.session_state.get("market_data")
        if df is not None:
            from ai_engine import analyze_dataframe
            signal = analyze_dataframe(df)

            st.divider()
            st.subheader("📊 Current Signal Risk Analysis")

            entry = signal.get("entry", 0)
            sl = signal.get("sl", 0)
            tp1 = signal.get("tp1", 0)
            tp2 = signal.get("tp2", 0)
            tp3 = signal.get("tp3", 0)

            # Position sizing
            sizing = self.calculate_position_size(entry, sl, balance, risk_pct)
            rr = self.risk_reward_ratio(entry, sl, tp1, tp2, tp3)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Position Size", f"{sizing['lots']} lots")
            with c2:
                st.metric("Risk Amount", f"${sizing['risk_amount']}")
            with c3:
                st.metric("R:R (TP1)", f"1:{rr['rr1']}")
            with c4:
                st.metric("R:R (TP2)", f"1:{rr['rr2']}")

            # Risk assessment
            st.subheader("🎯 Risk Assessment")
            if rr["rr1"] >= 2:
                st.success(f"✅ Good risk/reward ratio: 1:{rr['rr1']}")
            elif rr["rr1"] >= 1:
                st.warning(f"⚠️ Marginal risk/reward: 1:{rr['rr1']}")
            else:
                st.error(f"❌ Poor risk/reward: 1:{rr['rr1']}")

            if risk_pct > 3:
                st.error("❌ Risk per trade exceeds 3% — reduce position size")
            elif risk_pct > 2:
                st.warning("⚠️ Risk per trade above 2% — consider reducing")
            else:
                st.success("✅ Risk per trade within safe limits")

            # Trade plan table
            st.subheader("📋 Trade Plan")
            plan_data = {
                "Level": ["Entry", "Stop Loss", "TP1", "TP2", "TP3"],
                "Price": [f"{entry:.5f}", f"{sl:.5f}", f"{tp1:.5f}", f"{tp2:.5f}", f"{tp3:.5f}"],
                "Distance (pips)": [
                    "—",
                    f"{rr['risk_pips']:.1f}",
                    f"{rr['reward_pips_tp1']:.1f}",
                    f"{abs(tp2 - entry) * 10000:.1f}" if tp2 else "—",
                    f"{abs(tp3 - entry) * 10000:.1f}" if tp3 else "—",
                ],
                "P&L ($)": [
                    "—",
                    f"-${sizing['potential_loss']:.2f}",
                    f"+${sizing['potential_profit_tp1']:.2f}",
                    "—",
                    "—",
                ],
            }
            st.dataframe(pd.DataFrame(plan_data), use_container_width=True, hide_index=True)
        else:
            st.info("Load market data to see risk analysis")

        # Manual calculator
        with st.expander("🧮 Manual Position Calculator"):
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                m_entry = st.number_input("Entry", 0.0, format="%.5f", key="risk_m_entry")
            with mc2:
                m_sl = st.number_input("Stop Loss", 0.0, format="%.5f", key="risk_m_sl")
            with mc3:
                m_tp = st.number_input("Take Profit", 0.0, format="%.5f", key="risk_m_tp")

            if m_entry and m_sl:
                m_sizing = self.calculate_position_size(m_entry, m_sl, balance, risk_pct)
                m_rr = self.risk_reward_ratio(m_entry, m_sl, m_tp)
                st.metric("Recommended Lots", f"{m_sizing['lots']}")
                st.metric("Risk/Reward", f"1:{m_rr['rr1']}")
