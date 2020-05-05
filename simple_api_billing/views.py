from aiohttp import web
import db
import json
from decimal import *

getcontext().prec = 24   # TODO: 18 or 2 or ?

EUR_TO_USD = Decimal(1.24)
EUR_TO_RUB = Decimal(70.53)
USD_TO_RUB = Decimal(56.80)

CURRENCY_TYPE = ('USD', 'EUR', 'RUB')
BOOLEAN_TYPE = ('True', 'False', 'true', 'false')


def parse_boolean(string):
    return string.capitalize() == "True"


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


async def account_get(request):
    """
    ---
    description: This method on endpoint allow to get account info.
    tags:
    - Account
    produces:
    - application/json
    responses:
        "200":
            description: Successful operation. Return account info (balance, currency).
        "400":
            description: Bad request. Need args - integer(id).
        "404":
            description: Not found.
        "405":
            description: Invalid HTTP Method.
        "500":
            description: Server error.
    """
    try:
        if not request.query['id'].isdigit():
            response_obj = {
                'status': 'failed',
                'reason': 'Bad request. Need args: integer(id).'
            }
            return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
        async with request.app['db'].acquire() as conn:
            id_account = request.query['id']
            cursor = await conn.execute(db.account.select().where(db.account.c.id == id_account))
            record = await cursor.fetchall()
            account_info = [dict(info) for info in record]
            if not account_info:
                return web.Response(
                    text=json.dumps({'status': 'failed', 'reason': 'Not found.'}),
                    status=404,
                    content_type='application/json')
            return web.Response(
                text=json.dumps(account_info, ensure_ascii=False, default=str),
                status=200,
                content_type='application/json')
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500, content_type='application/json')


async def account_post(request):
    """
    ---
    description: This method on endpoint allow to create account.
    tags:
    - Account
    produces:
    - application/json
    responses:
        "201":
            description: Successful operation. Account created.
        "400":
            description: Bad request. Need args - integer(currency), boolean(overdraft).
        "405":
            description: Invalid HTTP Method.
        "500":
            description: Server error.
    """
    try:
        if request.query['currency'] not in CURRENCY_TYPE or request.query['overdraft'] not in BOOLEAN_TYPE:
            response_obj = {
                'status': 'failed',
                'reason': 'Bad request. Need integer(currency) and boolean(overdraft).'
            }
            return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
        async with request.app['db'].acquire() as conn:
            currency = request.query['currency']
            overdraft = parse_boolean(request.query['overdraft'])
            cursor = await conn.execute(
                db.account.insert().values(
                    currency=currency,
                    overdraft=overdraft)
            )
            record = await cursor.fetchall()
            account_id = [dict(info) for info in record]
            return web.Response(
                text=json.dumps(account_id),
                status=201,
                content_type='application/json')
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500, content_type='application/json')


async def invoice_post(request):
    """
    ---
    description: This method on endpoint allow to create invoice.
    tags:
    - Invoice
    produces:
    - application/json
    responses:
        "201":
            description: Successful operation. Invoice created.
        "400":
            description: Bad request. Need args - integer(account_id_from), integer(account_id_to), integer(amount).
        "404":
            description: Not found.
        "405":
            description: Invalid HTTP Method.
        "500":
            description: Server error.
    """
    try:
        if not request.query['account_id_from'].isdigit() or \
                not request.query['account_id_to'].isdigit() or \
                not request.query['amount'].replace('.', '', 1).isdigit():
            response_obj = {
                'status': 'failed',
                'reason': 'Bad request. Need args: integer(account_id_from), integer(account_id_to), integer(amount).'
            }
            return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
        async with request.app['db'].acquire() as conn:
            account_id_from = request.query['account_id_from']
            account_id_to = request.query['account_id_to']
            amount = request.query['amount']
            async with conn.begin() as tr:
                cursor = await conn.execute(
                    f"SELECT id, currency, overdraft, balance"
                    f" FROM account WHERE id in ({account_id_from}, {account_id_to}) FOR UPDATE;"
                )
                record = await cursor.fetchall()
                accounts_info = [dict(info) for info in record]

                if len(accounts_info) < 2:
                    return web.Response(
                        text=json.dumps({
                            'status': 'rejection',
                            'reason': 'Not found this accounts.'}),
                        status=404,
                        content_type='application/json')

                if int(accounts_info[0]["id"]) == int(account_id_from):
                    account_balance_from = Decimal(accounts_info[0]['balance']) - Decimal(amount)
                    overdraft = accounts_info[0]['overdraft']
                    account_balance_to = Decimal(accounts_info[1]["balance"]) + exchange.get(
                        f'{accounts_info[0]["currency"]}_TO_{accounts_info[1]["currency"]}')(Decimal(amount))
                else:
                    account_balance_from = Decimal(accounts_info[1]['balance']) - Decimal(amount)
                    overdraft = accounts_info[1]['overdraft']
                    account_balance_to = Decimal(accounts_info[0]["balance"]) + exchange.get(
                        f'{accounts_info[1]["currency"]}_TO_{accounts_info[0]["currency"]}')(Decimal(amount))

                if not overdraft and account_balance_from < Decimal(amount):
                        return web.Response(
                            text=json.dumps({
                                'status': 'rejection',
                                'reason': 'Not enough balance.'}),
                            status=403,
                            content_type='application/json')
                await conn.execute(
                    f"UPDATE account "
                    f"SET balance = CASE id "
                    f"WHEN {account_id_from} THEN {account_balance_from} "
                    f"WHEN {account_id_to} THEN {account_balance_to} END "
                    f"WHERE id in ({account_id_from}, {account_id_to});")
                await conn.execute(
                    db.invoice.insert().values(
                        account_id_from=account_id_from,
                        account_id_to=account_id_to,
                        amount=amount,
                    )
                )
            return web.Response(
                text=json.dumps({'status': 'success'}),
                status=201,
                content_type='application/json')
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500, content_type='application/json')
