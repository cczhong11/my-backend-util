
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re
from yelpapi import YelpAPI


class YelpDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h",enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(YelpDataFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        self.client = YelpAPI(self.cookie)
        
    
    def get_data(self, term, location):
        search_results = self.client.search_query(term=term,location=location)
        return search_results['businesses']
        
     
    def health_check(self):
        result = self.client.search_query(term="Doppio Zero Pizza Napoletana",location="Mountain View, CA")
        if len(result) == 0:
            return False
        return True

