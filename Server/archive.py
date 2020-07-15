'''
archive.py

Description: A simple archiving handling class made for handling video frame archives
'''
from zipfile import ZipFile
from datetime import datetime
from os import path
import os


class Archive:
    file_name = None

    def __init__(self, file_name=str(abs(hash(datetime.now()))) + '.zip'):
        self.file_name = file_name
        self.name_woextension = file_name.replace('.zip', '')
        self.zip_archive = ZipFile(file_name, 'r')

    """def add(self, file_name):
        try:
            self.zip_archive.write(file_name)
        except:
            print("Unable to add %s to %s" %
                  (file_name, self.zip_archive.file_name))"""

    def extract(self):
        if not os.path.exists(self.name_woextension):
            os.mkdir(self.name_woextension)
        os.chdir(self.name_woextension)
        self.zip_archive.extractall()
        self.zip_archive.close()

    def close(self):
        """Ryan - Need this to send a valid .zip"""
        self.zip_archive.close()

    def open(self):
        """
        Ryan - May have some use for future
        (maybe only instantiate the zip once?)
        """
        self.zip_archive.open()
