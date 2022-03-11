# encoding: utf-8
from .item import Item
from .mix import RawJsonMixIn


class Artifact(RawJsonMixIn, Item):

    def __init__(self, jenkins, raw):
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    def save(self, filename=None):
        if not filename:
            filename = self.name
        with self.handle_req('GET', '') as resp:
            save_response_to(resp, filename)


def save_response_to(response, filename):
    with open(filename, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
