def lucky_ticket(ticket):
    if str(ticket).isdigit():
        ticket = str(ticket).zfill(6)
        if sum(map(int, ticket[:3])) == sum(map(int, ticket[3:])):
            return True
        else:
            return False
    else:
        return False

    return "Ошибка в проге"


def almost_lucky(ticket):
    prev_ticket = ticket - 1
    next_ticket = ticket + 1
    return lucky_ticket(prev_ticket) or lucky_ticket(next_ticket)


print(almost_lucky(123320))
