from pathlib import Path
from DataWriter.DataWriterBase import DataWriterBase
import os
import datetime
import shutil

file_folder = {
    "jpg": "pic",
    "JPG": "pic",
    "png": "pic",
    "CR3": "pic",
    "DNG": "pic",
    "PNG": "pic",
    "HEIC": "pic",
    "heic": "pic",
    "mp4": "video",
    "MP4": "video",
    "MOV": "video",
    "mov": "video",
}


class DiskDataWriter(DataWriterBase):
    def __init__(self, folder, dry_run=False):
        super(DiskDataWriter, self).__init__()
        self.folder = folder
        self.dry_run = dry_run

    def write_data_to_date_based_folder(self, filename, rename="", food=False):
        stat = os.stat(filename)
        mt_time = datetime.datetime.fromtimestamp(stat.st_mtime)
        time_based_folder_name = mt_time.strftime("%Y_%m_%d")
        month_based_folder_name = mt_time.strftime("%Y_%m")
        subfix = filename.split(".")[-1]
        if subfix not in file_folder:
            print(f"{filename} is not supported")
            return

        base_folder = Path(
            f"{self.folder}/{month_based_folder_name}/{time_based_folder_name}/{file_folder[subfix]}"
        )
        if food:
            base_folder = Path(f"{self.folder}/{time_based_folder_name}/")
        base_folder.mkdir(parents=True, exist_ok=True)
        single_file = filename.split("/")[-1]
        if len(rename) > 0:
            # moving files
            single_file = f"{rename}_{single_file}"
        if os.path.exists(os.path.join(base_folder, single_file)):
            print(f"{os.path.join(base_folder, single_file)} already exists")
        if self.dry_run:
            print(f"move {filename} to {os.path.join(base_folder, single_file)}")
            return
        shutil.move(
            f"{filename}",
            f"{os.path.join(base_folder, single_file)}",
        )

    def health_check(self) -> bool:
        if os.path.exists(self.folder):
            return True
        return False
