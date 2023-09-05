import utils.show_data_and_find_hotels
from loader import bot
from telebot.types import CallbackQuery, ReplyKeyboardRemove
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
from loguru import logger
from states.user_states import UserInputState


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def send_start_calendar(callback: CallbackQuery) -> None:
    logger.info(f'Пользователь выбирает дату заезда. User_id: {callback.message.chat.id}')
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(), locale='ru').process(
        callback.data)
    if not result and key:
        bot.edit_message_text(f'Выберите {LSTEP[step]} заезда',
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(callback.message.chat.id) as data:
            data['start_date'] = result
        bot.edit_message_text("_",
                              callback.message.chat.id,
                              callback.message.message_id, reply_markup=None)
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=date.today(), locale='ru').build()
        bot.send_message(callback.message.chat.id, f"Выберите {LSTEP[step]} выезда",
                         reply_markup=calendar)
        bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def send_end_calendar(callback: CallbackQuery) -> None:
    logger.info(f'Пользователь выбирает дату выезда. User_id: {callback.message.chat.id}')
    with bot.retrieve_data(callback.message.chat.id) as data:
        new_start_date = data['start_date'] + timedelta(1)
        result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=new_start_date, locale='ru').process(
            callback.data)
        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]} выезда",
                                  callback.message.chat.id,
                                  callback.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.edit_message_text("_",
                                  callback.message.chat.id,
                                  callback.message.message_id, reply_markup=None)
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            data['end_date'] = result
            data['landmark_in'] = 0
            data['landmark_out'] = 0
            data['travellers_adults'] = 1
            data['children_ages'] = []
            if data['sort'] == 'DISTANCE':
                bot.set_state(callback.message.chat.id, UserInputState.landmarkIn)
                bot.send_message(callback.message.chat.id, 'Введите начало диапазона расстояния от центра '
                                                           '(от 0 миль).')
            else:
                utils.show_data_and_find_hotels.print_data(callback.message, data)

