import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re
import urllib
import json
from dataclasses import dataclass

@dataclass
class Restaurant(object):
    name:str =""
    lat:float=0.0
    lng:float=0.0
    city: str=""
    url:str=""
    online_booking:bool=False
    cuisine_type:str=""
    street_address:str=""
    award:str=""
    region:str=""
    yelp_link:str =""
    yelp_rating:float = -1.0
    price:str=""

class MichelinDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h", enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(MichelinDataFetcher, self).__init__(cookie, run_feq, enable)

    def load_cookie(self):
        cookie_str = ""
        with open(self.cookie) as f:
            cookie_str = f.read()
        url, header = parse_curl(cookie_str)
        self.header = header
        self.url = url

    def get_data(self, data):

        result = requests.post(self.url, headers=self.header, data=data).text
        result = json.loads(result)
        rs = []
        for r in result["results"][0].get("hits",[]):
            restaurant = Restaurant()
            restaurant.name = r["name"]
            restaurant.award = r['michelin_award']
            restaurant.city = r["city"]['name']
            restaurant.lat = r['_geoloc']['lat']
            restaurant.lng = r['_geoloc']['lng']
            restaurant.street_address = r['_highlightResult']['street']['value']
            restaurant.cuisine_type = r['_highlightResult']['cuisine_type']['value']
            restaurant.online_booking = r['online_booking'] == 1
            restaurant.region = r['region']['name']
            restaurant.url = r['url']
            rs.append(restaurant)
        return rs

    def health_check(self):
        return True

