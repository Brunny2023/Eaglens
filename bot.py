import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from config import TELEGRAM_TOKEN, PAYSTACK_TRIAL_PRICE, PAYSTACK_MONTHLY_PRICE, OWNER_USERNAME, OWNER_ID
from engine import EaglensEngine
from database import check_user_access, verify_invite_code, init_db, log_visitor, get_all_users
from payments import PaystackManager
from invites import generate_invite_code, notify_owner_of_new_code

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

engine = EaglensEngine()

DISCLAIMER_TEXT = (
    "🦅 *Welcome to Eaglens: Your Probabilistic Decision-Support System*\n\n"
    "Eaglens is a high-precision analytical engine designed to provide you with "
    "*calibrated, data-driven probabilities* for football match outcomes.\n\n"
    "🛡️ *Our Commitment to Accuracy:*\n"
    "Eaglens is *self-aware*. It monitors its own performance and prefers silence over unreliable output.\n\n"
    "💰 *Rain Dollars with Guided Predictions:*\n"
    "Stop guessing and start winning. Our system is engineered to help you make "
    "decisions that **rain dollars**. Let Eaglens guide your path to profitability today!\n\n"
    "⚠️ *Access Restricted*: Eaglens is currently **Invite-Only**."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and check access."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Log visitor
    log_visitor(user_id, username)

    # Update OWNER_ID if the owner interacts
    if username and f"@{username}" == OWNER_USERNAME:
        global OWNER_ID
        OWNER_ID = user_id

    has_access, status = check_user_access(user_id)
    
    if status in ["not_registered", "not_verified"]:
        await update.message.reply_text(
            DISCLAIMER_TEXT + "\n\n*Please enter your Invite Code to proceed:*",
            parse_mode='Markdown'
        )
        context.user_data['awaiting_invite'] = True
        return

    if status in ["not_subscribed", "expired"]:
        keyboard = [
            [InlineKeyboardButton(f"1-Month Trial (${PAYSTACK_TRIAL_PRICE})", callback_data='pay_trial')],
            [InlineKeyboardButton(f"Monthly Subscription (${PAYSTACK_MONTHLY_PRICE})", callback_data='pay_monthly')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🦅 *Subscription Required*\n\nTo access Eaglens predictions and start raining dollars, please select a plan:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    # Active user menu
    keyboard = [['🔍 Search Match', '📅 Today\'s Analysis'], ['📈 System Status', 'ℹ️ About Eaglens']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🦅 *Eaglens Active*\n\nReady to analyze? Use the menu below to get started.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify the invite code provided by the user."""
    if not context.user_data.get('awaiting_invite'):
        return await handle_menu(update, context)
    
    code = update.message.text.strip()
    user_id = update.effective_user.id
    
    if verify_invite_code(user_id, code):
        context.user_data['awaiting_invite'] = False
        await update.message.reply_text(
            "✅ *Invite Verified!*\n\nWelcome to the elite circle. Now, choose your entry plan to start receiving predictions:",
            parse_mode='Markdown'
        )
        # Show payment options
        keyboard = [
            [InlineKeyboardButton(f"1-Month Trial (${PAYSTACK_TRIAL_PRICE})", callback_data='pay_trial')],
            [InlineKeyboardButton(f"Monthly Subscription (${PAYSTACK_MONTHLY_PRICE})", callback_data='pay_monthly')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a plan:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ *Invalid or used invite code.* Please try again or contact support.")

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle plan selection and initialize Paystack transaction."""
    query = update.callback_query
    await query.answer()
    
    plan = query.data.split('_')[1]
    amount = PAYSTACK_TRIAL_PRICE if plan == 'trial' else PAYSTACK_MONTHLY_PRICE
    user_id = query.from_user.id
    email = f"user_{user_id}@eaglens.bot" # Placeholder email
    
    res = PaystackManager.initialize_transaction(email, amount, {"user_id": user_id, "plan": plan})
    
    if res.get('status'):
        auth_url = res['data']['authorization_url']
        ref = res['data']['reference']
        
        keyboard = [[InlineKeyboardButton("💳 Pay Now", url=auth_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🦅 *Payment Initialized*\n\nPlan: {plan.capitalize()}\nAmount: ${amount}\n\n"
            "Click the button below to complete your payment. Once done, use /verify to activate your account.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        context.user_data['last_ref'] = ref
    else:
        await query.edit_message_text("❌ Error initializing payment. Please try again later.")

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually verify payment using the reference."""
    ref = context.user_data.get('last_ref')
    if not ref:
        return await update.message.reply_text("No pending payment found. Use /start to subscribe.")
    
    res = PaystackManager.verify_transaction(ref)
    if res.get('status') and res['data']['status'] == 'success':
        user_id = update.effective_user.id
        plan = res['data']['metadata']['plan']
        expiry = PaystackManager.activate_subscription(user_id, plan)
        
        await update.message.reply_text(
            f"🎉 *Payment Successful!*\n\nYour Eaglens access is now **Active** until {expiry[:10]}.\n"
            "Use /start to open the main menu and start raining dollars! 💰",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⏳ Payment not yet verified. Please complete the payment or try again in a moment.")

async def generate_code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to generate a new multi-use invite code."""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if username and f"@{username}" == OWNER_USERNAME:
        max_uses = 100
        if context.args:
            try:
                max_uses = int(context.args[0])
            except ValueError:
                pass
        
        code = generate_invite_code(max_uses=max_uses)
        await update.message.reply_text(f"✅ Generated code: `{code}` with {max_uses} uses.", parse_mode='Markdown')
        await notify_owner_of_new_code(context, code, max_uses)
    else:
        await update.message.reply_text("❌ Unauthorized. Only the owner can generate codes.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to broadcast a message to all visitors."""
    username = update.effective_user.username
    if not (username and f"@{username}" == OWNER_USERNAME):
        return await update.message.reply_text("❌ Unauthorized.")

    if not context.args:
        return await update.message.reply_text("Usage: `/broadcast Your message here`", parse_mode='Markdown')

    message = " ".join(context.args)
    users = get_all_users()
    count = 0
    
    await update.message.reply_text(f"🚀 Starting broadcast to {len(users)} users...")
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 *Eaglens Broadcast*\n\n{message}", parse_mode='Markdown')
            count += 1
        except Exception as e:
            logging.error(f"Failed to send broadcast to {user_id}: {e}")
    
    await update.message.reply_text(f"✅ Broadcast complete. Sent to {count}/{len(users)} users.")

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu interactions with access check."""
    user_id = update.effective_user.id
    has_access, _ = check_user_access(user_id)
    
    if not has_access:
        return await start(update, context)

    text = update.message.text
    if text in ['🔍 Search Match', '📅 Today\'s Analysis']:
        prediction = engine.predict("Arsenal", "Chelsea", 1.8, 1.2)
        msg = f"🦅 *Match Analysis: {prediction['home_team']} vs {prediction['away_team']}*\n\n" \
              f"🏠 Home: {prediction['probabilities']['home']:.1%}\n" \
              f"🤝 Draw: {prediction['probabilities']['draw']:.1%}\n" \
              f"🚀 Away: {prediction['probabilities']['away']:.1%}\n\n" \
              f"**Confidence: {prediction['confidence']}/100** ({prediction['confidence_label']})"
        await update.message.reply_text(msg, parse_mode='Markdown')
    elif text == '📈 System Status':
        metrics = engine.calibration_metrics
        status_msg = f"🦅 *System Health*\n\n✅ Calibration: {metrics['brier_score']:.3f}\n✅ Stability: {metrics['data_drift_psi']:.2f}"
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    elif text == 'ℹ️ About Eaglens':
        await update.message.reply_text(
            "🦅 *Eaglens: The Future of Football Intelligence*\n\n"
            "We provide well-guided predictions that **rain dollars**. Let Eaglens guide your path to profitability!",
            parse_mode='Markdown'
        )

async def post_init(application):
    """Ensure database is ready and notify owner if possible."""
    init_db()
    logging.info("Eaglens Bot initialized and database ready.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('verify', verify_payment))
    application.add_handler(CommandHandler('gen_code', generate_code_command))
    application.add_handler(CommandHandler('broadcast', broadcast_command))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern='^pay_'))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_invite))
    application.run_polling()
