import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from openai import OpenAI
import settings

user_states = {}


async def click_button(update, context):

    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    model_choice = query.data
    user_states[chat_id] = {'selected_model': model_choice}

    await query.edit_message_text(text=f"Выбрана нейросеть: {query.data}. Отправьте запрос.")

async def cancel(update, context):
    chat_id = update.message.chat_id
    if chat_id in user_states:
        del user_states[chat_id]
        await update.message.reply_text("Текущий режим сброшен. Используйте /start для выбора нейросети")
    else:
        await update.message.reply_text("Нет активного режима для сброса")



def main():
    
    my_bot = Application.builder().token(settings.API_BOT).build()
    
    my_bot.add_handler(CommandHandler("start", start))

    my_bot.add_handler(CallbackQueryHandler(click_button))
    my_bot.add_handler(CommandHandler('cancel', cancel))
    my_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), common_request))

    my_bot.run_polling()


async def start(update, context):
    button_list = [
        [InlineKeyboardButton("Cypher-Alpha AI", callback_data='Cypher-Alpha AI')],
        [InlineKeyboardButton("Mistral AI", callback_data='Mistral AI')]
    ]
    
    reply_markup = InlineKeyboardMarkup(button_list)
    await update.message.reply_text('Я - бот, созданный на базе Cypher-Alpha AI.' 
                                    '\n Напиши вопрос, чтобы ИИ ответил на него. По умолчанию установлен Cypher-Alpha AI. '
                                    '\n Если хочешь воспользоваться Mistral Mini, напиши /mis перед запросом.' 
                                    '\n\n\n Если возникли проблемы, сообщите @tarazz77.\n Вероятно, надо переподключить API key.')

    await update.message.reply_text('Выберите нейросеть:', reply_markup=reply_markup)
    


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
    return "--CYPHER-ALPHA AI--\n" + completion.choices[0].message.content

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
    return '--MISTRAL AI--\n' + completion.choices[0].message.content


async def common_request(update, context):
    chat_id = update.message.chat_id
    
    if chat_id not in user_states:
        await update.message.reply_text("Сначала выберите модель через /start")
        return
    
    user_text = update.message.text
    model = user_states[chat_id]["selected_model"]
    #await update.message.reply_text('Собираю информацию...')
    if model == "Cypher-Alpha AI":
        response = chat(message=user_text) 
    else:
        response = mistral(request=user_text)  
    
    await update.message.reply_text(response)


if __name__ == '__main__':
    main()