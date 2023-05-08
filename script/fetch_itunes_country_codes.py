#!/usr/bin/env python
# coding: utf-8

import json
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def fetch_iTunes_countries(list_alpha2):
    whitelist = []

    # setup session to use retries when API throttles
    s = requests.Session()
    retry_strategy = Retry(
        total=100,  # total number of retries
        backoff_factor=5,  # incremental delay after first try
        status_forcelist=[401, 402, 403, 413, 429, 500, 502, 503, 504],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    # search itunes country store
    api = "https://itunes.apple.com/search?country="
    for alpha2 in list_alpha2:
        response = s.get(api + alpha2)

        # check for valid response
        if response.status_code == 200:
            whitelist.append(alpha2)

    return whitelist


def split(alist, n):
    for i in range(0, n):
        yield alist[i::n]


def main():
    # 1. Load list of all 676 available ISO 3166-1 alpha-2 codes
    # From https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    list_alpha2 = json.load(open("script/iso3166_1_alpha2.json"))
    assert len(list_alpha2) == 676

    # 2. Split into chunks to enable parallel execution
    chunk_size = int(sys.argv[1])
    chunk_num = int(sys.argv[2])
    chunks = list(split(list_alpha2, chunk_size))
    chunk = chunks[chunk_num]

    # 3. Fetch list of all codes that return 200 OK status
    whitelist = fetch_iTunes_countries(chunk)

    # 4. Output list as str
    print(",".join(whitelist))


if __name__ == "__main__":
    main()
