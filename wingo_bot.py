import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CONFIGURATION ---
# Your actual token from @BotFather
TOKEN = "8592194163:AAE_0Sd5wxYgQpySlpItuvhpzPo3cpY4AmA"

# --- PREDICTION LOGIC ---
def analyze_pattern(history):
    """
    Analyzes the history of Big (B) and Small (S) to predict the next.
    history: list of strings ['B', 'S', 'B', ...]
    """
    if len(history) < 2:
        return "Need more data (at least 2 results)", "N/A"

    last = history[-1]
    second_last = history[-2]
    
    # 1. Dragon Pattern (B-B-B-B or S-S-S-S)
    if len(history) >= 3 and all(x == last for x in history[-3:]):
        prediction = last # Follow the dragon
        reason = "Dragon Pattern detected (Consecutive results)"
    
    # 2. Mirror Pattern (B-S-B-S or S-B-S-B)
    elif last != second_last:
        prediction = "B" if last == "S" else "S"
        reason = "Mirror Pattern detected (Alternating)"
    
    # 3. Double Pattern (B-B-S-S)
    elif len(history) >= 4 and history[-1] == history[-2] and history[-3] == history[-4] and history[-2] != history[-3]:
        prediction = "B" if last == "S" else "S"
        reason = "Double Pattern detected (Pairs)"
        
    # Default: Follow the last result
    else:
        prediction = last
        reason = "Trend following (Default)"

    return prediction, reason

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['history'] = []
    reply_keyboard = [['Big (B)', 'Small (S)'], ['Reset Data', 'Show History']]
    
    welcome_text = (
        "🎰 **Win Go 1 Min Predictor Bot** 🎰\n\n"
        "Please input the latest results one by one to get a prediction.\n"
        "Use the buttons below to enter 'Big' or 'Small'."
    )
    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True),
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if 'history' not in context.user_data:
        context.user_data['history'] = []
    
    history = context.user_data['history']

    if text == 'Reset Data':
        context.user_data['history'] = []
        await update.message.reply_text("History cleared. Start fresh!")
        return

    if text == 'Show History':
        hist_str = " -> ".join(history) if history else "Empty"
        await update.message.reply_text(f"Current History: {hist_str}")
        return

    # Process B or S
    val = ""
    if "Big" in text or text.upper() == "B":
        val = "B"
    elif "Small" in text or text.upper() == "S":
        val = "S"
    
    if val:
        history.append(val)
        # Keep only last 10 for analysis
        if len(history) > 10:
            history.pop(0)
            
        prediction, reason = analyze_pattern(history)
        
        response = (
            f"✅ Added: **{val}**\n"
            f"📊 History: {' -> '.join(history)}\n\n"
            f"🔮 **Next Prediction: {prediction}**\n"
            f"📝 Reason: {reason}\n\n"
            f"⚠️ *Note: This is just a pattern analysis. Play responsibly.*"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("Please use the buttons or type 'B' or 'S'.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(msg_handler)
    
    print("Bot is running...")
    application.run_polling()
