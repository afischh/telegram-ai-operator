import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from llm import complete
from storage import append_log

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is required")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    append_log({"event": "start", "chat_id": update.effective_chat.id})
    await update.message.reply_text("AI Operator ready")


async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /ask <question>")
        return

    answer = await complete(text, system="You are a helpful AI operator assistant.")
    append_log({
        "event": "ask",
        "chat_id": update.effective_chat.id,
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
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("summarize", summarize))

if __name__ == "__main__":
    app.run_polling()
