# GoldFX Pro

AI-powered gold & forex analysis platform built with Python and Streamlit.

GoldFX Pro combines classical technical analysis, modern price-action concepts, and multiple AI models in a single dashboard to help traders analyze XAU/USD and major forex pairs across all timeframes (M5 to weekly).

> **Disclaimer:** This project is for educational and research purposes only. It is not financial advice. Trading carries a high level of risk.

## Features

- **30+ analysis tabs** in a Streamlit interface (Arabic-language UI)
- **16 technical analysis engines** covering:
  - Classical chart patterns and candlestick patterns
  - Harmonic patterns
  - SMC / ICT concepts
  - Elliott Wave
- **Multi-model AI integration:** Ollama (local), OpenRouter, Groq, Gemini, and others
- **ICT Pro tab:** full recommendations across timeframes from M5 to weekly
- **Candle scanner tab** with historical statistics
- **Volume analysis:** buyer vs. seller volume linked to liquidity zones
- **Three-level cache system** for faster repeated analysis
- **Per-pair memory** with pattern tracking
- **Prompt management system** for customizing AI prompts
- **Signal validation methodology:** signal ledger, no-lookahead labeling, and independent-window validation (Brier skill score vs. base rate, bootstrap confidence intervals)
- **MT4/MT5 data integration**

## Tech Stack

- Python 3.12
- Streamlit
- pandas / NumPy
- LLM providers via API or local Ollama

## Installation

```bash
git clone https://github.com/nasserfa100-ctrl/goldfx-pro.git
cd goldfx-pro
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (it is already ignored by git) and add your own API keys:

```
OPENROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

Never commit API keys or account credentials to the repository.

## Run

```bash
streamlit run app.py
```

## Project Status

Actively developed, with ongoing work on volume analysis, the ICT Pro tab, and signal validation.

## Contributing

Issues and pull requests are welcome. Please open an issue first to discuss major changes.

## License

Released under the [MIT License](LICENSE).

