from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_yes_no() -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками 'Да' и 'Нет'.
    Returns: Клавиатура InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="Да", callback_data="yes"),
        InlineKeyboardButton(text="Нет", callback_data="no")
    )
    return keyboard
