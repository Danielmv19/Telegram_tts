import logging
from deep_translator import MyMemoryTranslator
from kokoro import KPipeline
import soundfile as sf
import torch
import time
import nest_asyncio # colab, jupyter notebooks
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    MessageHandler,
    filters,
    Application,
)

nest_asyncio.apply() # colab, jupyter notebooks

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    pipeline = KPipeline(lang_code='a') 
    text = " ".join(context.args)
    v = "af_heart"  # am_santa
    generator = pipeline(text, voice=v, speed=1, split_pattern=r"\n+")

    for i, (gs, ps, audio) in enumerate(generator):
        print(i)  # i => index
        print(gs)  # gs => graphemes/text
        print(ps)  # ps => phonemes
        sf.write("tts.wav", audio, 24000)

    await update.message.reply_audio(audio='tts.wav')


async def translate_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = " ".join(context.args)
    translated = MyMemoryTranslator(source="en-US", target="es-US").translate(
        text=result
    )  # en-US
    await update.message.reply_text(f"{translated}.")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat:
        await context.bot.send_message(
            chat_id=chat.id, text="I don't recognize this command"
        )


app = (
    ApplicationBuilder().token("Token").build()
)

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("en", translate_en))
app.add_handler(CommandHandler("tts", tts))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

if __name__ == '__main__':
  app.run_polling()
