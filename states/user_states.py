from telebot.handler_backends import State, StatesGroup


class UserInputState(StatesGroup):
    command = State()  # команда, которую выбрал пользователь
    input_city = State()  # город, который ввел пользователь
    destinationId = State()  # запись id города
    quantity_hotels = State()  # количество отелей, нужное пользователю
    photo_count = State()  # количество фотографий
    start_date = State()  # ввод даты заезда, выезда
    end_date = State()  # ввод даты заезда, выезда
    priceMin = State()  # минимальная стоимость отеля
    priceMax = State()  # максимальная стоимость отеля
    landmarkIn = State()  # начало диапазона расстояния от центра
    landmarkOut = State()  # конец диапазона расстояния от центра
    travellers_adults = State()  # количество взрослых
    travellers_children = State()  # количество детей
    age_travellers_children = State()  # Возраст дете
    select_number = State()  # выбор истории поиска
