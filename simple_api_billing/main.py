from aiohttp import web
from views import ping
from aiohttp_swagger import *


app = web.Application()
app.router.add_route('GET', "/ping/", ping)

setup_swagger(app, swagger_url="/api/v1", ui_version=2)

web.run_app(app, host="127.0.0.1")
