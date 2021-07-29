# encoding: utf-8
import json
from functools import partial

from .artifact import save_response_to
from .item import Item, snake
from .mix import RunScriptMixIn


class System(Item, RunScriptMixIn):

    def __init__(self, jenkins, url):
        '''
        see: https://support.cloudbees.com/hc/en-us/articles/216118748-How-to-Start-Stop-or-Restart-your-Instance-
        '''
        super().__init__(jenkins, url)

        def _post(entry):
            return self.handle_req('POST', entry, allow_redirects=False)

        for entry in ['restart', 'safeRestart', 'exit',
                      'safeExit', 'quietDown', 'cancelQuietDown']:
            setattr(self, snake(entry), partial(_post, entry))

    def reload_jcasc(self):
        return self.handle_req('POST', 'configuration-as-code/reload')

    def export_jcasc(self, filename='jenkins.yaml'):
        with self.handle_req('POST', 'configuration-as-code/export') as resp:
            save_response_to(resp, filename)

    def apply_jcasc(self, new):
        params = {"newSource": new}
        resp = self.handle_req(
            'POST', 'configuration-as-code/checkNewSource', params=params)
        if resp.text.startswith('<div class=error>'):
            raise ValueError(resp.text)
        d = {'json': json.dumps(params),
             'replace': 'Apply new configuration'}
        return self.handle_req('POST', 'configuration-as-code/replace', data=d)

    def decrypt_secret(self, text):
        cmd = f'println(hudson.util.Secret.decrypt("{text}"))'
        return self.run_script(cmd)
