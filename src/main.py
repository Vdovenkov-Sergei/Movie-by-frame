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
from src.utils import (
    CLASSES,
    DONT_KNOW_RESPONSE,
    GREETING,
    RESPONSE,
    RESPONSE_LIST,
    TEMPERATURE,
    THRESHOLD_TOP1,
    THRESHOLD_TOP3,
    transform,
)

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
        if not update.message.photo:
            await update.message.reply_text("Пожалуйста, отправь мне изображение!🎬")
            return

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

        top_probs, top_indices = torch.topk(probabilities, k=3, dim=1)
        top_probs = top_probs.squeeze(0).tolist()
        top_indices = top_indices.squeeze(0).tolist()

        max_prob = top_probs[0]
        predicted_class = top_indices[0]
        if max_prob >= THRESHOLD_TOP1:
            await update.message.reply_text(RESPONSE.format(name=CLASSES[predicted_class]))
        elif max_prob >= THRESHOLD_TOP3:
            await update.message.reply_text(
                RESPONSE_LIST.format(
                    top1=CLASSES[top_indices[0]], top2=CLASSES[top_indices[1]], top3=CLASSES[top_indices[2]]
                )
            )
        else:
            await update.message.reply_text(DONT_KNOW_RESPONSE)

    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке изображения.😕")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Извините, я не понял эту команду.😕")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.warning(f"Ошибка у пользователя {user.full_name} (ID: {user.id})\nОшибка: {context.error}")


def main() -> None:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.add_error_handler(error)
    app.run_polling()
