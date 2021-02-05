from .item import Item


class Artifact(Item):

    def __init__(self, jenkins, raw):
        super().__init__(
            jenkins, f"{jenkins.url}{raw['url'][1:]}")
        # remove trailing slash
        self.url = self.url[:-1]
        self.raw = raw
        self.raw['_class'] = 'Artifact'

    def api_json(self, tree='', depth=0):
        return self.raw

    def save(self, to=None):
        if not to:
            to = self.name
        with self.handle_req('GET', '') as resp:
            save_response_to(resp, to)


def save_response_to(response, to):
    with open(to, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
