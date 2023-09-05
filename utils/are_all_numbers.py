def are_all_numbers(lst):
    for item in lst:
        try:
            numb = int(item)
            if 0 <= numb <= 16:
                return True
            else:
                return False
        except ValueError:
            return False  # Если не удалось преобразовать в число, возвращаем False
