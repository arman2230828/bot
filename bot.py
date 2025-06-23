import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Bot Token
BOT_TOKEN = "7986275346:AAG_TBcb3qP151eNUs9DQ00mPO0hXxbnLV8"

# Required Channels
REQUIRED_CHANNELS = [
    "@jsbbsksna", "@kanvsujs",
    "@nabbjshbs", "@kshbbsks",
    "@kalaEarn", "@Earkaro618"
]

BONUS_PER_REFERRAL = 5
WITHDRAW_LIMIT = 50
user_data = {}

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def check_user_joined_all(bot, user_id) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            status = bot.get_chat_member(chat_id=channel, user_id=user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True


def get_join_keyboard():
    keyboard = []
    for i in range(0, len(REQUIRED_CHANNELS), 2):
        row = []
        for ch in REQUIRED_CHANNELS[i:i + 2]:
            row.append(InlineKeyboardButton("🔗 Join", url=f"https://t.me/{ch[1:]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("✅ I’ve Joined All", callback_data="joined")])
    return InlineKeyboardMarkup(keyboard)


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("💳 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🔗 Referral", callback_data="referral"),
         InlineKeyboardButton("📘 How to Earn", callback_data="howto")]
    ])


def back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ])


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    context.bot.send_message(
        chat_id=user_id,
        text="📛 कृपया नीचे दिए गए सभी चैनलों को join करें:",
        reply_markup=get_join_keyboard()
    )


def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    action = query.data

    if action == "joined":
        if check_user_joined_all(context.bot, user_id):
            if user_id not in user_data:
                user_data[user_id] = {"balance": 0, "referrals": []}

                # Referral Bonus Logic
                message = query.message
                if message and message.text and "/start" in message.text:
                    args = message.text.split()
                    if len(args) > 1 and args[1].isdigit():
                        ref_id = int(args[1])
                        if ref_id != user_id and ref_id in user_data:
                            if user_id not in user_data[ref_id]["referrals"]:
                                user_data[ref_id]["referrals"].append(user_id)
                                user_data[ref_id]["balance"] += BONUS_PER_REFERRAL
                                try:
                                    context.bot.send_message(
                                        chat_id=ref_id,
                                        text=f"🎉 आपने 1 referral पूरा किया!\n₹{BONUS_PER_REFERRAL} आपके वॉलेट में जोड़ दिए गए हैं।"
                                    )
                                    # 🎉 Popup for referrer
                                    context.bot.send_message(
                                        chat_id=user_id,
                                        text="🎉 Congratulations! Your referral was successful.\n₹5 has been added to your wallet."
                                    )
                                except:
                                    pass

            # Main menu message
            keyboard = main_menu().inline_keyboard
            context.bot.send_message(
                chat_id=user_id,
                text="✅ धन्यवाद! आपने सभी चैनल join कर लिए हैं। अब आप earning शुरू कर सकते हैं।\n\nAdd Channel : @ARMAN9012",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            query.edit_message_text("❌ आपने सभी चैनल जॉइन नहीं किए हैं। कृपया पहले सभी को जॉइन करें।",
                                    reply_markup=get_join_keyboard())

    elif action in ["balance", "withdraw", "referral", "howto", "back"]:
        if not check_user_joined_all(context.bot, user_id):
            query.edit_message_text("⚠️ पहले सभी चैनल join करें तभी आप earning शुरू कर सकते हैं।",
                                    reply_markup=get_join_keyboard())
            return

        if user_id not in user_data:
            user_data[user_id] = {"balance": 0, "referrals": []}

        if action == "balance":
            bal = user_data[user_id]["balance"]
            query.edit_message_text(f"💰 आपकी बैलेंस: ₹{bal}", reply_markup=back_button())

        elif action == "withdraw":
            if user_data[user_id]["balance"] >= WITHDRAW_LIMIT:
                user_data[user_id]["balance"] = 0
                query.edit_message_text("✅ Withdrawal request भेज दी गई है!", reply_markup=back_button())
            else:
                query.edit_message_text(
                    f"❌ ₹{WITHDRAW_LIMIT} से कम बैलेंस पर withdrawal नहीं किया जा सकता।",
                    reply_markup=back_button())

        elif action == "referral":
            ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
            ref_count = len(user_data[user_id]["referrals"])
            total = ref_count * BONUS_PER_REFERRAL
            query.edit_message_text(
                f"🔗 आपका referral link:\n{ref_link}\n\n👥 Referrals: {ref_count}\n💸 Earnings: ₹{total}",
                reply_markup=back_button()
            )

        elif action == "howto":
            query.edit_message_text(
                "📘 *कमाई कैसे करें:*\n\n1. अपना referral link शेयर करें।\n2. जब कोई नया user सभी चैनल join करके बोट स्टार्ट करता है तो आपको ₹5 मिलते हैं।\n3. ₹50 होने पर withdrawal कर सकते हैं।",
                parse_mode="Markdown", reply_markup=back_button()
            )

        elif action == "back":
            query.edit_message_text("🏠 मुख्य मेनू", reply_markup=main_menu())


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_error_handler(lambda u, c: logger.error(f"Error: {c.error}"))
    logger.info("✅ Bot started...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
