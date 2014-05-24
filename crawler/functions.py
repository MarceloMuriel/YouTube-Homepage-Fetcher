'''
Created on Mar 18, 2014

@author: hmuriel
'''

from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import lxml.html
import json
import time
import random

def readURL(addr, urlvars, headers):
    data = ""
    try: req = urlopen(Request("%s?%s" % (addr, urlencode(urlvars)), None, headers))
    except HTTPError as e: 
        if e.code != '403':
            print('HTTP Error: {0}. Request: {1}'.format(e.code, "%s?%s" % (addr, urlencode(urlvars))))
    except URLError as e: print('URL Error: {0}'.format(e.reason))
    else:
        data = req.read().decode(req.headers.get_content_charset())
    return data

def readFeed(full_url, urlvars, headers):
    ''' Lazy generator to read the feeds '''
    # Try to read the URL twice naively in case the server answers with a (non persistent) HTTP error.
    data = readURL(full_url, urlvars, headers) or readURL(full_url, urlvars, headers)
    if data:
        doc = lxml.html.fromstring(data)
        feed_nodes = doc.xpath('//ul/li[contains(@class, "feed")]');
        for feed_node in feed_nodes:
            feed = {#'name': (feed_node.xpath('.//h2/a/span[contains(@class, "title")]/text()') or ['']).pop(0).strip(),
                    'href': (feed_node.xpath('.//h2/a/@href') or ['']).pop(0).strip()}
            videos = []
            for video_href in feed_node.xpath('.//a[starts-with(@href, "/watch")]/@href'):
                video_id = video_href.split('?v=').pop()
                # Video might already exist, since there are multiple hrefs in the video container.
                if video_id not in videos:
                    videos.append(video_id)
            feed.update({'videos':videos})
            yield feed
    else:
        print('error reading', full_url, 'with', urlvars)

def readVideoMeta(full_url, urlvars, headers, sleep = True):
    data = readURL(full_url, urlvars, headers)
    if not data and sleep:
        time.sleep(random.randrange(1,2))
        data = readURL(full_url, urlvars, headers)
    if not data:
        return None
    return json.loads(data)

if __name__ == '__main__':
    # Test feed retrieval
    print(list(readFeed('https://www.youtube.com', {}, {})))
    