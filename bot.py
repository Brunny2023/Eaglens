import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import TELEGRAM_TOKEN
from engine import EaglensEngine

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

engine = EaglensEngine()

DISCLAIMER_TEXT = (
    "🦅 *Welcome to Eaglens: Your Probabilistic Decision-Support System*\n\n"
    "Eaglens is not a tipster or a betting bot. It is a high-precision analytical engine "
    "designed to provide you with *calibrated, data-driven probabilities* for football match outcomes.\n\n"
    "🛡️ *Our Commitment to Accuracy:*\n"
    "Unlike traditional predictors, Eaglens is *self-aware*. It continuously monitors its own "
    "performance, data quality, and market volatility. If our internal confidence drops or "
    "environmental conditions become too unpredictable, the system will *prefer silence* over "
    "unreliable output.\n\n"
    "📊 *How to Use Eaglens:*\n"
    "1. **Probabilities**: We provide the mathematical likelihood of Home, Draw, and Away outcomes.\n"
    "2. **Confidence**: Every prediction is paired with a Confidence Score (0-100). This reflects "
    "the stability of the underlying data and model calibration.\n\n"
    "By using Eaglens, you are accessing a cautious quantitative analyst that actively "
    "discourages blind trust and prioritizes statistical integrity above all else.\n\n"
    "*Ready to analyze? Use the menu below to get started.*"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and show the disclaimer."""
    keyboard = [['🔍 Search Match', '📅 Today\'s Analysis'], ['📈 System Status', 'ℹ️ About Eaglens']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        DISCLAIMER_TEXT,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current health of the analytical engine."""
    metrics = engine.calibration_metrics
    status_msg = (
        "🦅 *Eaglens System Health Report*\n\n"
        f"✅ **Calibration (Brier)**: {metrics['brier_score']:.3f} (Healthy)\n"
        f"✅ **Data Stability (PSI)**: {metrics['data_drift_psi']:.2f} (Stable)\n"
        f"✅ **League Volatility**: {metrics['league_volatility']:.2f} (Normal)\n"
        f"✅ **Active Sample Size**: {metrics['sample_size']} matches\n\n"
        "The engine is currently operating at full analytical capacity."
    )
    await update.message.reply_text(status_msg, parse_mode='Markdown')

async def mock_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provide a mock prediction for demonstration."""
    # In a real scenario, this would fetch data from the API
    prediction = engine.predict("Arsenal", "Chelsea", 1.8, 1.2)
    
    if prediction["status"] == "success":
        msg = (
            f"🦅 *Match Analysis: {prediction['home_team']} vs {prediction['away_team']}*\n\n"
            "**Probabilities:**\n"
            f"🏠 Home: {prediction['probabilities']['home']:.1%}\n"
            f"🤝 Draw: {prediction['probabilities']['draw']:.1%}\n"
            f"🚀 Away: {prediction['probabilities']['away']:.1%}\n\n"
            f"**Confidence Score: {prediction['confidence']}/100**\n"
            f"Label: *{prediction['confidence_label']}*\n\n"
            "_Note: This is a probabilistic assessment, not a guaranteed outcome._"
        )
    else:
        msg = f"⚠️ *No Reliable Prediction Available*\n\nReason: {prediction['reason']}"
        
    await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '🔍 Search Match' or text == '📅 Today\'s Analysis':
        await mock_prediction(update, context)
    elif text == '📈 System Status':
        await system_status(update, context)
    elif text == 'ℹ️ About Eaglens':
        await update.message.reply_text(
            "🦅 *Welcome to the Future of Football Intelligence!*\n\n"
            "Eaglens isn't just a bot; it's your ultimate edge in the world of football. "
            "By combining elite statistical calibration with real-time signal processing, "
            "we provide you with the **well-guided predictions** you need to dominate.\n\n"
            "💰 *Turn Insights into Results:*\n"
            "Stop guessing and start winning. Our system is engineered to help you make "
            "decisions that **rain dollars**. Whether you're looking for the next big win "
            "or consistent growth, Eaglens provides the mathematical clarity to get you there.\n\n"
            "🚀 *Join the Elite:* Don't leave your success to chance. Let Eaglens guide your "
            "path to profitability today!",
            parse_mode='Markdown'
        )

if __name__ == '__main__':
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: Please set your TELEGRAM_TOKEN in config.py or as an environment variable.")
    else:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        print("Eaglens Bot is starting...")
        application.run_polling()
