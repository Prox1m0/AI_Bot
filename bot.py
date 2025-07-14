import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from openai import OpenAI
import settings

#трекер для выбранной ИИ (messagehandler)
user_states = {}

#обработчик кнопок
async def click_button(update, context):

    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    model_choice = query.data
    user_states[chat_id] = {'selected_model': model_choice}

    await query.edit_message_text(text=f"Выбрана нейросеть: {query.data}. Отправьте запрос.")

#функция для отмены выбранной ИИ
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

#команда /start
async def start(update, context):
    button_list = [
        [InlineKeyboardButton("Cypher-Alpha AI", callback_data='Cypher-Alpha AI')],
        [InlineKeyboardButton("Mistral AI", callback_data='Mistral AI')]
    ]
    
    reply_markup = InlineKeyboardMarkup(button_list)
    await update.message.reply_text('Я ваш удобный виртуальный помощник' 
                                    '\n Перед запросом необходимо выбрать модель, нажав на одну из кнопок.'
                                    '\n После выбора чат активируется, можете смело обращаться.'
                                    '\n\n Чтобы поменять выбранную модель, используйте /cancel для деактивации, затем повторно выберите сеть.' 
                                    '\n\n\n Если возникли проблемы, сообщите @tarazz77')

    await update.message.reply_text('Выберите нейросеть:', reply_markup=reply_markup)
    

#логика ответа cypher-alpha
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
    return "   --CYPHER-ALPHA AI--\n\n" + completion.choices[0].message.content

#логика ответа mistral mini
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
    return '   --MISTRAL AI--\n\n' + completion.choices[0].message.content

#функция общего обработчика запросов с определением выбранной сети
async def common_request(update, context):
    chat_id = update.message.chat_id
    
    if chat_id not in user_states:
        await update.message.reply_text("Сначала выберите модель через /start")
        return
    
    user_text = update.message.text
    model = user_states[chat_id]["selected_model"]
    await update.message.reply_text('Собираю информацию...')
    if model == "Cypher-Alpha AI":
        response = chat(message=user_text) 
    else:
        response = mistral(request=user_text)  
    
    await update.message.reply_text(response)


if __name__ == '__main__':
    main()