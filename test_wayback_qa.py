# 1. list of replay urls to validate
# 2. get har from replay rendering
# 3. analyze har file
# number of 200s rendered?
# live web leaks? logic equal to what we have done before

# 4. compare against previous generated results
# 5.fetch screenshots also
# image compare with screenshots

import json
from collections import Counter

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

counter_publico2017 = Counter()
counter_jurisapp2019 = Counter()

pytest_plugins = ["docker_compose"]


@pytest.fixture(scope="session", autouse=True)
def launch_webrender(session_scoped_container_getter):
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=10,
                    status_forcelist=[500, 502, 503, 504])
    request_session.mount('http://', HTTPAdapter(max_retries=retries))

    service = session_scoped_container_getter.get("webrender-puppeteer").network_info[0]
    webrender_url = "http://{}:{}".format(service.hostname, service.host_port)

    assert request_session.get(webrender_url)
    return webrender_url


@pytest.fixture(scope="session", autouse=True)
def read_har_files():
    with open('testfiles/publico.2017.har', mode='r') as fl:
        js = json.load(fl)
        for entrie in js['log']['entries']:
            counter_publico2017[entrie['response']['status']] = counter_publico2017[entrie['response']['status']] + 1

    with open('testfiles/jurisapp.2019.ceger.har', mode='r') as fl:
        js = json.load(fl)
        for entrie in js['log']['entries']:
            counter_jurisapp2019[entrie['response']['status']] = counter_jurisapp2019[entrie['response']['status']] + 1


def fill_replay_counter(har_json):
    replay_counter = Counter()
    for entry in har_json['log']['entries']:
        replay_counter[entry['response']['status']] = replay_counter[entry['response']['status']] + 1
    return replay_counter


def test_replay_status_codes(launch_webrender):
    webrender_url = launch_webrender
    res = requests.get(url='{}/har'.format(webrender_url), params={
        'url': 'https://preprod.arquivo.pt/noFrame/replay/20171204180222/https://www.publico.pt/'})
    har_json = json.loads(res.content)

    replay_counter = fill_replay_counter(har_json)
    assert replay_counter[200] >= counter_publico2017[200]

    res = requests.get(url='{}/har'.format(webrender_url), params={
        'url': 'https://preprod.arquivo.pt/noFrame/replay/20190426132340/https://www.jurisapp.gov.pt'})
    har_json = json.loads(res.content)

    replay_counter = fill_replay_counter(har_json)
    assert replay_counter[200] >= counter_jurisapp2019[200]
