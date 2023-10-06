# encoding: utf-8

# pylint: disable=no-member
# type: ignore
from collections import namedtuple
from pathlib import PurePosixPath


class UrlMixIn:
    __slots__ = ()

    def _url2name(self, url):
        if not url.startswith(self.url):
            raise ValueError(f'{url} is not in {self.url}')
        return url.replace(self.url, '/').replace('/job/', '/').strip('/')

    def _name2url(self, full_name):
        if not full_name:
            return self.url
        full_name = full_name.strip('/').replace('/', '/job/')
        return f'{self.url}job/{full_name}/'

    def _parse_name(self, full_name):
        if full_name.startswith(('http://', 'https://')):
            full_name = self._url2name(full_name)
        path = PurePosixPath(full_name)
        parent = str(path.parent) if path.parent.name else ''
        return parent, path.name


class DeletionMixIn:
    __slots__ = ()

    def delete(self):
        self.handle_req('POST', 'doDelete')


class ConfigurationMixIn:
    __slots__ = ()

    def configure(self, xml=None):
        if not xml:
            return self.handle_req('GET', 'config.xml').text
        return self.handle_req('POST', 'config.xml',
                               headers=self.headers, content=xml)

    @property
    def name(self):
        return self.url.split('/')[-2]


class DescriptionMixIn:
    __slots__ = ()

    def set_description(self, text):
        self.handle_req('POST', 'submitDescription',
                        params={'description': text})


class RunScriptMixIn:
    __slots__ = ()

    def run_script(self, script):
        return self.handle_req('POST', 'scriptText',
                               data={'script': script}).text


class EnableMixIn:
    __slots__ = ()

    def enable(self):
        return self.handle_req('POST', 'enable')

    def disable(self):
        return self.handle_req('POST', 'disable')


class RawJsonMixIn:
    __slots__ = ()

    def api_json(self, tree='', depth=0):
        return self.raw


Parameter = namedtuple('Parameter', ['class_name', 'name', 'value'])


class ActionsMixIn:
    __slots__ = ()

    def get_parameters(self):
        parameters = []
        for action in self.api_json()['actions']:
            if 'parameters' in action:
                parameters.extend(Parameter(raw['_class'], raw['name'], raw.get(
                    'value', '')) for raw in action['parameters'])
                break
        return parameters

    def get_causes(self):
        return next((action['causes'] for action in self.api_json()['actions'] if 'causes' in action), [])


# async classes


class AsyncDeletionMixIn:
    __slots__ = ()

    async def delete(self):
        await self.handle_req('POST', 'doDelete')


class AsyncConfigurationMixIn:
    __slots__ = ()

    async def configure(self, xml=None):
        if xml:
            return await self.handle_req('POST', 'config.xml',
                                         headers=self.headers, content=xml)
        return (await self.handle_req('GET', 'config.xml')).text

    @property
    def name(self):
        return self.url.split('/')[-2]


class AsyncDescriptionMixIn:
    __slots__ = ()

    async def set_description(self, text):
        await self.handle_req('POST', 'submitDescription',
                              params={'description': text})


class AsyncRunScriptMixIn:
    __slots__ = ()

    async def run_script(self, script):
        return (await self.handle_req('POST', 'scriptText', data={'script': script})).text


class AsyncEnableMixIn:
    __slots__ = ()

    async def enable(self):
        return await self.handle_req('POST', 'enable')

    async def disable(self):
        return await self.handle_req('POST', 'disable')


class AsyncRawJsonMixIn:
    __slots__ = ()

    async def api_json(self, tree='', depth=0):
        return self.raw


class AsyncActionsMixIn:
    __slots__ = ()

    async def get_parameters(self):
        parameters = []
        data = await self.api_json()
        for action in data['actions']:
            if 'parameters' in action:
                parameters.extend(Parameter(raw['_class'], raw['name'], raw.get(
                    'value', '')) for raw in action['parameters'])
                break
        return parameters

    async def get_causes(self):
        data = await self.api_json()
        return next((action['causes'] for action in data['actions'] if 'causes' in action), [])
