"""
GoldFX Pro - Trade Manager
Professional trade management system with order lifecycle, Plan B, trailing stops, and JSON persistence.
"""

import json
import os
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime


# ─── Enums ────────────────────────────────────────────────────────────────────

class OrderType(str, Enum):
    BUY_MARKET = "buy_market"
    SELL_MARKET = "sell_market"
    BUY_STOP = "buy_stop"
    SELL_STOP = "sell_stop"
    BUY_LIMIT = "buy_limit"
    SELL_LIMIT = "sell_limit"

    @property
    def emoji(self) -> str:
        _map = {
            "buy_market": "🟢", "sell_market": "🔴",
            "buy_stop": "🟩", "sell_stop": "🟥",
            "buy_limit": "🔵", "sell_limit": "🟠",
        }
        return _map.get(self.value, "⚪")


class TradeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"

    @property
    def arabic(self) -> str:
        _map = {"pending": "قيد الانتظار", "active": "نشطة", "closed": "مغلقة", "cancelled": "ملغاة"}
        return _map.get(self.value, self.value)


class TrailingMode(str, Enum):
    NONE = "none"
    ATR = "atr"
    PERCENT = "percent"


# ─── Trade Order ──────────────────────────────────────────────────────────────

@dataclass
class TradeOrder:
    order_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    symbol: str = "XAUUSD"
    order_type: str = OrderType.BUY_MARKET.value
    status: str = TradeStatus.PENDING.value
    entry_price: float = 0.0
    current_price: float = 0.0
    stop_loss: float = 0.0
    take_profit_1: float = 0.0
    take_profit_2: float = 0.0
    take_profit_3: float = 0.0
    lot_size: float = 0.01
    pnl: float = 0.0
    pnl_pips: float = 0.0
    trailing_mode: str = TrailingMode.NONE.value
    trailing_distance: float = 0.0
    trailing_stop: float = 0.0

    # Plan B: reverse trade on SL hit
    plan_b_enabled: bool = False
    plan_b_order_type: str = ""
    plan_b_lot_size: float = 0.01
    plan_b_sl: float = 0.0
    plan_b_tp: float = 0.0

    # Metadata
    created_at: str = ""
    activated_at: str = ""
    closed_at: str = ""
    close_reason: str = ""
    close_price: float = 0.0
    notes: str = ""
    ai_signal: str = ""
    ai_confidence: int = 0
    risk_reward: float = 0.0
    actions: list = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    # ── Properties expected by app.py ──

    @property
    def trade_id(self) -> str:
        return self.order_id

    @property
    def direction(self) -> str:
        if "buy" in self.order_type:
            return "BUY"
        return "SELL"

    @property
    def plan_b(self):
        """Return a namespace so app.py can do trade.plan_b.enabled / .activated."""
        class _PlanB:
            def __init__(self, trade):
                self.enabled = trade.plan_b_enabled
                self.activated = bool(trade.plan_b_order_type and trade.status == TradeStatus.ACTIVE.value)
        return _PlanB(self)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TradeOrder":
        # Filter to only known fields
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})


# ─── Helper ───────────────────────────────────────────────────────────────────

