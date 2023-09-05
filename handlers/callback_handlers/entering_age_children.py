from loader import bot
from telebot.types import CallbackQuery
from states import user_states


@bot.callback_query_handler(func=lambda call: True)
def get_age_children(callback: CallbackQuery) -> None:
    """
    Функция для ввода возраста детей и подсчета их количества.
    :param callback: Ответ с Клавиатуры.
    :return: None
    """
    if callback.message.text.isdigit():
        if 0 <= int(callback.message.text) <= 6:
            with bot.retrieve_data(callback.message.chat.id) as data:
                data['children_count '] = callback.data
                bot.send_message(callback.message.chat.id, f"Введите возраст до 17 лет, каждого ребенка через пробел:\n"
                                                           f"Пример(3 5 6 3).")
                bot.set_state(callback.message.chat.id, user_states.UserInputState.age_travellers_children)
        else:
            bot.send_message(callback.message.chat.id, "Ошибка! Вы вышли из диапазона от 0-6! Повторите попытку ввода!")
    else:
        bot.send_message(callback.message.chat.id, "Ошибка! Вы ввели не число! Повторите попытку ввода!")
