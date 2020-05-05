from aiohttp import web

from views import ping, index
from settings import config
from db import close_pg, init_pg

from aiohttp_swagger import *


app = web.Application()
app.router.add_route('GET', "/", index)
app.router.add_route('GET', "/ping", ping)


app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

app['config'] = config
setup_swagger(app, swagger_url="/api/v1", ui_version=2)

web.run_app(app, host="127.0.0.1")
