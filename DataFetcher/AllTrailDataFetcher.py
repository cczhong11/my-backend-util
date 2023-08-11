import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re
import urllib
import json
from dataclasses import dataclass


@dataclass
class Hike(object):
    name: str = ""
    avg_rating: float = 0.0
    city_name: str = ""
    created_at: str = ""
    distance: float = 0.0
    duration: float = 0.0
    elevation_gain: float = 0.0
    trail_id: int = 0
    lat: float = 0.0
    lng: float = 0.0
    url: str = ""


class AllTrailDataFetcher(DataFetcherBase):
    def __init__(self, cookie, run_feq="1h", enable=True):
        self.header = {}
        self.feedList = []
        super(AllTrailDataFetcher, self).__init__(cookie, run_feq, enable)

    def load_cookie(self):
        cookie_str = ""
        with open(self.cookie) as f:
            cookie_str = f.read()
        url, header = parse_curl(cookie_str)
        self.header = header
        self.url = url

    def get_data(self, data=None):
        result = requests.post(self.url, headers=self.header).text
        try:
            result = json.loads(result)
        except:
            with open(data) as f:
                result = json.load(f)
        rs = []
        for r in result["maps"]:
            if "hiking" not in r["activities"]:
                continue
            trail = Hike()
            trail.name = r["name"]
            trail.avg_rating = r["avg_rating"]
            trail.city_name = r["city_name"]
            trail.created_at = r["created_at"]
            trail.distance = r["distance"]
            trail.duration = r["duration_minutes"]
            trail.elevation_gain = r["elevation_gain"]
            trail.trail_id = r["trail_id"]
            trail.lat = r["_geoloc"]["lat"]
            trail.lng = r["_geoloc"]["lng"]
            rs.append(trail)
        return rs

    def health_check(self):
        return True
