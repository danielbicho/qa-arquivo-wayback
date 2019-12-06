import hashlib
import os

import requests

har_render_endpoint = "http://localhost:9000/har?url="
screenshot_render_endpoint = "http://localhost:9000/screenshot?url="

with open('testfiles/test_urls_list.txt', mode='r') as input_file:
    for url in input_file.readlines():
        url = url.strip()
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        print("Generating {}.har file for: {}".format(url_hash, url))
        response = requests.get(url="{}{}".format(har_render_endpoint, url))
        with open(os.path.join('testfiles/hars', "{}.har".format(url_hash)), mode='wb') as output_file:
            output_file.write(response.content)

        print("Generating {}.screenshot file for: {}".format(url_hash, url))
        response = requests.get(url="{}{}".format(screenshot_render_endpoint, url))
        with open(os.path.join('testfiles/screenshots', "{}.screenshot".format(url_hash)), mode='wb') as output_file:
            output_file.write(response.content)
