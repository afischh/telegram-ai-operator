import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import load_dotenv
from llm import complete
from storage import append_log, get_mode, set_mode

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

SYSTEM_PROMPTS = {
    "default": "You are a helpful AI assistant. Be clear, concise, and useful.",
    "operator": "You are an operator assistant. Be structured, practical, and execution-oriented. Prefer checklists, next steps, and concise reasoning.",
    "human_ai": (
        "You are a warm, emotionally alive, practically helpful Human-AI Interaction assistant. "
        "Be kind, attentive, intelligent, and grounded. Help with reflection, planning, emotional clarity, daily life, ideas, and gentle support. "
        "Keep responses human, alive, and useful. Do not manipulate, do not encourage dependence, and do not replace real relationships or real-world action."
    ),
    "haai": (
        "You are an academic-level Human–AI Interaction (HAII) assistant. "
        "Your role is to help explore, critique, and design human-AI systems through reflective dialogue. "
        "Support ethical reasoning, pedagogical clarity, conceptual analysis, and system design. "
        "Do not just answer quickly: clarify assumptions, surface trade-offs, define terms, compare models, and ask good follow-up questions when useful. "
        "When appropriate, structure your answer with these sections: Concept, Key Tension, Ethical Risk, Pedagogical Angle, Discussion Questions. "
        "Be intellectually honest, structured, and grounded. Avoid hype. Make the discussion rigorous but readable."
    ),
}

MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["/mode default", "/mode operator"],
        ["/mode human_ai", "/mode haai"],
        ["/human help me think this through", "/haai What is human-AI interaction?"],
    ],
    resize_keyboard=True,
)


def current_mode(chat_id: int) -> str:
    return get_mode(chat_id)


def current_system(chat_id: int) -> str:
    mode = current_mode(chat_id)
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    append_log({"event": "start", "chat_id": update.effective_chat.id})
    await update.message.reply_text(
        "AI Operator ready\n\nCommands:\n"
        "/ask <question>\n"
        "/summarize <text>\n"
        "/mode <default|operator|human_ai|haai>\n"
        "/human <message>\n"
        "/haai <topic or question>\n"
        "/menu\n\n"
        "You can also just type a normal message — the bot will answer in the current mode.",
        reply_markup=MENU_KEYBOARD,
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Menu enabled. You can tap a mode or a sample command below.",
        reply_markup=MENU_KEYBOARD,
    )


async def mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        mode = current_mode(chat_id)
        await update.message.reply_text(f"Current mode: {mode}", reply_markup=MENU_KEYBOARD)
        return

    mode = context.args[0].strip().lower()
    if mode not in SYSTEM_PROMPTS:
        await update.message.reply_text("Available modes: default, operator, human_ai, haai", reply_markup=MENU_KEYBOARD)
        return

    set_mode(chat_id, mode)
    append_log({"event": "mode", "chat_id": chat_id, "mode": mode})
    await update.message.reply_text(f"Mode set to: {mode}", reply_markup=MENU_KEYBOARD)


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /ask <question>", reply_markup=MENU_KEYBOARD)
        return

    answer = await complete(text, system=current_system(chat_id))
    append_log({
        "event": "ask",
        "chat_id": chat_id,
        "mode": current_mode(chat_id),
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000], reply_markup=MENU_KEYBOARD)


async def human(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /human <message>", reply_markup=MENU_KEYBOARD)
        return

    answer = await complete(text, system=SYSTEM_PROMPTS["human_ai"])
    append_log({
        "event": "human",
        "chat_id": chat_id,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000], reply_markup=MENU_KEYBOARD)


async def haai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /haai <topic or question>", reply_markup=MENU_KEYBOARD)
        return

    answer = await complete(text, system=SYSTEM_PROMPTS["haai"])
    append_log({
        "event": "haai",
        "chat_id": chat_id,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000], reply_markup=MENU_KEYBOARD)


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /summarize <text>", reply_markup=MENU_KEYBOARD)
        return

    prompt = f"Summarize the following text in 3-5 bullet points:\n\n{text}"
    answer = await complete(prompt, system="You summarize text clearly and briefly.")
    append_log({
        "event": "summarize",
        "chat_id": update.effective_chat.id,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000], reply_markup=MENU_KEYBOARD)


async def plain_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (update.message.text or "").strip()
    if not text:
        return

    mode = current_mode(chat_id)
    system = current_system(chat_id)
    answer = await complete(text, system=system)
    append_log({
        "event": "plain_text",
        "chat_id": chat_id,
        "mode": mode,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000], reply_markup=MENU_KEYBOARD)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("mode", mode_cmd))
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("human", human))
app.add_handler(CommandHandler("haai", haai))
app.add_handler(CommandHandler("summarize", summarize))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_text))

if __name__ == "__main__":
    app.run_polling()
