def lucky_ticket(ticket):
    if not isinstance(ticket, (int, str)):
        raise ValueError()

    try:
        ticket_num = int(str(ticket).strip())
        if ticket_num < 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError()

    ticket_str = str(ticket_num).zfill(6)

    if len(ticket_str) > 6:
        raise ValueError()

    return sum(map(int, ticket_str[:3])) == sum(map(int, ticket_str[3:]))


def is_almost_lucky(ticket):
    if not isinstance(ticket, (int, str)):
        raise ValueError()

    try:
        ticket_num = int(str(ticket).strip())
        if ticket_num < 0:
            raise ValueError()
    except (ValueError, TypeError):
        raise ValueError()

    if ticket_num == 0:
        return lucky_ticket(1)

    if lucky_ticket(ticket_num - 1):
        return True

    if lucky_ticket(ticket_num + 1):
        return True

    return False
