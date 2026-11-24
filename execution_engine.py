"""
GoldFX Pro - Execution Engine
Handles trade execution logic, order routing, and position management.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class ExecutionMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"
    DEMO = "demo"


class ExecutionEngine:
    """Trade execution engine with paper/live modes."""

    def __init__(self, mode: str = ExecutionMode.PAPER.value):
        self.mode = mode
        self.pending_orders: List[Dict] = []
        self.execution_log: List[Dict] = []
        self.slippage_pips: float = 0.5
        self.spread_pips: float = 3.0

    def set_mode(self, mode: str):
        self.mode = mode

    def execute_market_order(self, symbol: str, direction: str, lots: float, price: float,
                              sl: float = 0, tp: float = 0) -> Dict[str, Any]:
        """Execute a market order."""
        # Apply spread
        if direction == "buy":
            exec_price = price + self.spread_pips * 0.0001
        else:
            exec_price = price - self.spread_pips * 0.0001

        # Apply slippage
        import random
        slippage = random.uniform(0, self.slippage_pips) * 0.0001
        if direction == "buy":
            exec_price += slippage
        else:
            exec_price -= slippage

        result = {
            "order_id": f"EXE-{datetime.now().strftime('%H%M%S')}",
            "symbol": symbol,
            "direction": direction,
            "lots": lots,
            "requested_price": price,
            "execution_price": round(exec_price, 5),
            "slippage": round(slippage * 10000, 2),
            "spread": self.spread_pips,
            "sl": sl,
            "tp": tp,
            "mode": self.mode,
            "status": "filled",
            "timestamp": datetime.now().isoformat(),
        }

        self.execution_log.append(result)

        # Add to trade manager if available
        tm = st.session_state.get("trade_manager")
        if tm:
            from trade_manager import create_trade_order
            order = create_trade_order(
                symbol=symbol,
                order_type=f"{direction}_market",
                entry_price=exec_price,
                stop_loss=sl,
                take_profit_1=tp,
                lot_size=lots,
            )
            tm.add_trade(order)
            result["trade_manager_id"] = order.order_id

        return result

    def execute_pending_order(self, symbol: str, order_type: str, lots: float,
                               entry: float, sl: float = 0, tp: float = 0) -> Dict[str, Any]:
        """Place a pending order (stop/limit)."""
        order = {
            "order_id": f"PEND-{datetime.now().strftime('%H%M%S')}",
            "symbol": symbol,
            "order_type": order_type,
            "lots": lots,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "status": "pending",
            "mode": self.mode,
            "timestamp": datetime.now().isoformat(),
        }
        self.pending_orders.append(order)

        # Add to trade manager
        tm = st.session_state.get("trade_manager")
        if tm:
            from trade_manager import create_trade_order
            trade = create_trade_order(
                symbol=symbol,
                order_type=order_type,
                entry_price=entry,
                stop_loss=sl,
                take_profit_1=tp,
                lot_size=lots,
            )
            tm.add_trade(trade)
            order["trade_manager_id"] = trade.order_id

        return order

    def cancel_order(self, order_id: str) -> bool:
        for i, order in enumerate(self.pending_orders):
            if order["order_id"] == order_id:
                self.pending_orders[i]["status"] = "cancelled"
                return True
        return False

    def check_pending_orders(self, current_price: float) -> List[Dict]:
        """Check if any pending orders should be activated."""
        activated = []
        for order in self.pending_orders:
            if order["status"] != "pending":
                continue

            should_activate = False
            if order["order_type"] == "buy_stop" and current_price >= order["entry"]:
                should_activate = True
            elif order["order_type"] == "sell_stop" and current_price <= order["entry"]:
                should_activate = True
            elif order["order_type"] == "buy_limit" and current_price <= order["entry"]:
                should_activate = True
            elif order["order_type"] == "sell_limit" and current_price >= order["entry"]:
                should_activate = True

            if should_activate:
                result = self.execute_market_order(
                    order["symbol"],
                    "buy" if "buy" in order["order_type"] else "sell",
                    order["lots"],
                    current_price,
                    order.get("sl", 0),
                    order.get("tp", 0),
                )
                order["status"] = "activated"
                activated.append(result)

        return activated

    def get_execution_stats(self) -> Dict[str, Any]:
        if not self.execution_log:
            return {"total_executions": 0}

        slippages = [e.get("slippage", 0) for e in self.execution_log]
        return {
            "total_executions": len(self.execution_log),
            "avg_slippage": round(sum(slippages) / len(slippages), 2),
            "max_slippage": round(max(slippages), 2),
            "pending_orders": sum(1 for o in self.pending_orders if o["status"] == "pending"),
            "mode": self.mode,
        }

    def render(self):
        """Render execution engine UI."""
        st.header("⚡ Execution Engine")
        st.caption("Trade execution with paper/live modes")

        # Mode selector
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox("Execution Mode",
                                [ExecutionMode.PAPER.value, ExecutionMode.DEMO.value, ExecutionMode.LIVE.value],
                                key="exec_mode")
            self.set_mode(mode)
        with col2:
            if mode == ExecutionMode.LIVE.value:
                st.error("🔴 LIVE MODE — Real money at risk!")
            elif mode == ExecutionMode.PAPER.value:
                st.success("🟢 PAPER MODE — No real money")
            else:
                st.warning("🟡 DEMO MODE — Demo account")

        # Settings
        with st.expander("⚙️ Execution Settings"):
            c1, c2 = st.columns(2)
            with c1:
                self.spread_pips = st.number_input("Spread (pips)", 0.1, 10.0, 3.0, 0.1, key="exec_spread")
            with c2:
                self.slippage_pips = st.number_input("Max Slippage (pips)", 0.0, 5.0, 0.5, 0.1, key="exec_slip")

        # Quick execution
        st.subheader("🚀 Quick Execute")
        df = st.session_state.get("market_data")
        default_price = 0.0
        if df is not None and len(df) > 0:
            default_price = float(df["close"].iloc[-1])

        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            symbol = st.text_input("Symbol", "XAUUSD", key="exec_symbol")
        with qc2:
            lots = st.number_input("Lots", 0.01, 100.0, 0.01, key="exec_lots")
        with qc3:
            sl = st.number_input("SL", 0.0, format="%.5f", key="exec_sl")
        with qc4:
            tp = st.number_input("TP", 0.0, format="%.5f", key="exec_tp")

        bc1, bc2 = st.columns(2)
        with bc1:
            if st.button("🟢 BUY", key="exec_buy", type="primary", use_container_width=True):
                result = self.execute_market_order(symbol, "buy", lots, default_price, sl, tp)
                st.success(f"✅ BUY filled @ {result['execution_price']:.5f} (slip: {result['slippage']} pips)")
                st.json(result)
        with bc2:
            if st.button("🔴 SELL", key="exec_sell", type="primary", use_container_width=True):
                result = self.execute_market_order(symbol, "sell", lots, default_price, sl, tp)
                st.success(f"✅ SELL filled @ {result['execution_price']:.5f} (slip: {result['slippage']} pips)")
                st.json(result)

        # Execution log
        stats = self.get_execution_stats()
        st.subheader(f"📋 Execution Log ({stats.get('total_executions', 0)} trades)")
        if self.execution_log:
            log_data = [{
                "ID": e["order_id"],
                "Symbol": e["symbol"],
                "Side": e["direction"].upper(),
                "Lots": e["lots"],
                "Price": f"{e['execution_price']:.5f}",
                "Slippage": f"{e['slippage']} pips",
                "Time": e["timestamp"][:19],
            } for e in self.execution_log[-20:]]
            st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
        else:
            st.info("No executions yet")
