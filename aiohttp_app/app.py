import asyncpgsa
from aiohttp import web

from aiohttp_app.views.views import routes


async def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_shutdown)
    return app


async def on_start(app):
    db_settings = 'postgres://postgres:postgres@localhost:5432/demo'

    app['db'] = await asyncpgsa.create_pool(
        dsn=db_settings,
        command_timeout=60,
        min_size=10, max_size=10
    )


async def on_shutdown(app):
    await app['db'].close()


