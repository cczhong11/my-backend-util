import requests

from .DataReaderBase import DataReaderBase
import json
import re
import os


class PersonalBackendReader(DataReaderBase):
    def __init__(self, domain):
        self.domain = domain
        super(PersonalBackendReader, self).__init__()

    def get_list(self, folder):
        rs = requests.get(f"{self.domain}/file?list={folder}")
        return json.loads(rs.text)

    def get_data(self, folder, file_name):
        rs = requests.get(f"{self.domain}/json?name={file_name}.json&list={folder}")
        return json.loads(rs.text)

    def health_check(self):
        return True
