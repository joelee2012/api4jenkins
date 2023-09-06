# encoding: utf-8
import json
import time
import xml.etree.ElementTree as ET

from .item import AsyncItem, Item


class PluginsManager(Item):

    def get(self, name):
        for plugin in self.api_json(tree='plugins[shortName]')['plugins']:
            if plugin['shortName'] == name:
                return Plugin(self.jenkins, f'{self.url}plugin/{name}/')
        return None

    def install(self, *names, block=False):
        plugin_xml = ET.Element('jenkins')
        for name in names:
            if '@' not in name:
                name += '@latest'
            ET.SubElement(plugin_xml, 'install', {'plugin': name})
        self.handle_req('POST', 'installNecessaryPlugins',
                        headers=self.headers,
                        content=ET.tostring(plugin_xml))

        while block and not self.installation_done:
            time.sleep(2)

    def uninstall(self, *names):
        for name in names:
            self.handle_req('POST', f'plugin/{name}/doUninstall')

    def set_site(self, url):
        self.handle_req('POST', 'siteConfigure', params={'site': url})
        self.check_updates_server()

    def check_updates_server(self):
        self.handle_req('POST', 'checkUpdatesServer')

    @property
    def update_center(self):
        return UpdateCenter(self.jenkins, f'{self.jenkins.url}updateCenter/')

    @property
    def site(self):
        return self.update_center.site

    @property
    def restart_required(self):
        return self.update_center.restart_required

    @property
    def installation_done(self):
        return self.update_center.installation_done

    def set_proxy(self, name, port, *, username='',
                  password='', no_proxy='', test_url=''):
        data = {'name': name, 'port': port, 'userName': username,
                'password': password, 'noProxyHost': no_proxy,
                'testUrl': test_url}
        self.handle_req('POST', 'proxyConfigure', data={
                        'json': json.dumps(data)})

    def __iter__(self):
        for plugin in self.api_json(tree='plugins[shortName]')['plugins']:
            yield Plugin(self.jenkins,
                         f'{self.url}plugin/{plugin["shortName"]}/')


class Plugin(Item):
    def uninstall(self):
        self.handle_req('POST', 'doUninstall')


class UpdateCenter(Item):

    @property
    def installation_done(self):
        resp = self.handle_req('GET', 'installStatus')
        return all(job['installStatus'] != 'Pending'
                   for job in resp.json()['data']['jobs'])

    @property
    def restart_required(self):
        return self.api_json(tree='restartRequiredForCompletion').get(
            'restartRequiredForCompletion')

    @property
    def site(self):
        return self.api_json(tree='sites[url]')['sites'][0].get('url')


# async class

class AsyncPluginsManager(AsyncItem):

    async def get(self, name):
        data = await self.api_json(tree='plugins[shortName]')
        for plugin in data['plugins']:
            if plugin['shortName'] == name:
                return AsyncPlugin(self.jenkins, f'{self.url}plugin/{name}/')
        return None

    async def install(self, *names, block=False):
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

    async def uninstall(self, *names):
        for name in names:
            await self.handle_req('POST', f'plugin/{name}/doUninstall')

    async def set_site(self, url):
        await self.handle_req('POST', 'siteConfigure', params={'site': url})
        await self.check_updates_server()

    async def check_updates_server(self):
        await self.handle_req('POST', 'checkUpdatesServer')

    @property
    def update_center(self):
        return AsyncUpdateCenter(self.jenkins, f'{self.jenkins.url}updateCenter/')

    @property
    def site(self):
        return self.update_center.site

    @property
    def restart_required(self):
        return self.update_center.restart_required

    @property
    def installation_done(self):
        return self.update_center.installation_done

    async def set_proxy(self, name, port, *, username='',
                        password='', no_proxy='', test_url=''):
        data = {'name': name, 'port': port, 'userName': username,
                'password': password, 'noProxyHost': no_proxy,
                'testUrl': test_url}
        await self.handle_req('POST', 'proxyConfigure', data={
            'json': json.dumps(data)})

    async def __aiter__(self):
        data = await self.api_json(tree='plugins[shortName]')
        for plugin in data['plugins']:
            yield AsyncPlugin(self.jenkins,
                              f'{self.url}plugin/{plugin["shortName"]}/')


class AsyncPlugin(AsyncItem):
    async def uninstall(self):
        await self.handle_req('POST', 'doUninstall')


class AsyncUpdateCenter(AsyncItem):

    @property
    async def installation_done(self):
        resp = await self.handle_req('GET', 'installStatus')
        return all(job['installStatus'] != 'Pending'
                   for job in resp.json()['data']['jobs'])

    @property
    async def restart_required(self):
        data = await self.api_json(tree='restartRequiredForCompletion')
        return data.get('restartRequiredForCompletion')

    @property
    async def site(self):
        data = await self.api_json(tree='sites[url]')
        return data['sites'][0].get('url')
