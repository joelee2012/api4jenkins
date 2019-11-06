# encoding: utf-8

# pylint: disable=no-member


class DeletionMix:

    def delete(self):
        self.handle_req('POST', 'doDelete', allow_redirects=False)


class ConfigrationMix:

    def configure(self, xml=None):
        if not xml:
            return self.handle_req('GET', 'config.xml').text
        return self.handle_req('POST', 'config.xml',
                               headers=self.headers, data=xml)


class DescriptionMix:

    def set_description(self, text):
        self.handle_req('POST', 'submitDescription',
                        params={'description': text})


class RunScriptMix:
    def run_script(self, script):
        return self.handle_req('POST', 'scriptText',
                               data={'script': script}).text
