from DataWriter.DataWriterBase import DataWriterBase
import os
from pathlib import Path
import re

home = str(Path.home())


class MarkdownImgDownloader(DataWriterBase):
    def __init__(self, md_path: str, download_dir: str):
        self.md_path = md_path
        self.download_dir = download_dir
        self.downloaded = os.path.join(download_dir, "downloaded.txt")

    def download_path(self):
        downloaded = set()
        if os.path.exists(self.downloaded):
            with open(self.downloaded) as f:
                for l in f:
                    downloaded.add(l.strip())

        with open(self.md_path) as f:
            with open(self.downloaded, "a") as ff:
                for l in f:
                    rs = re.findall("!\[\]\((.*)\)", l)
                    if len(rs) > 0:
                        if "http" in rs[0]:
                            url = rs[0]
                            filehash = url.split("/")[-1]
                            if filehash in downloaded:
                                continue
                            os.system(f'wget "{url}" -P {self.download_dir} -bq')

                            ff.write(filehash + "\n")

    def write_data(self):
        self.download_path()

    def health_check(self) -> bool:
        if os.path.exists(self.md_path):
            return False
        return True
