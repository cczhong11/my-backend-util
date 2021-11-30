
from .DataFetcherBase import DataFetcherBase
import requests
import re
from yelpapi import YelpAPI


class DeepLDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h",enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        self.cookie = cookie
        super(DeepLDataFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        pass
        
    
    def get_data(self, text):
        search_results = requests.post("https://api.deepl.com/v2/translate",data=f"auth_key={self.cookie}&text={text}&target_lang=ZH")
        return search_results
        
     
    def health_check(self):
        result = self.get_data(text="test")
        if len(result) == 0:
            return False
        return True

