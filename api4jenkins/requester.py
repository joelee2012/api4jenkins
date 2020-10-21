# encoding: utf-8
from pprint import pformat
import logging
from requests import Session, adapters


logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 1


def Requester(**kwargs):
    # Remote end closed connection without
    # response on successive Session requests maybe happen
    # see: https://github.com/psf/requests/issues/4784
    # and https://github.com/psf/requests/issues/4664
    session = Session()
    max_retries = kwargs.pop('max_retries', DEFAULT_MAX_RETRIES)
    adapter = adapters.HTTPAdapter(max_retries=max_retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    def send(method, url, **kw):
        logger.debug('%s: %s with parameters: %s',
                     method, url, pformat(kw))
        resp = session.request(method, url, **kwargs, **kw)
        logger.debug('Response: %s', resp)
        resp.raise_for_status()
        return resp

    return send
