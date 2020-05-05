from aiohttp import web

from views import account_get, account_post, invoice_post
from settings import config
from db import close_pg, init_pg

from aiohttp_swagger import *


app = web.Application()

app.router.add_route('GET', "/account", account_get)
app.router.add_route('POST', "/account", account_post)
app.router.add_route('POST', "/invoice", invoice_post)


app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

app['config'] = config
setup_swagger(app, swagger_url="/api/v1")

web.run_app(app, host="127.0.0.1")
