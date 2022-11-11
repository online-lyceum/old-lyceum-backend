import logging
from typing import Callable
from argparse import ArgumentParser

from aiohttp import web


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

app = web.Application()


def route(url: str, method: str):
    """
    The function generates python decorators.
    Decorated function has to return web.Response object
    :param url: URL address for page
    :param method: HTTP method ("GET" or "POST")
    :return: Decorator
    """
    method = method.lower()

    def decorator(func: Callable) -> Callable:
        if method == 'get':
            app.add_routes([web.get(url, func)])
        elif method == 'post':
            app.add_routes([web.post(url, func)])
        else:
            raise ValueError('Unsupported method')
        return func
    return decorator


class Root:
    @staticmethod
    @route('/', 'get')
    async def get(request):
        logger.debug(request)
        return web.Response(text='This is lyceum asynchronous API')


def run_app():
    parser = ArgumentParser()
    parser.add_argument('-H', '--host', default='0.0.0.0', required=False)
    parser.add_argument('-p', '-P', '--port', default='80', required=False)
    args = parser.parse_args()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    run_app()
