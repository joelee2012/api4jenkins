# encoding: utf-8
from .item import Item
from .mix import RunScriptMix


class System(Item, RunScriptMix):

    def restart(self):
        self.handle_req('POST', 'restart', allow_redirects=False)

    def safe_restart(self):
        self.handle_req('POST', 'safeRestart', allow_redirects=False)

    def quiet_down(self):
        self.handle_req('POST', 'quietDown', allow_redirects=False)

    def cancel_quiet_down(self):
        self.handle_req('POST', 'cancelQuietDown', allow_redirects=False)

    def show_credential(self):
        pass

# TODO add groovy to print credential
