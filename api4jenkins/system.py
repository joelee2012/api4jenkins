# encoding: utf-8
from functools import partial
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


# TODO add groovy to print credential
    # def show_credential(self):
    #     pass
