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
PATH = "/Users/tianchenzhong/Dropbox/生活/food"


def move_volume(volume):

    fd = FileDataReader(volume)
    dw = DiskDataWriter(PATH)
    if not fd.health_check() or not dw.health_check():
        print(f"{volume} is not exist or {PATH} not exist")
        return

    img_file_list = fd.get_img_list()

    for item in img_file_list:
        dw.write_data_to_date_based_folder(item["name"], "", food=True)


def move():

    if os.path.exists(PATH):

        move_volume(PATH)


if __name__ == "__main__":
    move()
