class DataFetcherBase(object):
    def __init__(self):
        self.load_cookie()
    
    def load_cookie(self):
        pass
    
    def get_data(self, url):
        return {}

    def health_check(self):
        pass