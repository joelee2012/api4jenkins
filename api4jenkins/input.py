import json

from .item import Item


class PendingInputAction(Item):

    def __init__(self, jenkins, raw):
        ''' see https://github.com/jenkinsci/pipeline-stage-view-plugin/tree/master/rest-api
        '''
        super().__init__(
            jenkins, f"{jenkins.url}{raw['redirectApprovalUrl']}{raw['id']}/")
        self.raw = raw
        self.raw['_class'] = 'PendingInputAction'

    def api_json(self, tree='', depth=0):
        return self.raw

    def abort(self):
        self._item.handle_req('POST', 'abort')

    def submit(self, **params):
        if params:
            params = [{'name': k, 'value': v} for k, v in params.items()]
            data = {'proceed': self.raw['proceedText'],
                    'json': json.dumps({'parameter': params})}
            self.handle_req('POST', 'submit', data=data)
        else:
            self.handle_req('POST', 'proceedEmpty')
