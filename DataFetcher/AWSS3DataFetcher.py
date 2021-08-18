import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re
import boto3



class AWSS3DataFetcher(DataFetcherBase):
    def __init__(self, cookie, bucket, run_feq="1h",enable=True):
        self.bucket = bucket
        self.s3_client = boto3.client('s3')
        super(AWSS3DataFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        pass
    
    def get_data(self, path, subfix=""):
        content = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=path, MaxKeys=50)
        rs = []
        for item in content['Contents']:
            if item['Size'] == 0:
                continue
            if subfix != "" and subfix not in item['Key']:
                continue
            rs.append(item)
        return rs
     
    def health_check(self):
        content = self.s3_client.list_objects_v2(Bucket=self.bucket, MaxKeys=10)
        if len(content['Contents']) == 0:
            return False
        return True


