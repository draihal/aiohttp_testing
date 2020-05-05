from aiohttp import web
import db
import json
from decimal import *
from validation import parse_boolean, is_digit, is_decimal, is_boolean, is_currency_type
from exchange import exchange

getcontext().prec = 24   # TODO: 18 or 2 or ?


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
        async with request.app['db'].acquire() as conn:
            id_account = request.query['id']
            if not is_digit(id_account):
                response_obj = {'status': 'failed', 'reason': 'Bad request. Check args.'}
                return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
            cursor = await conn.execute(db.account.select().where(db.account.c.id == id_account))
            record = await cursor.fetchall()
            account_info = [dict(info) for info in record]
            if not account_info:
                return web.Response(text=json.dumps({'status': 'failed', 'reason': 'Not found.'}),
                                    status=404, content_type='application/json')
            return web.Response(text=json.dumps(account_info, ensure_ascii=False, default=str),
                                status=200, content_type='application/json')
    except Exception as e:
        return web.Response(text=json.dumps({'status': 'failed', 'reason': str(e)}),
                            status=500, content_type='application/json')


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
        async with request.app['db'].acquire() as conn:
            currency = request.query['currency']
            overdraft = parse_boolean(request.query['overdraft'])
            if not is_currency_type(currency) or not is_boolean(overdraft):
                response_obj = {
                    'status': 'failed', 'reason': 'Bad request. Need integer(currency) and boolean(overdraft).'}
                return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
            cursor = await conn.execute(db.account.insert().values(currency=currency, overdraft=overdraft))
            record = await cursor.fetchall()
            account_id = [dict(info) for info in record]
            return web.Response(text=json.dumps(account_id), status=201, content_type='application/json')
    except Exception as e:
        return web.Response(text=json.dumps({'status': 'failed', 'reason': str(e)}),
                            status=500, content_type='application/json')


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
        async with request.app['db'].acquire() as conn:
            account_id_from = request.query['account_id_from']
            account_id_to = request.query['account_id_to']
            amount = request.query['amount']
            if not is_digit(account_id_from) or not is_digit(account_id_to) or not is_decimal(amount):
                response_obj = {
                    'status': 'failed',
                    'reason': 'Bad request. Need args int(account_id_from), int(account_id_to), int(amount).'}
                return web.Response(text=json.dumps(response_obj), status=400, content_type='application/json')
            async with conn.begin() as tr:
                cursor = await conn.execute(
                    f"SELECT id, currency, overdraft, balance"
                    f" FROM account WHERE id in ({account_id_from}, {account_id_to}) FOR UPDATE;")
                record = await cursor.fetchall()
                accounts_info = [dict(info) for info in record]
                if len(accounts_info) < 2:
                    return web.Response(text=json.dumps({'status': 'rejection', 'reason': 'Not found this accounts.'}),
                                        status=404, content_type='application/json')
                account_from_index = [i for i, _ in enumerate(accounts_info) if _['id'] == int(account_id_from)][0]
                account_to_index = [i for i, _ in enumerate(accounts_info) if _['id'] == int(account_id_to)][0]
                account_balance_from = Decimal(accounts_info[account_from_index]['balance']) - Decimal(amount)
                overdraft = accounts_info[account_from_index]['overdraft']
                account_balance_to = Decimal(
                    accounts_info[account_to_index]["balance"]) + exchange.get(
                    f'{accounts_info[account_from_index]["currency"]}_TO_{accounts_info[account_to_index]["currency"]}'
                )(Decimal(amount))
                if not overdraft and account_balance_from < Decimal(amount):
                    return web.Response(text=json.dumps({'status': 'rejection', 'reason': 'Not enough balance.'}),
                                        status=403, content_type='application/json')
                await conn.execute(
                    f"UPDATE account SET balance = CASE id "
                    f"WHEN {account_id_from} THEN {account_balance_from} "
                    f"WHEN {account_id_to} THEN {account_balance_to} END "
                    f"WHERE id in ({account_id_from}, {account_id_to});")
                await conn.execute(db.invoice.insert().values(
                    account_id_from=account_id_from, account_id_to=account_id_to, amount=amount,))
            return web.Response(text=json.dumps({'status': 'success'}), status=201, content_type='application/json')
    except Exception as e:
        return web.Response(text=json.dumps({'status': 'failed', 'reason': str(e)}),
                            status=500, content_type='application/json')
