def custom_string_to_int(s):
    if len(s) == 0:
        raise ValueError("Вы ввели пустую строку!")

    is_negative = False
    start_index = 0

    if s[0] == '-':
        is_negative = True
        start_index = 1
    elif s[0] == '+':
        start_index = 1

    if start_index >= len(s):
        raise ValueError("Строка содержит только знак без цифр")

    result = 0
    digit_count = 0

    for i in range(start_index, len(s)):
        char = s[i]

        if ord(char) < ord('0') or ord(char) > ord('9'):
            raise ValueError(f"Некорректный символ '{char}' в строке")

        digit = ord(char) - ord('0')

        result = result * 10 + digit
        digit_count += 1

    if digit_count == 0:
        raise ValueError("Строка не содержит цифр")

    return -result if is_negative else result


print(custom_string_to_int("123"))  # Вывод: 123
print(custom_string_to_int("-456"))  # Вывод: -456
print(custom_string_to_int("0"))  # Вывод: 0
print(custom_string_to_int("-0"))  # Вывод: 0
custom_string_to_int("12a3")  # Должно вызвать ValueError
custom_string_to_int("")  # Должно вызвать ValueError
