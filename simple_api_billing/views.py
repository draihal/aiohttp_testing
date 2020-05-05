from aiohttp import web
import db
import json


EUR_TO_USD = 1.24
EUR_TO_RUB = 70.53
USD_TO_RUB = 56.80

CURRENCY_TYPE = ('USD', 'EUR', 'RUB')
BOOLEAN_TYPE = ('True', 'False', 'true', 'false')


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
            description: Bad request. Need args: integer(id).
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
            return web.Response(
                text=json.dumps(account_info, ensure_ascii=False, default=str),
                status=200,
                content_type='application/json')
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500, content_type='application/json')


def boolean_parse(string):
    # boolean_dict = {'True': True, 'False': False}
    # return boolean_dict.get(string, string)
    return string.capitalize() == "True"


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
            description: Bad request. Need args: integer(currency), boolean(overdraft).
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
            overdraft = boolean_parse(request.query['overdraft'])
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
        "405":
            description: Invalid HTTP Method.
        "500":
            description: Server error.
    """
    pass
