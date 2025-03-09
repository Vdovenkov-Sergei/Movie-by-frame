import io
import logging
import os
import warnings

import torch
from dotenv import load_dotenv
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.model import model
from src.utils import CLASSES, DONT_KNOW_RESPONSE, GREETING, RESPONSE, TEMPERATURE, THRESHOLD, transform

warnings.filterwarnings("ignore")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Токен для телеграм-бота не найден!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(GREETING)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        file = await update.message.photo[-1].get_file()
        image_stream = io.BytesIO()
        await file.download_to_memory(out=image_stream)
        image_stream.seek(0)

        image = Image.open(image_stream).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(image_tensor)
            mean = torch.mean(output, dim=1, keepdim=True)
            std = torch.std(output, dim=1, keepdim=True)
            normalized_output = (output - mean) / std
            scaled_output = normalized_output / TEMPERATURE
            probabilities = torch.sigmoid(scaled_output)

        max_prob, predicted_class = torch.max(probabilities, dim=1)
        max_prob = max_prob.item()
        predicted_class = predicted_class.item()

        if max_prob < THRESHOLD:
            await update.message.reply_text(DONT_KNOW_RESPONSE)
        else:
            await update.message.reply_text(RESPONSE.format(movie_name=CLASSES[predicted_class], confidence=max_prob))
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке изображения.")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f"Update {update} caused error {context.error}")


def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_error_handler(error)
    app.run_polling()
