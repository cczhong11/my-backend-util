from .DataReaderBase import DataReaderBase
import os
import web_util

class FileReader(DataReaderBase):
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
        return [{'name': path, 'content': rs}]
    
    def get_list(self, sub_folder):
        rs = []
        absolute_path = f"{self.folder}/{sub_folder}"
        if not os.path.exists(absolute_path):
            return rs
        for item in os.listdir(absolute_path):
            if "9999" in item:
                continue
            if "read" in sub_folder:
                rs.append({'name':item})
                continue
            json_obj = web_util.read_json_file(f"{absolute_path}/{item}")
            if "latlng" in json_obj:
                rs.append({'name': item, 'latlng': json_obj['latlng']})
            else:
                rs.append({'name': item})
        return rs
    
    def get_latest_file(self, sub_folder):
        rs = self.get_list(sub_folder)
        rs = sorted(rs, key=lambda x: x['name'],reverse=True)
        return rs[0]['name']
    
    
    def health_check(self):
        if os.path.exists(self.folder):
            return True
        return False