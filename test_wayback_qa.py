# live web leaks? logic equal to what we have done before
# 4. compare against previous generated results
# 5.fetch screenshots also
# image compare with screenshots

import hashlib
import json
from collections import Counter, defaultdict

import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

pytest_plugins = ["docker_compose"]

counters = defaultdict()


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
    with open('testfiles/test_urls_list.txt', mode='r') as fl:
        for line in fl.readlines():
            url = line.strip()
            url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
            fp = open('testfiles/hars/{}.har'.format(url_hash))
            js = json.load(fp)

            counter = Counter()
            for entrie in js['log']['entries']:
                counter[entrie['response']['status']] = counter[entrie['response']['status']] + 1
            counters[url_hash] = counter


def fill_replay_counter(har_json):
    replay_counter_test = Counter()
    for entry in har_json['log']['entries']:
        replay_counter_test[entry['response']['status']] = replay_counter_test[entry['response']['status']] + 1
    return replay_counter_test


def test_replay_status_codes(launch_webrender):
    webrender_url = launch_webrender

    with open('testfiles/test_urls_list.txt', mode='r') as fl:
        for line in fl.readlines():
            url = line.strip()
            print("Testing replay for URL: {} ....".format(url))
            url_hash = hashlib.md5(url.encode('utf8')).hexdigest()

            res = requests.get(url='{}/har'.format(webrender_url), params={
                'url': url})
            har_json = json.loads(res.content)

            replay_counter = fill_replay_counter(har_json)
            print(replay_counter)
            print(counters[url_hash])
            assert replay_counter[200] >= counters[url_hash][200]
