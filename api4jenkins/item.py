# encoding: utf-8

import contextlib
import re
from importlib import import_module
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, ContextManager, AsyncContextManager
from httpx import Response

import api4jenkins

from .exceptions import ItemNotFoundError


def camel(s: str) -> str:
    if s[0] == '_':
        return s
    first, *other = s.split('_')
    return first.lower() + ''.join(x.title() for x in other)


def _snake() -> Any:
    pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def func(name: str) -> str:
        return pattern.sub('_', name).lower()
    return func


snake = _snake()


def append_slash(url: str) -> str:
    return url if url[-1] == '/' else f'{url}/'


def _new_item() -> Any:
    delimiter = re.compile(r'[.$]')

    def func(jenkins, module, item):
        class_name = delimiter.split(item['_class'])[-1]
        if isinstance(jenkins, api4jenkins.AsyncJenkins):
            class_name = f'Async{class_name}'
        mod = import_module(module)
        if not hasattr(mod, class_name):
            msg = f'''{mod} has no class {class_name} to describe
                  {item["url"]}, patch new class with api4jenkins._patch_to,
                  see: https://api4jenkins.readthedocs.io/en/latest/user/example.html#patch'''
            raise AttributeError(msg)
        _class = getattr(mod, class_name)
        return _class(jenkins, item['url'])

    return func


new_item = _new_item()


class BaseItem:
    headers: Dict[str, str] = {'Content-Type': 'text/xml; charset=utf-8'}
    _attr_names: List[str] = []

    def __init__(self, jenkins: Any, url: str) -> None:
        self.jenkins = jenkins
        self.url = append_slash(url)
        self._request = jenkins.http_client.request
        self._stream = jenkins.http_client.stream

    def _new_item(self, module: str, item: Dict[str, Any]) -> Any:
        return new_item(self.jenkins, module, item)

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.url == other.url

    def __str__(self):
        return f'<{type(self).__name__}: {self.url}>'

    def _add_crumb(self, crumb: Optional[Dict[str, str]], kwargs: Dict[str, Any]) -> None:
        if crumb:
            headers = kwargs.get('headers', {})
            headers.update(crumb)
            kwargs['headers'] = headers

    @classmethod
    def _get_attr_names(cls, api_json: Dict[str, Any]) -> None:
        types = (int, str, bool, type(None))
        cls._attr_names = [snake(k)
                           for k in api_json if isinstance(api_json[k], types)]


class Item(BaseItem):

    def api_json(self, tree: str = '', depth: int = 0) -> Dict[str, Any]:
        params = {'depth': depth}
        if tree:
            params['tree'] = tree
        return self.handle_req('GET', 'api/json', params=params).json()

    def handle_req(self, method: str, entry: str, **kwargs: Any) -> Response:
        self._add_crumb(self.jenkins.crumb, kwargs)
        return self._request(method, self.url + entry, **kwargs)

    @contextlib.contextmanager
    def handle_stream(self, method: str, entry: str, **kwargs: Any) -> Iterator[Response]:
        self._add_crumb(self.jenkins.crumb, kwargs)
        with self._stream(method, self.url + entry, **kwargs) as response:
            yield response

    def exists(self) -> bool:
        try:
            self.api_json(tree='_class')
            return True
        except ItemNotFoundError:
            return False

    @property
    def dynamic_attrs(self) -> List[str]:
        if not self._attr_names:
            self._get_attr_names(self.api_json())
        return self._attr_names

    def __getattr__(self, name: str) -> Any:
        if name in self.dynamic_attrs:
            attr = camel(name)
            return self.api_json(tree=attr)[attr]
        return super().__getattribute__(name)

    def __getitem__(self, name: Union[str, int]) -> Any:
        if hasattr(self, 'get'):
            return self.get(name)
        raise TypeError(f"'{type(self).__name__}' object is not subscriptable")

    def iter(self) -> None:
        raise TypeError(f"'{type(self).__name__}' object is not iterable")

    def __iter__(self) -> Iterator[Any]:
        yield from self.iter()


class AsyncItem(BaseItem):

    async def api_json(self, tree: str = '', depth: int = 0) -> Dict[str, Any]:
        params = {'depth': depth}
        if tree:
            params['tree'] = tree
        return (await self.handle_req('GET', 'api/json', params=params)).json()

    async def handle_req(self, method: str, entry: str, **kwargs: Any) -> Response:
        self._add_crumb(await self.jenkins.crumb, kwargs)
        return await self._request(method, self.url + entry, **kwargs)

    @contextlib.asynccontextmanager
    async def handle_stream(self, method: str, entry: str, **kwargs: Any) -> AsyncIterator[Response]:
        self._add_crumb(await self.jenkins.crumb, kwargs)
        async with self._stream(method, self.url + entry, **kwargs) as response:
            yield response

    async def exists(self) -> bool:
        try:
            await self.api_json(tree='_class')
            return True
        except ItemNotFoundError:
            return False

    @property
    async def dynamic_attrs(self) -> List[str]:
        if not self._attr_names:
            self._get_attr_names(await self.api_json())
        return self._attr_names

    async def __getattr__(self, name: str) -> Any:
        if name in (await self.dynamic_attrs):
            attr = camel(name)
            return (await self.api_json(tree=attr))[attr]
        return super().__getattribute__(name)

    async def __getitem__(self, name: Union[str, int]) -> Any:
        if hasattr(self, 'get'):
            return await self.get(name)
        raise TypeError(f"'{type(self).__name__}' object is not subscriptable")

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Default implementation raises TypeError since most items are not iterable.
        Subclasses that support iteration should override this method."""
        raise TypeError(f"'{type(self).__name__}' object is not iterable")
        yield  # This makes it a generator function but is never reached
