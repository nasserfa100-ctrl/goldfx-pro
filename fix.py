import re

# ── Fix app.py ──
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove old fix if exists (search for our wrapper pattern)
# We need to find and replace the entire block from analyze_dataframe to display_analysis(wrapped)
pattern = r'            result = analyze_dataframe\(ai_df, lookback=lookback, sl_mode=sl_mode\).*?display_analysis\(wrapped\)'

replacement = '''            result = analyze_dataframe(ai_df, lookback=lookback, sl_mode=sl_mode)
            tf_label = "H1"
            trend = result.get("trend", {})
            sr = result.get("support_resistance", {})
            sig_data = None
            if result.get("signal") and result["signal"] != "WAIT":
                sig_data = {
                    "trade_type": "Buy" if result["signal"] == "BUY" else "Sell",
                    "confidence": result.get("confidence", 50) / 100,
                    "entry_price": result.get("entry", 0),
                    "stop_loss": result.get("sl", 0),
                    "take_profit": result.get("tp1", 0),
                    "reason": " | ".join(result.get("reasons", [])),
                    "timeframe": tf_label,
                    "strategy": "AI Engine",
                }
            wrapped = {
                "summary": {
                    "base_timeframe": tf_label,
                    "current_price": result.get("current_price", 0),
                    "analyzed_timeframes": [tf_label],
                    "total_signals": 1 if sig_data else 0,
                },
                "timeframes": {
                    tf_label: {
                        "trend": trend.get("trend", "neutral").lower(),
                        "rsi": result.get("rsi", 0),
                        "rsi_signal": "overbought" if result.get("rsi", 50) > 70 else ("oversold" if result.get("rsi", 50) < 30 else "neutral"),
                        "atr": result.get("atr", 0),
                        "trend_strength": trend.get("strength", 0) / 100,
                        "support_levels": sr.get("support", []),
                        "resistance_levels": sr.get("resistance", []),
                        "signal": sig_data,
                    },
                },
                "signals": [sig_data] if sig_data else [],
            }
            display_analysis(wrapped)'''

# Try regex replace first (handles old fix)
code_new = re.sub(pattern, replacement, code, flags=re.DOTALL)
if code_new != code:
    code = code_new
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ app.py — تم إصلاحه (regex)")
else:
    # Try simple string replace for original code
    old_simple = '            result = analyze_dataframe(ai_df, lookback=lookback, sl_mode=sl_mode)\n            display_analysis(result)'
    if old_simple in code:
        code = code.replace(old_simple, replacement)
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(code)
        print("✅ app.py — تم إصلاحه (simple)")
    else:
        print("⚠️ app.py — لم يتم العثور على النص")

# ── Fix ai_engine.py ──
with open("ai_engine.py", "r", encoding="utf-8") as f:
    code2 = f.read()

old2 = '    df = df.copy()\n    for col in ["open", "high", "low", "close"]:'
new2 = '    df = df.copy()\n    df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]\n    for col in ["open", "high", "low", "close"]:'

if old2 in code2:
    code2 = code2.replace(old2, new2)
    with open("ai_engine.py", "w", encoding="utf-8") as f:
        f.write(code2)
    print("✅ ai_engine.py — تم إصلاحه")
else:
    print("⚠️ ai_engine.py — لم يتم العثور على النص (ربما معدّل مسبقاً)")

# ── Fix trade_manager.py ──
with open("trade_manager.py", "r", encoding="utf-8") as f:
    code3 = f.read()

fixes = 0

old3a = 'return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}'
new3a = 'return {"total_trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "total_pnl": 0}'
if old3a in code3:
    code3 = code3.replace(old3a, new3a)
    fixes += 1

old3b = '''class OrderType(str, Enum):
    BUY_MARKET = "buy_market"
    SELL_MARKET = "sell_market"
    BUY_STOP = "buy_stop"
    SELL_STOP = "sell_stop"
    BUY_LIMIT = "buy_limit"
    SELL_LIMIT = "sell_limit"


class TradeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"'''

new3b = '''class OrderType(str, Enum):
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
        return _map.get(self.value, self.value)'''

if old3b in code3:
    code3 = code3.replace(old3b, new3b)
    fixes += 1

old3c = '''    ai_confidence: int = 0
    risk_reward: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:'''

new3c = '''    ai_confidence: int = 0
    risk_reward: float = 0.0
    actions: list = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

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
        class _PlanB:
            def __init__(self, trade):
                self.enabled = trade.plan_b_enabled
                self.activated = bool(trade.plan_b_order_type and trade.status == TradeStatus.ACTIVE.value)
        return _PlanB(self)

    def to_dict(self) -> dict:'''

if old3c in code3:
    code3 = code3.replace(old3c, new3c)
    fixes += 1

old3d = '    # ── Live Update ──\n\n    def update_prices(self, current_price: float):'

new3d = '''    # ── Live Update (single trade) ──

    def update_price(self, trade_id: str, current_price: float) -> dict:
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
        if "buy" in trade.order_type:
            trade.pnl = round((current_price - trade.entry_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((current_price - trade.entry_price) * 10000, 1)
        else:
            trade.pnl = round((trade.entry_price - current_price) * trade.lot_size * 100, 2)
            trade.pnl_pips = round((trade.entry_price - current_price) * 10000, 1)
        self._update_trailing(trade, current_price)
        events = []
        hit = self._check_sl_tp(trade, current_price)
        if hit:
            self.close_trade(trade_id, current_price, hit)
            events.append("sl_hit" if hit == "stop_loss" else hit)
            self._save()
        else:
            self._save()
        return {"events": events}

    def activate_plan_b(self, trade_id: str):
        trade = self.trades.get(trade_id)
        if not trade:
            return None
        return self.execute_plan_b(trade)

    # ── Live Update (all trades) ──

    def update_prices(self, current_price: float):'''

if old3d in code3:
    code3 = code3.replace(old3d, new3d)
    fixes += 1

old3e = '    def get_stats(self) -> Dict[str, Any]:'
new3e = '''    def get_trade_summary(self) -> Dict[str, Any]:
        return self.get_stats()

    def get_stats(self) -> Dict[str, Any]:'''
if old3e in code3:
    code3 = code3.replace(old3e, new3e)
    fixes += 1

if fixes > 0:
    with open("trade_manager.py", "w", encoding="utf-8") as f:
        f.write(code3)
    print(f"✅ trade_manager.py — تم إصلاح {fixes} مشاكل")
else:
    print("⚠️ trade_manager.py — لم يتم العثور على نصوص الإصلاح (ربما معدّل مسبقاً)")

print("\n🎉 تم الانتهاء! شغّل: streamlit run app.py")
