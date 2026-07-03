# encoding: utf-8
import json
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterator, AsyncIterator, Optional, List
from httpx import Response

from .item import AsyncItem, Item


class PluginsManager(Item):

    def get(self, name: str) -> Optional['Plugin']:
        for plugin in self.api_json(tree='plugins[shortName]')['plugins']:
            if plugin['shortName'] == name:
                return Plugin(self.jenkins, f'{self.url}plugin/{name}/')
        return None

    def install(self, *names: str, block: bool = False) -> Response:
        plugin_xml = ET.Element('jenkins')
        for name in names:
            if '@' not in name:
                name += '@latest'
            ET.SubElement(plugin_xml, 'install', {'plugin': name})
        resp = self.handle_req('POST', 'installNecessaryPlugins',
                             headers=self.headers,
                             content=ET.tostring(plugin_xml))

        while block and not self.installation_done:
            time.sleep(2)
        return resp

    def uninstall(self, *names: str) -> List[Response]:
        responses = []
        for name in names:
            responses.append(
                self.handle_req('POST', f'plugin/{name}/doUninstall')
            )
        return responses

    def set_site(self, url: str) -> Response:
        resp = self.handle_req('POST', 'siteConfigure', params={'site': url})
        self.check_updates_server()
        return resp

    def check_updates_server(self) -> Response:
        return self.handle_req('POST', 'checkUpdatesServer')

    @property
    def update_center(self) -> 'UpdateCenter':
        return UpdateCenter(self.jenkins, f'{self.jenkins.url}updateCenter/')

    @property
    def site(self) -> Optional[str]:
        return self.update_center.site

    @property
    def restart_required(self) -> bool:
        return self.update_center.restart_required

    @property
    def installation_done(self) -> bool:
        return self.update_center.installation_done

    def set_proxy(self, name: str, port: int, *, username: str = '',
                  password: str = '', no_proxy: str = '', test_url: str = '') -> Response:
        data = {'name': name, 'port': port, 'userName': username,
                'password': password, 'noProxyHost': no_proxy,
                'testUrl': test_url}
        return self.handle_req('POST', 'proxyConfigure', data={
            'json': json.dumps(data)})

    def __iter__(self) -> Iterator['Plugin']:
        for plugin in self.api_json(tree='plugins[shortName]')['plugins']:
            yield Plugin(self.jenkins,
                        f'{self.url}plugin/{plugin["shortName"]}/')


class Plugin(Item):
    def uninstall(self) -> Response:
        return self.handle_req('POST', 'doUninstall')


class UpdateCenter(Item):

    @property
    def installation_done(self) -> bool:
        resp = self.handle_req('GET', 'installStatus')
        return all(job['installStatus'] != 'Pending'
                  for job in resp.json()['data']['jobs'])

    @property
    def restart_required(self) -> bool:
        return bool(self.api_json(tree='restartRequiredForCompletion').get(
            'restartRequiredForCompletion'))

    @property
    def site(self) -> Optional[str]:
        return self.api_json(tree='sites[url]')['sites'][0].get('url')


# async class

class AsyncPluginsManager(AsyncItem):

    async def get(self, name: str) -> Optional['AsyncPlugin']:
        data = await self.api_json(tree='plugins[shortName]')
        for plugin in data['plugins']:
            if plugin['shortName'] == name:
                return AsyncPlugin(self.jenkins, f'{self.url}plugin/{name}/')
        return None

    async def install(self, *names: str, block: bool = False) -> None:
        plugin_xml = ET.Element('jenkins')
        for name in names:
            if '@' not in name:
                name += '@latest'
            ET.SubElement(plugin_xml, 'install', {'plugin': name})
        await self.handle_req('POST', 'installNecessaryPlugins',
                              headers=self.headers,
                              content=ET.tostring(plugin_xml))

        while block and not await self.installation_done:
            time.sleep(2)

    async def uninstall(self, *names: str) -> None:
        for name in names:
            await self.handle_req('POST', f'plugin/{name}/doUninstall')

    async def set_site(self, url: str) -> None:
        await self.handle_req('POST', 'siteConfigure', params={'site': url})
        await self.check_updates_server()

    async def check_updates_server(self) -> None:
        await self.handle_req('POST', 'checkUpdatesServer')

    @property
    def update_center(self) -> 'AsyncUpdateCenter':
        return AsyncUpdateCenter(self.jenkins, f'{self.jenkins.url}updateCenter/')

    @property
    async def site(self) -> Optional[str]:
        return await self.update_center.site

    @property
    async def restart_required(self) -> bool:
        return await self.update_center.restart_required

    @property
    async def installation_done(self) -> bool:
        return await self.update_center.installation_done

    async def set_proxy(self, name: str, port: int, *, username: str = '',
                        password: str = '', no_proxy: str = '',
                        test_url: str = '') -> Response:
        data = {'name': name, 'port': port, 'userName': username,
                'password': password, 'noProxyHost': no_proxy,
                'testUrl': test_url}
        await self.handle_req('POST', 'proxyConfigure', data={
            'json': json.dumps(data)})

    async def __aiter__(self) -> AsyncIterator['AsyncPlugin']:
        data = await self.api_json(tree='plugins[shortName]')
        for plugin in data['plugins']:
            yield AsyncPlugin(self.jenkins,
                            f'{self.url}plugin/{plugin["shortName"]}/')


class AsyncPlugin(AsyncItem):
    async def uninstall(self) -> Response:
        return await self.handle_req('POST', 'doUninstall')


class AsyncUpdateCenter(AsyncItem):

    @property
    async def installation_done(self) -> bool:
        resp = await self.handle_req('GET', 'installStatus')
        return all(job['installStatus'] != 'Pending'
                  for job in resp.json()['data']['jobs'])

    @property
    async def restart_required(self) -> bool:
        data = await self.api_json(tree='restartRequiredForCompletion')
        return bool(data.get('restartRequiredForCompletion'))

    @property
    async def site(self) -> Optional[str]:
        data = await self.api_json(tree='sites[url]')
        return data['sites'][0].get('url')
