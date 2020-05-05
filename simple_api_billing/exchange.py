from decimal import *


getcontext().prec = 24  # TODO: 18 or 2 or ?


EUR_TO_USD = Decimal(1.24)
EUR_TO_RUB = Decimal(70.53)
USD_TO_RUB = Decimal(56.80)


exchange = {
    'EUR_TO_USD': lambda amount: amount * EUR_TO_USD,
    'EUR_TO_RUB': lambda amount: amount * EUR_TO_RUB,
    'USD_TO_RUB': lambda amount: amount * USD_TO_RUB,
    'USD_TO_EUR': lambda amount: amount / EUR_TO_USD,
    'RUB_TO_EUR': lambda amount: amount / EUR_TO_RUB,
    'RUB_TO_USD': lambda amount: amount / USD_TO_RUB,
    'EUR_TO_EUR': lambda amount: amount,
    'USD_TO_USD': lambda amount: amount,
    'RUB_TO_RUB': lambda amount: amount,
}
