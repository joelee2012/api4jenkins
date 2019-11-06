from pathlib import Path
import json
import logging

import responses


# logging.basicConfig(level=logging.DEBUG)

TEST_DATA_DIR = Path(__file__).with_name('tests_data')
JENKINS_URL = 'http://0.0.0.0:8080/'


def mock_get(*args, **kwargs):
    responses.add(responses.GET, *args, **kwargs)


def mock_post(*args, **kwargs):
    responses.add(responses.POST, *args, **kwargs)


def remove_get(url):
    responses.remove(responses.GET, url)


def replace_get(*args, **kwargs):
    responses.replace(responses.GET, *args, **kwargs)


def responses_count():
    return len(responses.calls)


def load_test_json(name):
    with open(TEST_DATA_DIR.joinpath(name), 'rb') as f:
        return json.load(f)


def load_test_xml(name):
    with open(TEST_DATA_DIR.joinpath(name)) as f:
        return f.read()
