import os
import datetime
import click
import logging
import shutil
import sys
from DataReader.FileDataReader import FileDataReader
from DataWriter.DiskDataWriter import DiskDataWriter

logging.basicConfig()


logging.root.setLevel(logging.INFO)
# PATH = "/Volumes/BackupSSD/"  # "/Volumes/T7 Touch/orgranized photo"
PATH = "/Volumes/T7 Touch/orgranized photo"
if os.path.exists("/Volumes/BackupSSD/"):
    PATH = "/Volumes/BackupSSD/"
possible_path = [
    "/Volumes/POCKET2/DCIM/103MEDIA",
    "/Volumes/POCKET2/DCIM/101MEDIA",
    "/Volumes/POCKET2/DCIM/102MEDIA",
    "/Volumes/dji/DCIM/101MEDIA",
    "/Volumes/dji mini3/DCIM/100MEDIA",
    "/Volumes/eos rp/DCIM/100CANON",
    "/Volumes/eos rp/DCIM/102CANON",
    # "/Volumes/T7 Touch/iphone13/",
    "/Volumes/Action3/DCIM/DJI_002_A01/",
    "/Volumes/BackupSSD/iphone13/AnyTrans-Export-2023-04-22/My Photos/",
]
prefix = {
    "/Volumes/POCKET2/DCIM/": "pocket2",
    "/Volumes/dji/DCIM/": "mini2",
    "/Volumes/dji mini3/DCIM/": "mini3",
}


def move_volume(volume):
    file_prefix = ""
    for p in prefix:
        if p in volume:
            file_prefix = prefix[p]
    fd = FileDataReader(volume)
    dw = DiskDataWriter(PATH)
    if not fd.health_check() or not dw.health_check():
        print(f"{volume} is not exist or {PATH} not exist")
        return

    img_file_list = fd.get_img_list()

    video_file_list = fd.get_video_list()

    for item in img_file_list:
        dw.write_data_to_date_based_folder(item["name"], file_prefix)
    for item in video_file_list:
        dw.write_data_to_date_based_folder(item["name"], file_prefix)


def move():
    srcs = []
    for p in possible_path:
        if os.path.exists(p):
            srcs.append(p)
            break
    for src in srcs:
        move_volume(src)


if __name__ == "__main__":
    move()
