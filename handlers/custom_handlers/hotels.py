from loader import bot
from telebot.types import Message
from request_api import reqwest
from keyboards.inline import inline_regions


@bot.message_handler(commands=["lowprice"])
def start_message(message: Message):
    bot.delete_state(message.chat.id)
    bot.send_message(message.chat.id, "Привет, введите в какой город хотите поехать?")
    bot.register_next_step_handler(message, handle_message)


@bot.message_handler(func=lambda message: False)
def handle_message(message: Message):
    city_name = message.text
    regions = reqwest.city_founding(city_name)
    list_region = [regions[i]["Region"] for i in range(len(regions))]
    inline_regions.start_message(message, list_region)
