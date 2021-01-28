import json

from .item import Item


class PendingInputAction(Item):
    ''' this class implement functionality to process
    `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_
    '''

    def __init__(self, jenkins, raw):
        super().__init__(
            jenkins, f"{jenkins.url}{raw['abortUrl'].rstrip('abort')}")
        self.raw = raw
        self.raw['_class'] = 'PendingInputAction'

    def api_json(self, tree='', depth=0):
        return self.raw

    def abort(self):
        '''submit `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_'''
        return self.handle_req('POST', 'abort')

    def submit(self, **params):
        '''submit `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_

        - for input requires parametes:
            - if submit without parameters, it will use default value of parameters
            - if submit with wrong parameters, exception raised
        - for input does not requires parameters, but submit with paramters, exception raised
        '''
        if params:
            args = [a['name'] for a in self.raw['inputs']]
            params_keys = list(params.keys())
            if not args:
                raise TypeError(
                    f'input takes 0 argument, but got {params_keys}')
            if not all(k in args for k in params_keys):
                raise TypeError(
                    f'input takes arguments: {args}, but got {params_keys}')
            params = [{'name': k, 'value': v} for k, v in params.items()]
            data = {'proceed': self.raw['proceedText'],
                    'json': json.dumps({'parameter': params})}
            return self.handle_req('POST', 'submit', data=data)
        else:
            return self.handle_req('POST', 'proceedEmpty')
