# Eaglens: Football Prediction Decision-Support System

Eaglens is a production-ready Telegram bot designed as a self-aware probabilistic decision-support system for football match outcomes. It prioritizes statistical integrity and calibration over high-volume predictions.

## Core Principles
- **Probability ≠ Confidence**: Every prediction includes both the mathematical likelihood and a confidence score based on model health.
- **Self-Awareness**: The system monitors its own calibration (Brier score), data drift (PSI), and performance.
- **Silence is a Feature**: If reliability thresholds are not met, the system suppresses predictions rather than providing unreliable data.

## Features
- **Probabilistic Outcomes**: Home/Draw/Away distributions.
- **Multi-Layer Gating**: 5 hard gates to ensure prediction reliability.
- **News-to-Signal Engine**: Adjusts probabilities based on classified news (Lineups, Tactics, etc.).
- **Assumption Registry**: Continuously validates core predictive assumptions.

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Football-Data.org API Key (from [football-data.org](https://www.football-data.org/))

### 2. Installation
```bash
# Clone the repository (or copy the files)
mkdir eaglens_bot && cd eaglens_bot

# Install dependencies
pip install python-telegram-bot requests pandas numpy scikit-learn scipy
```

### 3. Configuration
Edit `config.py` and replace the placeholders with your actual tokens:
```python
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
FOOTBALL_DATA_API_KEY = "YOUR_FOOTBALL_DATA_API_KEY"
```

### 4. Running the Bot
```bash
python bot.py
```

## Accuracy Disclaimer
Upon starting the bot, users are presented with a confidence-building disclaimer that emphasizes the system's analytical rigor and commitment to data integrity. It positions the bot as a "cautious quantitative analyst" rather than a gambling tool.
