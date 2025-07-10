import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
import settings

def main():
    
    my_bot = Application.builder().token(settings.API_BOT).build()
    
    chat_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), ask)
    mistral_handler = MessageHandler(filters.TEXT, ask_mistral)

    my_bot.add_handler(CommandHandler("start", start))
    my_bot.add_handler(CommandHandler('mis', ask_mistral))
    my_bot.add_handler(chat_handler)
    my_bot.add_handler(mistral_handler)


    my_bot.run_polling()


async def start(update, context):
    await update.message.reply_text('Я - бот, созданный на базе Cypher-Alpha AI.' 
                                    '\n Напиши вопрос, чтобы ИИ ответил на него. По умолчанию установлен Cypher-Alpha AI. '
                                    '\n Если хочешь воспользоваться Mistral Mini, напиши /mis перед запросом.' 
                                    '\n\n\n Если возникли проблемы, сообщите @tarazz77.\n Вероятно, надо переподключить API key.')

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

def mistral(image = '', request = ''):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.MISTRAL_API,
    )

    completion = client.chat.completions.create(
    model="mistralai/mistral-small-3.2-24b-instruct:free",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": request
            }
        ]
        }
    ]
    )
    return completion.choices[0].message.content

async def ask(update, context):
    await update.message.reply_text('Пару секунд...')
    text = update.message.text
    await update.message.reply_text(chat(text))


async def ask_mistral(update, context):
    await update.message.reply_text('Собираю информацию...')
    text = update.message.text
    await update.message.reply_text(mistral(request=text))



if __name__ == '__main__':
    main()