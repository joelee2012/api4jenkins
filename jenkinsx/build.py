# encoding: utf-8

import re
import time

from .item import Item
from .mix import DescriptionMix, DeletionMix


class Build(Item, DescriptionMix, DeletionMix):

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
        self.handle_req('POST', 'stop', allow_redirects=False)

    def term(self):
        self.handle_req('POST', 'term', allow_redirects=False)

    def kill(self):
        self.handle_req('POST', 'kill', allow_redirects=False)

    def retrigger(self):
        pass

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
        job_name = self.jenkins._url2name(re.sub(r'\w+[/]?$', '', self.url))
        return self.jenkins.get_job(job_name)


class WorkflowRun(Build):
    pass


class FreeStyleBuild(Build):
    pass


class MatrixBuild(Build):
    pass
