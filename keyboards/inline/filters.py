from telebot import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter
from telebot import types


class CityCallbackFilter(AdvancedCustomFilter):
    """Фильтр для клавиатуры с выбором городов"""

    key = 'city_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
