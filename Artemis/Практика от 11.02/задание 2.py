def rational_to_decimal(numerator, denominator, precision=10):

    if not str(abs(numerator)).isdigit() \
            or not str(abs(denominator)).isdigit():
        raise ValueError
    if precision < 0 or not str(precision).isdigit():
        raise ValueError
    if denominator == 0:
        raise ValueError()

    sign = ''
    if numerator * denominator < 0:
        sign = '-'

    numerator = abs(numerator)
    denominator = abs(denominator)

    integer_part = numerator // denominator
    remainder = numerator % denominator

    if remainder == 0:
        return f"{sign}{integer_part}.0"

    decimal_part = ""
    remainders = {}
    position = 0

    while remainder != 0 and position < precision:
        if remainder in remainders:
            period_start = remainders[remainder]
            non_period = decimal_part[:period_start]
            period = decimal_part[period_start:]
            return f"{sign}{integer_part}.{non_period}({period})"

        remainders[remainder] = position
        remainder *= 10
        digit = remainder // denominator
        decimal_part += str(digit)
        remainder %= denominator
        position += 1

    if remainder == 0:
        return f"{sign}{integer_part}.{decimal_part}"
    else:
        return f"{sign}{integer_part}.({decimal_part})..."


print(rational_to_decimal(1, 2))  # Вывод: "0.5"
print(rational_to_decimal(1, 3))  # Вывод: "0.(3)"
print(rational_to_decimal(5, 6))  # Вывод: "0.8(3)"
print(rational_to_decimal(-1, 4))  # Вывод: "-0.25"
print(rational_to_decimal(1, 7, 6))  # Вывод: "0.(142857)..."
