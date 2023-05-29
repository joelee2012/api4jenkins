# encoding: utf-8
import logging
from httpx import Client, HTTPTransport, AsyncClient, AsyncHTTPTransport
from .exceptions import ItemNotFoundError, ServerError, AuthenticationError, BadRequestError
from .__version__ import __title__, __version__


logger = logging.getLogger(__name__)


def log_request(request):
    logger.debug(
        f"Send Request: {request.method} {request.url} - Waiting for response")


def check_response(response):
    # request = response.request
    # logger.debug(
    #     f"Response event hook: {request.method} {request.url} - Status {response.status_code}")
    if response.is_success or response.is_redirect:
        return
    if response.status_code == 404:
        raise ItemNotFoundError(f'404 Not found {response.url}')
    if response.status_code == 401:
        raise AuthenticationError(
            f'401 Invalid authorization for {response.url}')
    if response.status_code == 403:
        raise PermissionError(f'403 No permission to access {response.url}')
    if response.status_code == 400:
        raise BadRequestError(f'400 {response.headers["X-Error"]}')
    response.raise_for_status()


def new_http_client(**kwargs):
    transport = HTTPTransport(retries=kwargs.pop('max_retries', 1))
    client = Client(transport=transport, **kwargs,
                    event_hooks={'request': [log_request], 'response': [check_response]})
    client.headers = {'User-Agent': f'{__title__}/{__version__}'}
    return client


async def alog_request(request):
    log_request(request)


async def acheck_response(response):
    check_response(response)


def new_async_http_client(**kwargs):
    transport = AsyncHTTPTransport(retries=kwargs.pop('max_retries', 1))
    client = AsyncClient(transport=transport, **kwargs,
                         event_hooks={'request': [alog_request], 'response': [acheck_response]})
    client.headers = {'User-Agent': f'{__title__}/{__version__}'}
    return client
