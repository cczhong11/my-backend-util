from typing import List
import requests
from bs4 import BeautifulSoup
from .DataReaderBase import DataReaderBase
from web_util import parse_curl
import re
import dropbox


class DropboxReader(DataReaderBase):
    def __init__(self, access_token):
        self.client = dropbox.Dropbox(access_token)
        super(DropboxReader, self).__init__()

    def get_data(self, path, subfix: List[str]):
        return self.get_files(path, subfix)

    def health_check(self):
        return True

    def get_files(self, folder, subfix: List[str]):
        result = self.client.files_list_folder(folder, recursive=True)

        folders = []

        def process_dirs(entries):
            for entry in entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    file_subfix = entry.name.split(".")[-1]
                    if file_subfix in subfix:
                        folders.append((entry.name, entry.path_lower))

        process_dirs(result.entries)

        while result.has_more:
            result = self.client.files_list_folder_continue(result.cursor)
            process_dirs(result.entries)

        return folders

    def download(self, file_path, file_name):
        self.client.files_download_to_file(file_name, file_path)
