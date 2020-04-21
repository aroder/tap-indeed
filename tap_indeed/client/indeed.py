import datetime
import itertools
import re
import urllib.parse

import backoff
from bs4 import BeautifulSoup
import requests
import singer

batch_ts = datetime.datetime.now()
pattern = re.compile('Page \d+ of (\d+) jobs')
URL_TEMPLATE = "https://www.indeed.com/jobs?as_and=&as_phr=&as_any=&as_not=&as_ttl={QUERY}&as_cmp=&jt=all&st=&as_src=&salary=&radius=25&l={LOCATION}&fromage=any&limit=10&sort=date&psf=advsrch&from=advancedsearch"

def record(query, location):
    return {
        'query': query,
        'location': location,
        'openings_count': None
    }


class IndeedClient(object):
    def __init__(self, locations, queries):
        self.locations = locations
        self.queries = queries
        self.records = [record(location, query) for (query, location) in itertools.product(locations, queries)]

    def extract(self):
        for rec in self.records:
            r = self.request(URL_TEMPLATE.format(QUERY=urllib.parse.quote(rec['query']), LOCATION=urllib.parse.quote(rec['location'])))
            soup = BeautifulSoup(r.text, 'html.parser')
            t = soup.select("div#searchCountPages")

            match = pattern.search(t[0].contents[0])
            if match is not None:
                rec['openings_count'] = int(match.group(1))
            
            yield rec

    @singer.utils.ratelimit(3, 1)
    def request(self, url):
        return requests.get(url)