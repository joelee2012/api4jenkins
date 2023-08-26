# encoding: utf-8
import json

from .item import AsyncItem, Item
from .mix import AsyncRawJsonMixIn, RawJsonMixIn


class PendingInputAction(RawJsonMixIn, Item):
    ''' this class implement functionality to process
    `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_
    '''

    def __init__(self, jenkins, raw):
        super().__init__(
            jenkins, f"{jenkins.url}{raw['abortUrl'].rstrip('abort').lstrip('/')}")
        self.raw = raw
        self.raw['_class'] = 'PendingInputAction'

    def abort(self):
        '''submit `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_'''
        return self.handle_req('POST', 'abort')

    def submit(self, **params):
        '''submit `input step <https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/>`_

        - if input requires parameters:
            - if submit without parameters, it will use default value of parameters
            - if submit with wrong parameters, exception raised
        - if input does not requires parameters, but submit with parameters, exception raised
        '''
        if params:
            data = _make_input_params(self.raw, **params)
            return self.handle_req('POST', 'submit', data=data)
        return self.handle_req('POST', 'proceedEmpty')


def _make_input_params(api_json, **params):
    input_args = [input['name'] for input in api_json['inputs']]
    params_keys = list(params.keys())
    if not input_args:
        raise TypeError(f'input takes 0 argument, but got {params_keys}')
    if any(k not in input_args for k in params_keys):
        raise TypeError(
            f'input takes arguments: {input_args}, but got {params_keys}')
    params = [{'name': k, 'value': v} for k, v in params.items()]
    return {'proceed': api_json['proceedText'],
            'json': json.dumps({'parameter': params})}


class AsyncPendingInputAction(AsyncRawJsonMixIn, AsyncItem):
    def __init__(self, jenkins, raw):
        super().__init__(
            jenkins, f"{jenkins.url}{raw['abortUrl'].rstrip('abort').lstrip('/')}")
        self.raw = raw
        self.raw['_class'] = 'AsyncPendingInputAction'

    async def abort(self):
        return await self.handle_req('POST', 'abort')

    async def submit(self, **params):
        if params:
            data = _make_input_params(self.raw, **params)
            return await self.handle_req('POST', 'submit', data=data)
        return await self.handle_req('POST', 'proceedEmpty')
