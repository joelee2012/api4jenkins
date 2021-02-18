# encoding: utf-8

# pylint: disable=no-member


class DeletionMixIn:

    def delete(self):
        self.handle_req('POST', 'doDelete', allow_redirects=False)


class ConfigurationMixIn:

    def configure(self, xml=None):
        if not xml:
            return self.handle_req('GET', 'config.xml').text
        return self.handle_req('POST', 'config.xml',
                               headers=self.headers, data=xml)


class DescriptionMixIn:

    def set_description(self, text):
        self.handle_req('POST', 'submitDescription',
                        params={'description': text})


class RunScriptMixIn:

    def run_script(self, script):
        return self.handle_req('POST', 'scriptText',
                               data={'script': script}).text


class EnableMixIn:

    def enable(self):
        return self.handle_req('POST', 'enable')

    def disable(self):
        return self.handle_req('POST', 'disable')


class RawJsonMixIn:

    def api_json(self, tree='', depth=0):
        return self.raw
