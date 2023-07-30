from loader import bot
from telebot.types import CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from loguru import logger
from states.user_states import UserInputState
from utils.show_data_and_find_hotels import print_data


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def date_reply(call: CallbackQuery) -> None:
    with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        if not data.get("start_date"):
            result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(call.data)
        elif not data.get('end_date'):
            new_start_date = data.get('start_date') + timedelta(1)
            result, key, step = DetailedTelegramCalendar(min_date=new_start_date).process(call.data)
    if not result and key:
        bot.edit_message_text("Введите дату: ", call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
            if not data.get('start_date'):
                logger.info('Ввод даты заезда: ' + call.message.text + f' User_id: {call.message.chat.id}')
                data['start_date'] = result
                calendar, step = DetailedTelegramCalendar(min_date=result + timedelta(1)).build()
                bot.edit_message_text("Введите дату выезда:",
                                      call.message.chat.id, call.message.message_id, reply_markup=calendar)
            elif not data.get('end_date'):
                logger.info('Ввод даты выезда: ' + call.message.text + f' User_id: {call.message.chat.id}')
                data['end_date'] = result
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    print(data)
    if data['sort'] == 'DISTANCE':
        bot.set_state(call.message.chat.id, UserInputState.landmarkIn)
        bot.send_message(call.message.chat.id, 'Введите начало диапазона расстояния от центра(от 0 миль): ')
    else:
        print_data(call.message, data)

