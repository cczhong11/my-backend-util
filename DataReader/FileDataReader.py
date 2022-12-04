from genericpath import isdir
from .DataReaderBase import DataReaderBase
import os
import web_util


class FileDataReader(DataReaderBase):
    def __init__(self, folder):
        self.folder = folder

    def get_data(self, path, sub_folder=None):
        rs = ""
        absolute_path = f"{self.folder}/{path}"
        if sub_folder is not None:
            absolute_path = f"{self.folder}/{sub_folder}/{path}"
        if not os.path.exists(absolute_path):
            return rs
        with open(absolute_path) as f:
            rs = f.read()
        return [{"name": path, "content": rs}]

    def get_list(self, sub_folder):
        rs = []
        absolute_path = f"{self.folder}/{sub_folder}"
        if not os.path.exists(absolute_path):
            return rs
        for item in os.listdir(absolute_path):
            if "9999" in item:
                continue
            if ".json" in item:
                json_obj = web_util.read_json_file(f"{absolute_path}/{item}")
                if "latlng" in json_obj:
                    rs.append({"name": item, "latlng": json_obj["latlng"]})
                    continue
            rs.append({"name": item})
        return sorted(rs, key=lambda x: x["name"])

    def get_latest_file(self, sub_folder):
        rs = self.get_list(sub_folder)
        rs = sorted(rs, key=lambda x: x["name"], reverse=True)
        return rs[0]["name"]

    def get_img_list(self, sub_folder=None, set_absolute_path=None):
        rs = []
        if sub_folder is not None:
            absolute_path = f"{self.folder}/{sub_folder}"
        else:
            absolute_path = self.folder
        # overwrite
        if set_absolute_path:
            absolute_path = set_absolute_path
        if not os.path.exists(absolute_path):
            return rs

        for item in os.listdir(absolute_path):
            if (
                ".JPG" in item
                or ".jpg" in item
                or ".png" in item
                or ".PNG" in item
                or ".CR3" in item
                or ".cr3" in item
                or ".dng" in item
                or ".DNG" in item
                or ".HEIC" in item
                or ".heic" in item
            ):
                rs.append({"name": os.path.join(absolute_path, item)})
            if os.path.isdir(absolute_path + "/" + item):
                new_rs = self.get_img_list(set_absolute_path=absolute_path + "/" + item)
                rs.extend(new_rs)
        return sorted(rs, key=lambda x: x["name"])

    def get_video_list(self, sub_folder=None, set_absolute_path=None):
        rs = []
        if sub_folder is not None:
            absolute_path = f"{self.folder}/{sub_folder}"
        else:
            absolute_path = self.folder
        # overwrite
        if set_absolute_path:
            absolute_path = set_absolute_path
        if not os.path.exists(absolute_path):
            return rs
        for item in os.listdir(absolute_path):
            if (
                ".MP4" in item
                or ".mp4" in item
                or ".mov" in item
                or ".MOV" in item
                or ".AAC" in item
                or ".SRT" in item
            ):
                rs.append({"name": os.path.join(absolute_path, item)})
            if os.path.isdir(absolute_path + "/" + item):
                new_rs = self.get_video_list(
                    set_absolute_path=absolute_path + "/" + item
                )
                rs.extend(new_rs)
        return sorted(rs, key=lambda x: x["name"])

    def health_check(self):
        if os.path.exists(self.folder):
            return True
        return False
