import requests
from bs4 import BeautifulSoup
from .DataReaderBase import DataReaderBase
from web_util import parse_curl
import re
import boto3


class AWSS3DataReader(DataReaderBase):
    def __init__(self, bucket):
        self.bucket = bucket
        self.s3_client = boto3.client("s3")
        super(AWSS3DataReader, self).__init__()

    def get_data(self, path, subfix="", max_keys=50):
        content = self.s3_client.list_objects_v2(
            Bucket=self.bucket, Prefix=path, MaxKeys=max_keys
        )
        rs = []
        for item in content["Contents"]:
            if item["Size"] == 0:
                continue
            if subfix != "" and subfix not in item["Key"]:
                continue
            rs.append(item)
        return sorted(rs, key=lambda x: x["LastModified"])

    def health_check(self):
        content = self.s3_client.list_objects_v2(Bucket=self.bucket, MaxKeys=10)
        if len(content["Contents"]) == 0:
            return False
        return True
