# encoding: utf-8
import json
from functools import partial

from .item import AsyncItem, Item, snake
from .mix import AsyncRunScriptMixIn, RunScriptMixIn


class System(Item, RunScriptMixIn):

    def __init__(self, jenkins, url):
        '''
        see: https://support.cloudbees.com/hc/en-us/articles/216118748-How-to-Start-Stop-or-Restart-your-Instance-
        '''
        super().__init__(jenkins, url)

        def _post(entry):
            return self.handle_req('POST', entry)

        for entry in ['restart', 'safeRestart', 'exit',
                      'safeExit', 'quietDown', 'cancelQuietDown']:
            setattr(self, snake(entry), partial(_post, entry))

    def reload_jcasc(self):
        return self.handle_req('POST', 'configuration-as-code/reload')

    def export_jcasc(self):
        return self.handle_req('POST', 'configuration-as-code/export').text

    def apply_jcasc(self, content):
        params = {"newSource": content}
        resp = self.handle_req(
            'POST', 'configuration-as-code/checkNewSource', params=params)
        if resp.text.startswith('<div class=error>'):
            raise ValueError(resp.text)
        data = {'json': json.dumps(params),
                'replace': 'Apply new configuration'}
        return self.handle_req('POST', 'configuration-as-code/replace', data=data)

    def decrypt_secret(self, text):
        cmd = f'println(hudson.util.Secret.decrypt("{text}"))'
        return self.run_script(cmd)

# async class


class AsyncSystem(AsyncItem, AsyncRunScriptMixIn):

    def __init__(self, jenkins, url):
        '''
        see: https://support.cloudbees.com/hc/en-us/articles/216118748-How-to-Start-Stop-or-Restart-your-Instance-
        '''
        super().__init__(jenkins, url)

        async def _post(entry):
            return await self.handle_req('POST', entry)

        for entry in ['restart', 'safeRestart', 'exit',
                      'safeExit', 'quietDown', 'cancelQuietDown']:
            setattr(self, snake(entry), partial(_post, entry))

    async def reload_jcasc(self):
        return await self.handle_req('POST', 'configuration-as-code/reload')

    async def export_jcasc(self):
        data = await self.handle_req('POST', 'configuration-as-code/export')
        return data.text

    async def apply_jcasc(self, content):
        params = {"newSource": content}
        resp = await self.handle_req(
            'POST', 'configuration-as-code/checkNewSource', params=params)
        if resp.text.startswith('<div class=error>'):
            raise ValueError(resp.text)
        data = {'json': json.dumps(params),
                'replace': 'Apply new configuration'}
        return await self.handle_req('POST', 'configuration-as-code/replace', data=data)

    async def decrypt_secret(self, text):
        cmd = f'println(hudson.util.Secret.decrypt("{text}"))'
        return await self.run_script(cmd)
