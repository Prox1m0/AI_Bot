import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import settings

def main():
    
    my_bot = Application.builder().token(settings.API_BOT).build()
    
    my_bot.add_handler(CommandHandler("start", start))
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), ask)
    my_bot.add_handler(chat_handler)

    my_bot.run_polling()


async def start(update, context):
    await update.message.reply_text('Я - бот, созданный на базе Cypher-Alpha AI. \n Напиши вопрос, чтобы ИИ ответил на него')

def chat(message):
    client = OpenAI(
        base_url=settings.BASE_AI_URL,
        api_key=settings.API_AI,
    )

    completion = client.chat.completions.create(
    model=settings.AI_MODEL,
    messages=[
        {
        "role": "user",
        "content": message,
        }
    ]
    )
    return completion.choices[0].message.content

async def ask(update, context):
    await update.message.reply_text('Пару секунд...')
    text = update.message.text
    await update.message.reply_text(chat(text))

if __name__ == '__main__':
    main()