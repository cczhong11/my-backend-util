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

PATH = "/Volumes/My Book/photo backup/照片整理"

possible_path = [
    # "/Volumes/photo/iphonese/三星",
    # "/Volumes/photo/iphonese/相机胶卷",
    # "/Volumes/My Book/photo backup/iphonexs"
    # "/Volumes/My Book/iphone12/AnyTrans-Export-2023-09-17/My Photos",
    "/Volumes/TOSHIBA EXT/photo/"
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
    dw = DiskDataWriter(PATH, False, False)
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
