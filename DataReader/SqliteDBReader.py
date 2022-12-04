import requests

from .DataReaderBase import DataReaderBase
from sqlite_util import select_database
import re
import os


class SqliteDBReader(DataReaderBase):
    def __init__(self, sqlite_db_path):

        self.sqlite_db_path = sqlite_db_path
        super(SqliteDBReader, self).__init__()

    def get_data(self, sql):
        rs = select_database(self.sqlite_db_path, sql)
        return rs

    def health_check(self):
        if not os.path.exists(self.sqlite_db_path):
            return False
        return True
