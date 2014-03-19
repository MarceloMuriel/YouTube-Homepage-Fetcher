'''
Created on Mar 19, 2014

@author: hmuriel
'''
from crawler.crawl import Feed
import os

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    print('path set to', os.getcwd())
    Feed().updateFeeds()