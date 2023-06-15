from loader import bot
from utils.set_bot_commands import set_default_commands
import handlers  # noqa
from telebot.custom_filters import StateFilter, IsDigitFilter
from keyboards.inline.filters import CityCallbackFilter


def run_bot():
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    bot.add_custom_filter(IsDigitFilter())
    bot.add_custom_filter(CityCallbackFilter())
    bot.infinity_polling()


if __name__ == "__main__":
    run_bot()
