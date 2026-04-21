import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from llm import complete
from storage import append_log, get_mode, set_mode

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
}


def current_system(chat_id: int) -> str:
    mode = get_mode(chat_id)
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    append_log({"event": "start", "chat_id": update.effective_chat.id})
    await update.message.reply_text(
        "AI Operator ready\n\nCommands:\n"
        "/ask <question>\n"
        "/summarize <text>\n"
        "/mode <default|operator|human_ai>\n"
        "/human <message>"
    )


async def mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        mode = get_mode(chat_id)
        await update.message.reply_text(f"Current mode: {mode}")
        return

    mode = context.args[0].strip().lower()
    if mode not in SYSTEM_PROMPTS:
        await update.message.reply_text("Available modes: default, operator, human_ai")
        return

    set_mode(chat_id, mode)
    append_log({"event": "mode", "chat_id": chat_id, "mode": mode})
    await update.message.reply_text(f"Mode set to: {mode}")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /ask <question>")
        return

    answer = await complete(text, system=current_system(chat_id))
    append_log({
        "event": "ask",
        "chat_id": chat_id,
        "mode": get_mode(chat_id),
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000])


async def human(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /human <message>")
        return

    answer = await complete(text, system=SYSTEM_PROMPTS["human_ai"])
    append_log({
        "event": "human",
        "chat_id": chat_id,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000])


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /summarize <text>")
        return

    prompt = f"Summarize the following text in 3-5 bullet points:\n\n{text}"
    answer = await complete(prompt, system="You summarize text clearly and briefly.")
    append_log({
        "event": "summarize",
        "chat_id": update.effective_chat.id,
        "input": text,
        "output": answer,
    })
    await update.message.reply_text(answer[:4000])


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mode", mode_cmd))
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("human", human))
app.add_handler(CommandHandler("summarize", summarize))

if __name__ == "__main__":
    app.run_polling()
