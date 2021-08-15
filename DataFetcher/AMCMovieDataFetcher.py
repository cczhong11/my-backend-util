import requests
from .DataFetcherBase import DataFetcherBase

class AMCMovieDataFetcher(DataFetcherBase):
    def __init__(self,api, enable=True):
        self.api = api
        self.headers = {"X-AMC-Vendor-Key":api}
        self.data = []
        super(AMCMovieDataFetcher, self).__init__(enable=enable)
    
    def load_cookie(self):
        pass
    
    def get_data(self, url):
        rs = {}
        movie_list = []
        for movie in self.data:
            if movie.get("genre","") == "":
                continue
            movie_list.append({"name":movie.get("name",""),"genre":movie.get("genre",""),"imdb":movie.get("imdbId",""),"url":movie.get("websiteUrl","")})
        rs['data'] = movie_list
        return rs

    def health_check(self):
        rs = requests.get("https://api.amctheatres.com/v2/movies/views/now-playing?page-size=30",headers=self.headers).json()
        self.data = rs.get("_embedded",{}).get("movies",[])
        if len(self.data) == 0:
            return False
        return True