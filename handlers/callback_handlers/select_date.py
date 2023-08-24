from loader import bot
from telebot.types import CallbackQuery, ReplyKeyboardRemove
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
from loguru import logger


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def send_start_calendar(callback: CallbackQuery) -> None:
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
        bot.edit_message_text(f"Записал",
                              callback.message.chat.id,
                              callback.message.message_id, reply_markup=ReplyKeyboardRemove())
        calendar, step = DetailedTelegramCalendar(calendar_id=2, min_date=date.today(), locale='ru').build()
        bot.send_message(callback.message.chat.id, f"Выберите {LSTEP[step]} выезда",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def send_end_calendar(callback: CallbackQuery) -> None:
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
            data['end_date'] = result
            bot.edit_message_text(f"Дата заезда {data['start_date']}\n"
                                  f"Дата выезда {result}",
                                  callback.message.chat.id,
                                  callback.message.message_id)

# TODO Дописать логеры и завершить функцию
