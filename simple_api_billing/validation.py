CURRENCY_TYPE = ('USD', 'EUR', 'RUB')
BOOLEAN_TYPE = ('True', 'False', 'true', 'false')


def parse_boolean(string):
    return string.capitalize() == "True"


def is_digit(query):
    return query.isdigit()


def is_decimal(query):
    return query.replace('.', '', 1).isdigit()


def is_boolean(query):
    return query in BOOLEAN_TYPE


def is_currency_type(query):
    return query in CURRENCY_TYPE
