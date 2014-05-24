'''
Created on Mar 18, 2014

@author: hmuriel
'''
from crawler import PATH
from crawler.functions import readFeed, readURL, readVideoMeta
from datetime import datetime
import sqlite3
import os
import sys
import json

class Feed:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
    # Base URL
    base_url = 'http://www.youtube.com'
    yt3_api = 'https://www.googleapis.com/youtube/v3/videos'
    yt2_api = 'https://gdata.youtube.com/feeds/api/videos'
    yt2_alt = 'jsonc'
    yt2_strict = 'true'
    yt2_version = 2
    
    # JS code to retrieve countries from the youtube homepage:
    # a = []
    # $x('//div[@class="yt-picker-section"]//a[@class="yt-picker-item"]/@href').forEach(function(e){a.push(e.value.substring(27, 29));})
    countries = ["US", "DZ", "AR", "AU", "AT", "BH", "BE", "BA", "BG", "CA", "CL", "CO", "HR", "CZ", "DK", "EG", "EE", "FI", "FR", "DE", "GH", "GR", "HK", "HU", "IN", "ID", "IE", "IL", "IT", "JP", "JO", "KE", "KW", "LV", "LT", "MK", "MY", "MX", "ME", "MA", "NL", "NZ", "NG", "NO", "OM", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "KR", "ES", "SE", "CH", "TW", "TN", "TR", "UG", "UA", "AE", "GB", "YE"]
    
    def getFeedsByCountry(self, urlvars={'gl':'CH', 'persist_gl':1}):
        feeds = []
        for feed in readFeed(self.base_url, urlvars, self.headers):
            feeds.append(feed)
        return feeds
    
    def updateFeeds(self, api_key = None):
        if not api_key: 
            print('no API key provided..')
            return
        vids = []
        conn = sqlite3.connect(os.path.dirname(PATH) + '/homepage-feeds.db')
        c = conn.cursor()
        # for simplicity use the same timestamp.
        timestamp = datetime.now().isoformat()
        print(timestamp)
        # Process the feeds by country
        c_country = 0
        for country in self.countries:
            feeds = self.getFeedsByCountry({'gl':country, 'persist_gl':1})
            try:
                for feed in feeds:
                    for v in feed['videos']:
                        c.execute("INSERT INTO feed VALUES (?, ?, ?, ?)", (country, feed['href'], timestamp, v))
                        if not c.execute("SELECT vid FROM video_meta WHERE vid='{0}' AND timestamp='{1}'".format(v, timestamp)).fetchone():
                            v_meta = self.getVideoMeta(api_key, v)
                            if v_meta:
                                stats = v_meta['statistics']
                                # Default the rating to 0 and update later on.
                                c.execute("INSERT INTO video_meta VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (timestamp, v_meta['id'], stats['viewCount'], stats['likeCount'], stats['dislikeCount'], stats['favoriteCount'], stats['commentCount'], 0, 0))
                                vids.append(v)
                        conn.commit()
            except sqlite3.Error as e:
                print(e)
            c_country += 1
            if c_country % 10 == 0: print('{0} % countries processed.', c_country / len(self.countries) * 100)
        c.close()
        conn.close()
        self.updateRating(vids, timestamp)
    
    def getVideoMeta(self, api_key = None, vid = None):
        fields = 'items(id,statistics)'
        data_v3 = None
        data = readVideoMeta(self.yt3_api, {'id': vid, 'key': api_key, 'part': 'statistics', 'fields': fields}, self.headers)
        if data: data_v3 = data['items'].pop()
        return data_v3
    
    def getVideoMetaV2(self, vid = None, sleep = True):
        data_v2 = readVideoMeta(self.yt2_api + '/' + vid, {'v': self.yt2_version, 'alt': self.yt2_alt, 'strict': self.yt2_strict}, self.headers, sleep)
        return data_v2
    
    def updateRating(self, vids, timestamp):
        print('Updating the rating of {0} videos'.format(len(vids)))
        v_failed = []
        conn = sqlite3.connect(os.path.dirname(PATH) + '/homepage-feeds.db')
        c = conn.cursor()
        for v in vids:
            data = self.getVideoMetaV2(v)
            if data:
                try:
                    c.execute("UPDATE video_meta SET rating='{0}', ratings='{1}' WHERE timestamp='{2}' AND vid='{3}'".format(data['rating'] if 'rating' in data else 0, data['ratingCount'] if 'ratingCount' in data else 0, timestamp, v))
                    conn.commit()
                except sqlite3.Error as e:
                    print(e)
            else:
                v_failed.append(v)
        c.close()
        conn.close()
        if v_failed:
            print('FAILED to retrieve meta for {0} videos ({1})'.format(len(v_failed), len(v_failed) / len(vids) * 100))
            print('trying again')
            self.updateRating(v_failed, timestamp)

if __name__ == '__main__':
    #print(Feed().getFeedsByCountry())
    Feed().updateFeeds(sys.argv[1])
    #print(Feed().videoMeta(sys.argv[1], 'jZN7OSEG0ZE'))
    