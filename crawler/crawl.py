'''
Created on Mar 18, 2014

@author: hmuriel
'''
from crawler import PATH
from crawler.functions import readFeed
from datetime import datetime
import sqlite3
import os

class Feed:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
    # Base URL
    base_url = 'http://www.youtube.com'
    # JS code to retrieve countries from the youtube homepage:
    # a = []
    # $x('//div[@class="yt-picker-section"]//a[@class="yt-picker-item"]/@href').forEach(function(e){a.push(e.value.substring(27, 29));})
    countries = ["US", "DZ", "AR", "AU", "AT", "BH", "BE", "BA", "BG", "CA", "CL", "CO", "HR", "CZ", "DK", "EG", "EE", "FI", "FR", "DE", "GH", "GR", "HK", "HU", "IN", "ID", "IE", "IL", "IT", "JP", "JO", "KE", "KW", "LV", "LT", "MK", "MY", "MX", "ME", "MA", "NL", "NZ", "NG", "NO", "OM", "PE", "PH", "PL", "PT", "QA", "RO", "RU", "SA", "SN", "RS", "SG", "SK", "SI", "ZA", "KR", "ES", "SE", "CH", "TW", "TN", "TR", "UG", "UA", "AE", "GB", "YE"]
    
    def getFeedsByCountry(self, urlvars={'gl':'CH', 'persist_gl':1}):
        feeds = []
        for feed in readFeed(self.base_url, urlvars, self.headers):
            feeds.append(feed)
        return feeds
    
    def updateFeeds(self):
        conn = sqlite3.connect(os.path.dirname(PATH) + '/homepage-feeds.db')
        c = conn.cursor()
        # for simplicity use the same timestamp.
        timestamp = datetime.now().isoformat()
        # Process the feeds by country
        for country in self.countries:
            feeds = self.getFeedsByCountry({'gl':country, 'persist_gl':1})
            try:
                for feed in feeds:
                    for v in feed['videos']:
                        c.execute("INSERT INTO feed VALUES (?, ?, ?, ?)", (country, feed['href'], timestamp, v))
                conn.commit()
            except sqlite3.Error as e:
                print(e)
        c.close()
        conn.close()
if __name__ == '__main__':
    #print(Feed().getFeedsByCountry())
    Feed().updateFeeds()