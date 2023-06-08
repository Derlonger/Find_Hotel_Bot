from loader import bot, logger
from utils.set_bot_commands import set_default_commands


@logger.catch
def run_bot():
    set_default_commands(bot)
    bot.infinity_polling()


if __name__ == "__main__":
    run_bot()