def create_trade_order(
    symbol: str = "XAUUSD",
    order_type: str = OrderType.BUY_MARKET.value,
    entry_price: float = 0.0,
    stop_loss: float = 0.0,
    take_profit_1: float = 0.0,
    take_profit_2: float = 0.0,
    take_profit_3: float = 0.0,
    lot_size: float = 0.01,
    trailing_mode: str = TrailingMode.NONE.value,
    trailing_distance: float = 0.0,
    plan_b_enabled: bool = False,
    plan_b_order_type: str = "",
    plan_b_lot_size: float = 0.01,
    plan_b_sl: float = 0.0,
    plan_b_tp: float = 0.0,
    ai_signal: str = "",
    ai_confidence: int = 0,
    notes: str = "",
) -> TradeOrder:
    """Create a new trade order with all parameters."""
    # Auto-detect plan_b_order_type if not specified
    if plan_b_enabled and not plan_b_order_type:
        if "buy" in order_type:
            plan_b_order_type = OrderType.SELL_MARKET.value
        else:
            plan_b_order_type = OrderType.BUY_MARKET.value

    # Calculate risk/reward
    rr = 0.0
    if stop_loss and take_profit_1 and entry_price:
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit_1 - entry_price)
        if risk > 0:
            rr = round(reward / risk, 2)

    order = TradeOrder(
        symbol=symbol,
        order_type=order_type,
        entry_price=entry_price,
        current_price=entry_price,
        stop_loss=stop_loss,
        take_profit_1=take_profit_1,
        take_profit_2=take_profit_2,
        take_profit_3=take_profit_3,
        lot_size=lot_size,
        trailing_mode=trailing_mode,
        trailing_distance=trailing_distance,
        plan_b_enabled=plan_b_enabled,
        plan_b_order_type=plan_b_order_type,
        plan_b_lot_size=plan_b_lot_size,
        plan_b_sl=plan_b_sl,
        plan_b_tp=plan_b_tp,
        ai_signal=ai_signal,
        ai_confidence=ai_confidence,
        risk_reward=rr,
        notes=notes,
    )

    # Market orders activate immediately
    if "market" in order_type:
        order.status = TradeStatus.ACTIVE.value
        order.activated_at = datetime.now().isoformat()

    return order


# ─── Trade Manager ────────────────────────────────────────────────────────────

