from loader import bot
from utils.set_bot_commands import set_default_commands
import handlers  # noqa
from telebot.custom_filters import StateFilter, IsDigitFilter


def run_bot():
    set_default_commands(bot)
    bot.infinity_polling()
    bot.add_custom_filter(StateFilter(bot))
    bot.add_custom_filter(IsDigitFilter())


if __name__ == "__main__":
    run_bot()
