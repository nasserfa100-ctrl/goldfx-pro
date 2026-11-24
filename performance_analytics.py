"""
GoldFX Pro - Performance Analytics
Track and visualize trading performance metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta


class PerformanceAnalytics:
    """Trading performance analytics and visualization."""

    def __init__(self):
        pass

    def _get_trade_data(self) -> List[Dict]:
        """Get trade history from TradeManager."""
        tm = st.session_state.get("trade_manager")
        if tm:
            return tm.history
        return []

    def calculate_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not trades:
            return self._empty_metrics()

        pnls = [t.get("pnl", 0) for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]

        total_pnl = sum(pnls)
        win_rate = len(wins) / len(pnls) * 100 if pnls else 0
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0

        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Expectancy
        expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

        # Consecutive wins/losses
        max_consec_wins = self._max_consecutive(pnls, positive=True)
        max_consec_losses = self._max_consecutive(pnls, positive=False)

        # Drawdown
        equity = np.cumsum(pnls)
        peak = np.maximum.accumulate(equity)
        drawdown = peak - equity
        max_drawdown = float(np.max(drawdown)) if len(drawdown) > 0 else 0

        return {
            "total_trades": len(pnls),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy": round(expectancy, 2),
            "max_consecutive_wins": max_consec_wins,
            "max_consecutive_losses": max_consec_losses,
            "max_drawdown": round(max_drawdown, 2),
            "best_trade": round(max(pnls), 2) if pnls else 0,
            "worst_trade": round(min(pnls), 2) if pnls else 0,
            "avg_rr": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
        }

    def _max_consecutive(self, pnls: List[float], positive: bool = True) -> int:
        max_count = 0
        count = 0
        for p in pnls:
            if (positive and p > 0) or (not positive and p <= 0):
                count += 1
                max_count = max(max_count, count)
            else:
                count = 0
        return max_count

    def _empty_metrics(self) -> Dict[str, Any]:
        return {
            "total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0,
            "total_pnl": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0,
            "expectancy": 0, "max_consecutive_wins": 0, "max_consecutive_losses": 0,
            "max_drawdown": 0, "best_trade": 0, "worst_trade": 0, "avg_rr": 0,
        }

    def render(self):
        """Render the performance analytics dashboard."""
        st.header("📈 Performance Analytics")
        st.caption("Track your trading performance over time")

        trades = self._get_trade_data()

        if not trades:
            st.info("📝 No closed trades yet. Complete some trades to see analytics.")
            # Demo mode
            if st.button("Load Demo Data", key="perf_demo"):
                st.session_state["_perf_demo"] = True
                st.rerun()
            if st.session_state.get("_perf_demo"):
                trades = self._generate_demo_trades()
                metrics = self.calculate_metrics(trades)
            else:
                return
        else:
            metrics = self.calculate_metrics(trades)

        # Key metrics row
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total P&L", f"${metrics['total_pnl']:+.2f}")
        with c2:
            st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
        with c3:
            st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
        with c4:
            st.metric("Expectancy", f"${metrics['expectancy']:.2f}")
        with c5:
            st.metric("Max Drawdown", f"${metrics['max_drawdown']:.2f}")

        # Detailed metrics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Trade Statistics")
            stats_df = pd.DataFrame([
                {"Metric": "Total Trades", "Value": metrics["total_trades"]},
                {"Metric": "Winning Trades", "Value": metrics["wins"]},
                {"Metric": "Losing Trades", "Value": metrics["losses"]},
                {"Metric": "Average Win", "Value": f"${metrics['avg_win']:.2f}"},
                {"Metric": "Average Loss", "Value": f"${metrics['avg_loss']:.2f}"},
                {"Metric": "Best Trade", "Value": f"${metrics['best_trade']:.2f}"},
                {"Metric": "Worst Trade", "Value": f"${metrics['worst_trade']:.2f}"},
                {"Metric": "Avg R:R", "Value": f"1:{metrics['avg_rr']:.2f}"},
                {"Metric": "Max Consec Wins", "Value": metrics["max_consecutive_wins"]},
                {"Metric": "Max Consec Losses", "Value": metrics["max_consecutive_losses"]},
            ])
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("📉 Equity Curve")
            if trades:
                pnls = [t.get("pnl", 0) for t in trades]
                equity = np.cumsum([0] + pnls)
                eq_df = pd.DataFrame({"Trade #": range(len(equity)), "Equity ($)": equity})
                st.line_chart(eq_df.set_index("Trade #"))

        # P&L distribution
        if trades:
            st.subheader("📊 P&L Distribution")
            pnls = [t.get("pnl", 0) for t in trades]
            pnl_df = pd.DataFrame({"P&L ($)": pnls})
            st.bar_chart(pnl_df["P&L ($)"])

        # Win/Loss pie
        if metrics["total_trades"] > 0:
            st.subheader("🎯 Win/Loss Ratio")
            pie_data = pd.DataFrame({
                "Result": ["Wins", "Losses"],
                "Count": [metrics["wins"], metrics["losses"]],
            })
            st.bar_chart(pie_data.set_index("Result"))

    def _generate_demo_trades(self) -> List[Dict]:
        """Generate demo trade data for testing."""
        import random
        trades = []
        for i in range(20):
            pnl = random.uniform(-150, 200)
            trades.append({
                "order_id": f"DEMO{i:03d}",
                "symbol": "XAUUSD",
                "order_type": random.choice(["buy_market", "sell_market"]),
                "entry_price": random.uniform(2300, 2400),
                "close_price": random.uniform(2300, 2400),
                "pnl": round(pnl, 2),
                "pnl_pips": round(pnl / 10, 1),
                "lot_size": 0.01,
                "opened_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "closed_at": datetime.now().isoformat(),
            })
        return trades
