class DataFetcherBase(object):
    def __init__(self, cookie, run_feq="1h", enable=True):
        self.enable = enable
        self.run_feq = run_feq
        self.cookie = cookie
        self.load_cookie()
    
    def load_cookie(self):
        pass
    
    def get_data(self, url):
        return {}

    def health_check(self):
        pass