from pathlib import Path
from DataWriter.DataWriterBase import DataWriterBase
import os
import datetime
import shutil
import exifread
from typing import Optional

file_folder = {
    "jpg": "pic",
    "JPG": "pic",
    "png": "pic",
    "CR3": "pic",
    "DNG": "pic",
    "PNG": "pic",
    "HEIC": "pic",
    "heic": "pic",
    "jpeg": "pic",
    "JPEG": "pic",
    "mp4": "video",
    "MP4": "video",
    "MOV": "video",
    "mov": "video",
    "AAC": "video",
    "SRT": "video",
    "AVI": "video",
    "avi": "video",
}


def find_img_original_time(filename: str) -> Optional[datetime.datetime]:
    with open(filename, "rb") as fh:
        try:
            tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
        except Exception as e:
            print(f"{filename} has error {e}")
            return None
        dateTaken = tags.get("EXIF DateTimeOriginal", None)
        if dateTaken:
            try:
                dateTaken = datetime.datetime.strptime(
                    dateTaken.printable[:19], "%Y:%m:%d %H:%M:%S"
                )
            except ValueError:
                try:
                    dateTaken = datetime.datetime.strptime(
                        dateTaken.printable, "%Y-%m-%d %H:%M:%S"
                    )
                except:
                    return None
        return dateTaken


class DiskDataWriter(DataWriterBase):
    def __init__(self, folder, dry_run=False, backup=False):
        super(DiskDataWriter, self).__init__()
        self.folder = folder
        self.dry_run = dry_run
        self.backup = backup

    def write_data_to_date_based_folder(
        self,
        filename,
        rename="",
        food=False,
    ):
        mt_time = find_img_original_time(filename)
        if mt_time is None:
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
        # time based folder name
        base_folder.mkdir(parents=True, exist_ok=True)
        single_file = filename.split("/")[-1]
        if len(rename) > 0:
            # moving files
            single_file = f"{rename}_{single_file}"
        if os.path.exists(os.path.join(base_folder, single_file)):
            print(f"{os.path.join(base_folder, single_file)} already exists")
            return
        if self.dry_run:
            print(f"move {filename} to {os.path.join(base_folder, single_file)}")
            return
        if self.backup:
            shutil.copy2(
                f"{filename}",
                f"{os.path.join(base_folder, single_file)}",
            )
            print(f"backup {filename} to {os.path.join(base_folder, single_file)}")
            return
        if os.path.exists(
            os.path.join(base_folder, single_file)
        ) and filename != os.path.join(base_folder, single_file):
            print(f"{os.path.join(base_folder, single_file)} already exists")
            # delete the file
            # os.remove(filename)
            return
        shutil.move(
            f"{filename}",
            f"{os.path.join(base_folder, single_file)}",
        )
        print(f"move {filename} to {os.path.join(base_folder, single_file)}")

    def health_check(self) -> bool:
        if os.path.exists(self.folder):
            return True
        return False
