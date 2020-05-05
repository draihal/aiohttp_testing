from aiohttp import web
import db
import json
# from aiohttp_validate import validate


EUR_TO_USD = 1.24
EUR_TO_RUB = 70.53
USD_TO_RUB = 56.80


# @validate(  # TODO: add validation?
#     request_schema={
#         "type": "object",
#         "properties": {
#             "id": {"type": "integer"},
#         },
#         "required": ["id"],
#         "additionalProperties": False
#     },
#     response_schema=None
# )
async def account_get(request):
    """
    ---
    description: This end-point allow to get account info.
    tags:
    - Account
    produces:
    - application/json
    responses:
        "200":
            description: successful operation. Return account info
        "405":
            description: invalid HTTP Method
        "500":
            description: server error
    """
    try:
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


async def account_post(request):
    pass


async def invoice_post(request):
    pass
