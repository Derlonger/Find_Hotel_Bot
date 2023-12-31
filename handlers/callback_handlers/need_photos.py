from loader import bot
from loguru import logger
from telebot.types import CallbackQuery
from states.user_states import UserInputState
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date


@bot.callback_query_handler(func=lambda call: call.data.isalpha())
def need_photo_callback(call: CallbackQuery) -> None:
    """
    Функция для обработки ответа инлайн-клавиатуры "Да" или "Нет".
    :param call: Нажатая кнопка 'yes' or 'no'
    :return: None
    """
    if call.data == 'yes':
        logger.info(f'Нажата кнопка "ДА". User_id: {call.message.chat.id}')
        with bot.retrieve_data(call.message.chat.id) as data:
            data['photo_need'] = call.data
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.set_state(call.message.chat.id, UserInputState.photo_count)
        bot.send_message(call.message.chat.id, 'Сколько вывести фотографий? От 1 до 10!')
    elif call.data == 'no':
        logger.info(f'Нажата кнопка "НЕТ". User_id: {call.message.chat.id} ')
        with bot.retrieve_data(call.message.chat.id) as data:
            data['photo_need'] = call.data
            data['photo_count'] = '0'
        bot.delete_message(call.message.chat.id, call.message.message_id)
        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
        bot.send_message(call.message.chat.id, "Введите дату заезда", reply_markup=calendar)

