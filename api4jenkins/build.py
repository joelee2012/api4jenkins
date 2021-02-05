# encoding: utf-8

import re
import time

from .artifact import Artifact, save_response_to
from .input import PendingInputAction
from .item import Item
from .mix import DeletionMixIn, DescriptionMixIn


class Build(Item, DescriptionMixIn, DeletionMixIn):

    def console_text(self, stream=False):
        with self.handle_req('GET', 'consoleText', stream=stream) as resp:
            for line in resp.iter_lines():
                yield line

    def progressive_output(self, html=False):
        url = 'logText/progressiveHtml' if html else 'logText/progressiveText'
        start = 0
        while True:
            resp = self.handle_req('GET', url, params={'start': start})
            time.sleep(1)
            if start == resp.headers.get('X-Text-Size'):
                continue
            yield resp.text
            if not resp.headers.get('X-More-Data'):
                break
            start = resp.headers['X-Text-Size']

    def stop(self):
        return self.handle_req('POST', 'stop', allow_redirects=False)

    def term(self):
        return self.handle_req('POST', 'term', allow_redirects=False)

    def kill(self):
        return self.handle_req('POST', 'kill', allow_redirects=False)

    def get_next_build(self):
        item = self.api_json(tree='nextBuild[url]')['nextBuild']
        if item:
            return self.__class__(self.jenkins, item['url'])
        return None

    def get_previous_build(self):
        item = self.api_json(tree='previousBuild[url]')['previousBuild']
        if item:
            return self.__class__(self.jenkins, item['url'])
        return None

    def get_job(self):
        '''get job of this build'''
        job_name = self.jenkins._url2name(re.sub(r'\w+[/]?$', '', self.url))
        return self.jenkins.get_job(job_name)


class WorkflowRun(Build):

    def get_pending_input(self):
        '''get current pending input step'''
        data = self.handle_req('GET', 'wfapi/describe').json()
        if not data['_links'].get('pendingInputActions'):
            return None
        action = self.handle_req('GET', 'wfapi/pendingInputActions').json()[0]
        return PendingInputAction(self.jenkins, action)

    def get_artifacts(self):
        artifacts = self.handle_req('GET', 'wfapi/artifacts').json()
        if not artifacts:
            return []
        for artifact in artifacts:
            yield Artifact(self.jenkins, artifact)

    def save_artifacts(self, to='archive.zip'):
        with self.handle_req('GET', 'artifact/*zip*/archive.zip') as resp:
            save_response_to(resp, to)


class FreeStyleBuild(Build):
    pass


class MatrixBuild(Build):
    pass
