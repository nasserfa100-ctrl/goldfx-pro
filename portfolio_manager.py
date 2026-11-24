"""
GoldFX Pro - Portfolio Manager
Multi-symbol portfolio tracking and management.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime


class PortfolioManager:
    """Manage a portfolio of positions across multiple symbols."""

    def __init__(self):
        self.positions: Dict[str, Dict] = {}
        self.watchlist: List[str] = ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY"]

    def add_position(self, symbol: str, direction: str, entry: float, lots: float, sl: float = 0, tp: float = 0):
        self.positions[symbol] = {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "lots": lots,
            "sl": sl,
            "tp": tp,
            "opened_at": datetime.now().isoformat(),
            "current_price": entry,
            "pnl": 0.0,
        }

    def remove_position(self, symbol: str):
        self.positions.pop(symbol, None)

    def update_price(self, symbol: str, price: float):
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos["current_price"] = price
            if pos["direction"] == "buy":
                pos["pnl"] = round((price - pos["entry"]) * pos["lots"] * 100, 2)
            else:
                pos["pnl"] = round((pos["entry"] - price) * pos["lots"] * 100, 2)

    def get_total_pnl(self) -> float:
        return sum(p.get("pnl", 0) for p in self.positions.values())

    def get_portfolio_summary(self) -> Dict[str, Any]:
        total_pnl = self.get_total_pnl()
        total_lots = sum(p.get("lots", 0) for p in self.positions.values())
        exposure = len(self.positions)

        return {
            "total_positions": exposure,
            "total_lots": round(total_lots, 2),
            "total_pnl": round(total_pnl, 2),
            "long_positions": sum(1 for p in self.positions.values() if p.get("direction") == "buy"),
            "short_positions": sum(1 for p in self.positions.values() if p.get("direction") == "sell"),
        }

    def render(self):
        """Render the portfolio manager UI."""
        st.header("📁 Portfolio Manager")
        st.caption("Multi-symbol portfolio tracking")

        # Watchlist
        st.subheader("👁️ Watchlist")
        cols = st.columns(min(len(self.watchlist), 5))
        for i, symbol in enumerate(self.watchlist[:5]):
            with cols[i % 5]:
                st.metric(symbol, "—", help="Connect data source for live prices")

        # Positions
        st.subheader("📊 Open Positions")

        if not self.positions:
            st.info("No open positions. Add a position below.")

            # Add position form
            with st.expander("➕ Add Position"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    symbol = st.selectbox("Symbol", self.watchlist, key="port_symbol")
                with c2:
                    direction = st.selectbox("Direction", ["buy", "sell"], key="port_dir")
                with c3:
                    entry = st.number_input("Entry Price", 0.0, format="%.5f", key="port_entry")
                with c4:
                    lots = st.number_input("Lots", 0.01, 100.0, 0.01, key="port_lots")

                c5, c6 = st.columns(2)
                with c5:
                    sl = st.number_input("Stop Loss", 0.0, format="%.5f", key="port_sl")
                with c6:
                    tp = st.number_input("Take Profit", 0.0, format="%.5f", key="port_tp")

                if st.button("Add Position", key="port_add"):
                    self.add_position(symbol, direction, entry, lots, sl, tp)
                    st.success(f"Added {direction} {symbol}")
                    st.rerun()
        else:
            # Summary
            summary = self.get_portfolio_summary()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Positions", summary["total_positions"])
            with c2:
                st.metric("Total Lots", summary["total_lots"])
            with c3:
                st.metric("Total P&L", f"${summary['total_pnl']:+.2f}")
            with c4:
                st.metric("Long/Short", f"{summary['long_positions']}/{summary['short_positions']}")

            # Position table
            pos_data = []
            for sym, pos in self.positions.items():
                emoji = "🟢" if pos["direction"] == "buy" else "🔴"
                pnl_emoji = "🟢" if pos["pnl"] >= 0 else "🔴"
                pos_data.append({
                    "Symbol": sym,
                    "Direction": f"{emoji} {pos['direction'].upper()}",
                    "Entry": f"{pos['entry']:.5f}",
                    "Current": f"{pos['current_price']:.5f}",
                    "Lots": pos["lots"],
                    "P&L": f"{pnl_emoji} ${pos['pnl']:+.2f}",
                    "SL": f"{pos['sl']:.5f}" if pos["sl"] else "—",
                    "TP": f"{pos['tp']:.5f}" if pos["tp"] else "—",
                })

            st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)

            # Close position
            with st.expander("❌ Close Position"):
                close_sym = st.selectbox("Select Position", list(self.positions.keys()), key="port_close_sym")
                if st.button("Close Position", key="port_close"):
                    self.remove_position(close_sym)
                    st.success(f"Closed {close_sym}")
                    st.rerun()

        # Risk overview
        st.subheader("⚠️ Portfolio Risk")
        total_exposure = sum(p.get("lots", 0) for p in self.positions.values())
        st.progress(min(1.0, total_exposure / 1.0))
        st.caption(f"Total exposure: {total_exposure:.2f} lots")

        if total_exposure > 0.5:
            st.warning("⚠️ High portfolio exposure — consider reducing")
        elif total_exposure > 0.2:
            st.info("ℹ️ Moderate portfolio exposure")
        else:
            st.success("✅ Low portfolio exposure")
