"""
GoldFX Pro - Ollama AI Interface
Streamlit UI for interacting with local Ollama LLM for trading analysis.
"""

import streamlit as st
import json
import subprocess
from datetime import datetime


def _check_ollama() -> bool:
    """Check if Ollama is running."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def _query_ollama(prompt: str, model: str = "llama3") -> str:
    """Query Ollama with a prompt."""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: Ollama request timed out"
    except FileNotFoundError:
        return "Error: Ollama not found. Install from https://ollama.ai"
    except Exception as e:
        return f"Error: {str(e)}"


def _build_market_context(df) -> str:
    """Build market context string from dataframe for LLM."""
    if df is None or len(df) == 0:
        return "No market data available."

    from ai_engine import analyze_dataframe
    signal = analyze_dataframe(df)

    context = f"""
Current Market Analysis (Gold/XAUUSD):
- Current Price: {signal.get('current_price', 'N/A')}
- RSI (14): {signal.get('rsi', 'N/A')}
- ATR: {signal.get('atr', 'N/A')}
- Trend: {signal.get('trend', {}).get('trend', 'N/A')} (strength: {signal.get('trend', {}).get('strength', 'N/A')})
- AI Signal: {signal.get('signal', 'N/A')} (confidence: {signal.get('confidence', 'N/A')}%)
- Entry: {signal.get('entry', 'N/A')}
- SL: {signal.get('sl', 'N/A')}
- TP1: {signal.get('tp1', 'N/A')} | TP2: {signal.get('tp2', 'N/A')} | TP3: {signal.get('tp3', 'N/A')}
- Support: {signal.get('support_resistance', {}).get('support', [])}
- Resistance: {signal.get('support_resistance', {}).get('resistance', [])}
"""
    return context


def render_ollama_ai():
    """Render the Ollama AI chat interface."""
    st.header("🤖 Ollama AI Assistant")
    st.caption("Chat with local LLM about your trading analysis")

    # Check Ollama availability
    ollama_available = _check_ollama()

    # Model selection
    col1, col2 = st.columns([2, 1])
    with col1:
        model = st.text_input("Model", value="llama3", key="ollama_model",
                              help="Ollama model name (e.g., llama3, mistral, codellama)")
    with col2:
        if ollama_available:
            st.success("✅ Ollama Online")
        else:
            st.error("❌ Ollama Offline")

    # Preset prompts
    st.subheader("📋 Quick Prompts")
    df = st.session_state.get("market_data")

    preset_cols = st.columns(3)
    with preset_cols[0]:
        if st.button("📊 Analyze Market", key="ollama_analyze"):
            ctx = _build_market_context(df)
            prompt = f"""You are a professional forex/gold trader. Based on this market data:
{ctx}
Provide a detailed analysis including:
1. Market condition assessment
2. Key levels to watch
3. Trade recommendation with reasoning
4. Risk factors to consider"""
            st.session_state["ollama_prompt"] = prompt

    with preset_cols[1]:
        if st.button("⚠️ Risk Assessment", key="ollama_risk"):
            ctx = _build_market_context(df)
            prompt = f"""As a risk management expert, analyze this trading setup:
{ctx}
Provide:
1. Position sizing recommendation
2. Risk/reward ratio analysis
3. Potential scenarios (best/worst case)
4. Whether this trade is worth taking"""
            st.session_state["ollama_prompt"] = prompt

    with preset_cols[2]:
        if st.button("📈 Strategy Ideas", key="ollama_strategy"):
            ctx = _build_market_context(df)
            prompt = f"""Based on current gold market conditions:
{ctx}
Suggest 3 different trading strategies:
1. Conservative approach
2. Moderate approach
3. Aggressive approach
Include entry, SL, TP for each."""
            st.session_state["ollama_prompt"] = prompt

    # Chat interface
    st.subheader("💬 Chat")

    # Initialize chat history
    if "ollama_messages" not in st.session_state:
        st.session_state["ollama_messages"] = []

    # Display chat history
    for msg in st.session_state["ollama_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Ask about the market...", key="ollama_input")

    # Handle preset prompt
    if "ollama_prompt" in st.session_state:
        user_input = st.session_state.pop("ollama_prompt")

    if user_input:
        # Show user message
        st.session_state["ollama_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if ollama_available:
                    response = _query_ollama(user_input, model)
                else:
                    # Fallback: use built-in analysis
                    ctx = _build_market_context(df)
                    response = f"""⚠️ Ollama is not available. Here's a basic analysis based on current data:

{ctx}

**Note:** For AI-powered analysis, install and start Ollama:
```
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3
```"""
                st.markdown(response)
                st.session_state["ollama_messages"].append({"role": "assistant", "content": response})

    # Clear chat
    if st.button("🗑️ Clear Chat", key="ollama_clear"):
        st.session_state["ollama_messages"] = []
        st.rerun()
