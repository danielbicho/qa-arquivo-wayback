import argparse
import hashlib
import os

import requests

parser = argparse.ArgumentParser()
parser.add_argument('--har', dest='har_render_endpoint', default='http://localhost:9000/har',
                      help='Specify HAR Render Endpoint. (Default: http://localhost:9000/har)')
parser.add_argument('--screenshot', dest='screenshot_render_endpoint', default='http://localhost:9000/screenshot',
                      help='Specify Screenshot Render Endpoint. (Default: http://localhost:9000/screenshot)')
parser.add_argument('--url_list', dest='url_list', default='testfiles/test_urls_list.txt', help='Specify path to list with URLs to test.')

args = parser.parse_args()

with open(args.url_list, mode='r') as input_file:
    for url in input_file.readlines():
        url = url.strip()
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        print("Generating {}.har file for: {}".format(url_hash, url))
        response = requests.get(url="{}?url={}".format(args.har_render_endpoint, url))
        with open(os.path.join('testfiles/hars', "{}.har".format(url_hash)), mode='wb') as output_file:
            output_file.write(response.content)

        print("Generating {}.screenshot file for: {}".format(url_hash, url))
        response = requests.get(url="{}?url={}".format(args.screenshot_render_endpoint, url))
        with open(os.path.join('testfiles/screenshots', "{}.screenshot".format(url_hash)), mode='wb') as output_file:
            output_file.write(response.content)