class TradeManager:
    """Professional trade management with JSON persistence."""

    def __init__(self, filepath: str = "trades.json"):
        self.filepath = filepath
        self.trades: Dict[str, TradeOrder] = {}
        self.history: List[Dict] = []
        self._load()

    # ── Persistence ──

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                for tid, tdata in data.get("trades", {}).items():
                    self.trades[tid] = TradeOrder.from_dict(tdata)
                self.history = data.get("history", [])
            except (json.JSONDecodeError, Exception):
                self.trades = {}
                self.history = []

    def _save(self):
        data = {
            "trades": {tid: t.to_dict() for tid, t in self.trades.items()},
            "history": self.history,
            "last_updated": datetime.now().isoformat(),
        }
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    # ── CRUD ──

    def add_trade(self, order: TradeOrder) -> str:
        self.trades[order.order_id] = order
        self._save()
        return order.order_id

    def get_trade(self, order_id: str) -> Optional[TradeOrder]:
        return self.trades.get(order_id)

    def get_active_trades(self) -> List[TradeOrder]:
        return [t for t in self.trades.values() if t.status == TradeStatus.ACTIVE.value]

    def get_pending_trades(self) -> List[TradeOrder]:
        return [t for t in self.trades.values() if t.status == TradeStatus.PENDING.value]

    def get_closed_trades(self) -> List[TradeOrder]:
        return [t for t in self.trades.values() if t.status == TradeStatus.CLOSED.value]

    def cancel_trade(self, order_id: str) -> bool:
        if order_id in self.trades:
            self.trades[order_id].status = TradeStatus.CANCELLED.value
            self.trades[order_id].closed_at = datetime.now().isoformat()
            self.trades[order_id].close_reason = "cancelled"
            self._save()
            return True
        return False

    def close_trade(self, order_id: str, close_price: float, reason: str = "manual") -> bool:
        if order_id not in self.trades:
            return False
        trade = self.trades[order_id]
        trade.status = TradeStatus.CLOSED.value
        trade.closed_at = datetime.now().isoformat()
        trade.close_price = close_price
        trade.close_reason = reason

        # Calculate final P&L
        if "buy" in trade.order_type:
            trade.pnl = round((close_price - trade.entry_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((close_price - trade.entry_price) * 10000, 1)
        else:
            trade.pnl = round((trade.entry_price - close_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((trade.entry_price - close_price) * 10000, 1)

        # Archive to history
        self.history.append({
            "order_id": trade.order_id,
            "symbol": trade.symbol,
            "order_type": trade.order_type,
            "entry_price": trade.entry_price,
            "close_price": close_price,
            "pnl": trade.pnl,
            "pnl_pips": trade.pnl_pips,
            "close_reason": reason,
            "opened_at": trade.activated_at or trade.created_at,
            "closed_at": trade.closed_at,
            "lot_size": trade.lot_size,
        })

        self._save()
        return True

    # ── Live Update (single trade — used by app.py) ──

    def update_price(self, trade_id: str, current_price: float) -> dict:
        """Update a single trade by ID. Returns {"events": [...]}."""
        trade = self.trades.get(trade_id)
        if not trade:
            return {"events": []}

        if trade.status == TradeStatus.PENDING.value:
            activated = self._check_pending_activation(trade, current_price)
            if activated:
                trade.status = TradeStatus.ACTIVE.value
                trade.activated_at = datetime.now().isoformat()
                self._save()
            return {"events": []}

        if trade.status != TradeStatus.ACTIVE.value:
            return {"events": []}

        trade.current_price = current_price

        # Calculate P&L
        if "buy" in trade.order_type:
            trade.pnl = round((current_price - trade.entry_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((current_price - trade.entry_price) * 10000, 1)
        else:
            trade.pnl = round((trade.entry_price - current_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((trade.entry_price - current_price) * 10000, 1)

        # Update trailing stop
        self._update_trailing(trade, current_price)

        # Check SL/TP
        events = []
        hit = self._check_sl_tp(trade, current_price)
        if hit:
            self.close_trade(trade_id, current_price, hit)
            if hit == "stop_loss":
                events.append("sl_hit")
            else:
                events.append(hit)
            self._save()
        else:
            self._save()

        return {"events": events}

    def activate_plan_b(self, trade_id: str):
        """Execute Plan B by trade ID. Returns new TradeOrder or None."""
        trade = self.trades.get(trade_id)
        if not trade:
            return None
        return self.execute_plan_b(trade)

    # ── Live Update (all trades) ──

    def update_prices(self, current_price: float):
        """Update all active trades with current price. Handles SL/TP hits, trailing stops, Plan B."""
        to_close = []
        to_activate = []

        for tid, trade in self.trades.items():
            if trade.status == TradeStatus.PENDING.value:
                # Check pending order activation
                activated = self._check_pending_activation(trade, current_price)
                if activated:
                    to_activate.append(tid)
                continue

            if trade.status != TradeStatus.ACTIVE.value:
                continue

            trade.current_price = current_price

            # Calculate P&L
            if "buy" in trade.order_type:
                trade.pnl = round((current_price - trade.entry_price) * trade.lot_size * 100, 2)
                trade.pnl_pips = round((current_price - trade.entry_price) * 10000, 1)
            else:
                trade.pnl = round((trade.entry_price - current_price) * trade.lot_size * 100, 2)
                trade.pnl_pips = round((trade.entry_price - current_price) * 10000, 1)

            # Update trailing stop
            self._update_trailing(trade, current_price)

            # Check SL/TP
            hit = self._check_sl_tp(trade, current_price)
            if hit:
                to_close.append((tid, current_price, hit))

        # Apply pending activations
        for tid in to_activate:
            t = self.trades[tid]
            t.status = TradeStatus.ACTIVE.value
            t.activated_at = datetime.now().isoformat()

        # Apply closures
        for tid, price, reason in to_close:
            self.close_trade(tid, price, reason)

        if to_close or to_activate:
            self._save()

    def _check_pending_activation(self, trade: TradeOrder, price: float) -> bool:
        if trade.order_type == OrderType.BUY_STOP.value:
            return price >= trade.entry_price
        elif trade.order_type == OrderType.SELL_STOP.value:
            return price <= trade.entry_price
        elif trade.order_type == OrderType.BUY_LIMIT.value:
            return price <= trade.entry_price
        elif trade.order_type == OrderType.SELL_LIMIT.value:
            return price >= trade.entry_price
        return False

    def _update_trailing(self, trade: TradeOrder, price: float):
        if trade.trailing_mode == TrailingMode.NONE.value:
            return

        if "buy" in trade.order_type:
            if trade.trailing_mode == TrailingMode.PERCENT.value:
                dist = price * trade.trailing_distance / 100
            else:  # ATR
                dist = trade.trailing_distance
            new_stop = price - dist
            if new_stop > trade.stop_loss:
                trade.stop_loss = round(new_stop, 5)
                trade.trailing_stop = round(new_stop, 5)
        else:
            if trade.trailing_mode == TrailingMode.PERCENT.value:
                dist = price * trade.trailing_distance / 100
            else:
                dist = trade.trailing_distance
            new_stop = price + dist
            if new_stop < trade.stop_loss:
                trade.stop_loss = round(new_stop, 5)
                trade.trailing_stop = round(new_stop, 5)

    def _check_sl_tp(self, trade: TradeOrder, price: float) -> Optional[str]:
        is_buy = "buy" in trade.order_type

        # Check SL
        if is_buy and trade.stop_loss and price <= trade.stop_loss:
            return "stop_loss"
        if not is_buy and trade.stop_loss and price >= trade.stop_loss:
            return "stop_loss"

        # Check TPs
        for tp_attr in ["take_profit_1", "take_profit_2", "take_profit_3"]:
            tp = getattr(trade, tp_attr, 0)
            if not tp:
                continue
            if is_buy and price >= tp:
                return f"take_profit ({tp_attr})"
            if not is_buy and price <= tp:
                return f"take_profit ({tp_attr})"

        return None

    # ── Plan B ──

    def execute_plan_b(self, original_trade: TradeOrder) -> Optional[TradeOrder]:
        """Execute Plan B: reverse trade after SL hit."""
        if not original_trade.plan_b_enabled:
            return None

        new_order = create_trade_order(
            symbol=original_trade.symbol,
            order_type=original_trade.plan_b_order_type,
            entry_price=original_trade.current_price,
            stop_loss=original_trade.plan_b_sl,
            take_profit_1=original_trade.plan_b_tp,
            lot_size=original_trade.plan_b_lot_size,
            ai_signal="Plan B",
            notes=f"Plan B from {original_trade.order_id}",
        )
        self.add_trade(new_order)
        return new_order

    # ── Stats ──

    def get_trade_summary(self) -> Dict[str, Any]:
        return self.get_stats()

    def get_trade_summary(self) -> Dict[str, Any]:
        return self.get_stats()

    def get_trade_summary(self) -> Dict[str, Any]:
        return self.get_stats()

    def get_trade_summary(self) -> Dict[str, Any]:
        return self.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        closed = self.get_closed_trades()
        if not closed:
            return {"total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}

        wins = [t for t in closed if t.pnl > 0]
        losses = [t for t in closed if t.pnl <= 0]

        return {
            "total_trades": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
            "total_pnl": round(sum(t.pnl for t in closed), 2),
            "avg_win": round(sum(t.pnl for t in wins) / len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t.pnl for t in losses) / len(losses), 2) if losses else 0,
            "best_trade": max((t.pnl for t in closed), default=0),
            "worst_trade": min((t.pnl for t in closed), default=0),
            "active_count": len(self.get_active_trades()),
            "pending_count": len(self.get_pending_trades()),
        }

    def get_trade_summary(self) -> Dict[str, Any]:
        """Alias for get_stats() — used by app.py history tab."""
        return self.get_stats()


# ─── Streamlit Rendering ─────────────────────────────────────────────────────

def render_trade_card(trade: TradeOrder):
    """Render a single trade as a styled card."""
    import streamlit as st
    status_colors = {
        "pending": "🟡",
        "active": "🟢",
        "closed": "⚫",
        "cancelled": "🔴",
    }
    emoji = status_colors.get(trade.status, "⚪")
    pnl_color = "🟢" if trade.pnl >= 0 else "🔴"

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        with col1:
            st.markdown(f"**{emoji} {trade.order_id}** — {trade.symbol}")
            st.caption(f"Type: {trade.order_type} | Status: {trade.status}")

        with col2:
            st.metric("Entry", f"{trade.entry_price:.5f}")
            st.caption(f"Current: {trade.current_price:.5f}")

        with col3:
            st.metric("P&L", f"${trade.pnl:+.2f}", delta=f"{trade.pnl_pips:+.1f} pips")

        with col4:
            if trade.status == "active":
                if st.button("❌", key=f"close_{trade.order_id}"):
                    return "close"
            elif trade.status == "pending":
                if st.button("🗑️", key=f"cancel_{trade.order_id}"):
                    return "cancel"

        # SL/TP row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.caption(f"SL: {trade.stop_loss:.5f}")
        with c2:
            st.caption(f"TP1: {trade.take_profit_1:.5f}")
        with c3:
            st.caption(f"TP2: {trade.take_profit_2:.5f}")
        with c4:
            st.caption(f"TP3: {trade.take_profit_3:.5f}")

        # Plan B indicator
        if trade.plan_b_enabled:
            st.caption(f"🔄 Plan B: {trade.plan_b_order_type} @ {trade.plan_b_sl:.5f}")

        # Trailing stop
        if trade.trailing_mode != "none":
            st.caption(f"📏 Trailing: {trade.trailing_mode} ({trade.trailing_distance})")

    return None


def render_trade_summary_html(trade: TradeOrder) -> str:
    """Render trade summary as HTML string."""
    pnl_color = "#4CAF50" if trade.pnl >= 0 else "#F44336"
    return f"""
    <div style="border:1px solid #333; border-radius:8px; padding:12px; margin:8px 0; background:#1a1a2e;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong style="color:#fff;">{trade.order_id}</strong>
                <span style="color:#888;"> — {trade.symbol} — {trade.order_type}</span>
            </div>
            <div style="color:{pnl_color}; font-size:1.2em; font-weight:bold;">
                ${trade.pnl:+.2f} ({trade.pnl_pips:+.1f} pips)
            </div>
        </div>
        <div style="color:#aaa; margin-top:8px;">
            Entry: {trade.entry_price:.5f} | SL: {trade.stop_loss:.5f} | TP1: {trade.take_profit_1:.5f}
        </div>
        <div style="color:#666; margin-top:4px;">
            Status: {trade.status} | R:R: {trade.risk_reward:.1f} | Lot: {trade.lot_size}
        </div>
    </div>
    """


def render_trade_panel_streamlit():
    """Render the full trade management panel in Streamlit."""
    import streamlit as st
    st.header("💼 Trade Manager")
    st.caption("Professional trade management with Plan B and trailing stops")

    # Initialize manager
    if "trade_manager" not in st.session_state:
        st.session_state["trade_manager"] = TradeManager("trades.json")
    tm: TradeManager = st.session_state["trade_manager"]

    # Stats bar
    stats = tm.get_stats()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Active", stats.get("active_count", 0))
    with c2:
        st.metric("Pending", stats.get("pending_count", 0))
    with c3:
        st.metric("Total P&L", f"${stats.get('total_pnl', 0):+.2f}")
    with c4:
        st.metric("Win Rate", f"{stats.get('win_rate', 0):.1f}%")
    with c5:
        st.metric("Total Trades", stats.get("total_trades", 0))

    # New order form
    with st.expander("➕ New Order", expanded=False):
        df = st.session_state.get("market_data")
        default_price = 0.0
        if df is not None and len(df) > 0:
            default_price = float(df["close"].iloc[-1])

        col1, col2, col3 = st.columns(3)
        with col1:
            order_type = st.selectbox("Order Type", [e.value for e in OrderType], key="tm_order_type")
            symbol = st.text_input("Symbol", "XAUUSD", key="tm_symbol")
            lot_size = st.number_input("Lot Size", 0.01, 100.0, 0.01, 0.01, key="tm_lot")
        with col2:
            entry_price = st.number_input("Entry Price", value=default_price, format="%.5f", key="tm_entry")
            stop_loss = st.number_input("Stop Loss", value=0.0, format="%.5f", key="tm_sl")
            take_profit_1 = st.number_input("Take Profit 1", value=0.0, format="%.5f", key="tm_tp1")
        with col3:
            take_profit_2 = st.number_input("Take Profit 2", value=0.0, format="%.5f", key="tm_tp2")
            take_profit_3 = st.number_input("Take Profit 3", value=0.0, format="%.5f", key="tm_tp3")
            notes = st.text_input("Notes", "", key="tm_notes")

        # Trailing stop
        st.markdown("**Trailing Stop**")
        tc1, tc2 = st.columns(2)
        with tc1:
            trailing_mode = st.selectbox("Mode", [e.value for e in TrailingMode], key="tm_trail_mode")
        with tc2:
            trailing_distance = st.number_input("Distance", 0.0, 1000.0, 0.0, 0.1, key="tm_trail_dist")

        # Plan B
        st.markdown("**Plan B (Reverse on SL Hit)**")
        plan_b_enabled = st.toggle("Enable Plan B", key="tm_planb")
        pb1, pb2, pb3 = st.columns(3)
        with pb1:
            plan_b_type = st.selectbox("Plan B Type", [e.value for e in OrderType], key="tm_planb_type")
        with pb2:
            plan_b_lot = st.number_input("Plan B Lot", 0.01, 100.0, 0.01, 0.01, key="tm_planb_lot")
        with pb3:
            plan_b_sl = st.number_input("Plan B SL", 0.0, format="%.5f", key="tm_planb_sl")
        plan_b_tp = st.number_input("Plan B TP", 0.0, format="%.5f", key="tm_planb_tp")

        if st.button("🚀 Place Order", key="tm_place", type="primary"):
            order = create_trade_order(
                symbol=symbol,
                order_type=order_type,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit_1=take_profit_1,
                take_profit_2=take_profit_2,
                take_profit_3=take_profit_3,
                lot_size=lot_size,
                trailing_mode=trailing_mode,
                trailing_distance=trailing_distance,
                plan_b_enabled=plan_b_enabled,
                plan_b_order_type=plan_b_type,
                plan_b_lot_size=plan_b_lot,
                plan_b_sl=plan_b_sl,
                plan_b_tp=plan_b_tp,
                notes=notes,
            )
            oid = tm.add_trade(order)
            st.success(f"✅ Order placed: {oid}")
            st.rerun()

    # Tabs for active/pending/closed
    tab1, tab2, tab3 = st.tabs(["🟢 Active", "🟡 Pending", "📜 History"])

    with tab1:
        active = tm.get_active_trades()
        if not active:
            st.info("No active trades")
        for trade in active:
            action = render_trade_card(trade)
            if action == "close":
                tm.close_trade(trade.order_id, trade.current_price, "manual_close")
                st.rerun()

    with tab2:
        pending = tm.get_pending_trades()
        if not pending:
            st.info("No pending orders")
        for trade in pending:
            action = render_trade_card(trade)
            if action == "cancel":
                tm.cancel_trade(trade.order_id)
                st.rerun()

    with tab3:
        closed = tm.get_closed_trades()
        if not closed:
            st.info("No closed trades")
        for trade in closed[-20:]:  # Last 20
            st.markdown(render_trade_summary_html(trade), unsafe_allow_html=True)

    # Price update simulation
    if st.button("🔄 Update Prices", key="tm_update"):
        df = st.session_state.get("market_data")
        if df is not None and len(df) > 0:
            current = float(df["close"].iloc[-1])
            tm.update_prices(current)
            st.success(f"Prices updated to {current:.5f}")
            st.rerun()
