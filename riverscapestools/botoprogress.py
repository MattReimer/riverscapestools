import threading
import os
import sys
import math
from progressbar import ProgressBar

class UploadProgress(object):
    """
    A Little helper class to display the up/download percentage
    """
    def __init__(self, filename):
        self._filename = filename
        self._basename = os.path.basename(self._filename)
        self._filesize = getSize(self._filename)
        self._seen_so_far = 0
        self._lock = threading.Lock()
        custom_options = {
            'start': 0,
            'end': 100,
            'width': 40,
            'blank': '_',
            'fill': '#',
            'format': '%(progress)s%% [%(fill)s%(blank)s]'
        }
        self.p = ProgressBar(**custom_options)

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self.percentdone = math.floor(float(self._seen_so_far) / float(self._filesize) * 100)
            # p.set(self.percentdone)
            self.p.progress = self.percentdone
            sys.stdout.write(
                "\r       {0} --> {3} {1} bytes of {2} transferred".format(
                    self._basename, format(self._seen_so_far, ",d"), format(self._filesize, ",d"), str(self.p)) )
            sys.stdout.flush()

class DownloadProgress(object):
    """
    A Little helper class to display the up/download percentage
    """
    def __init__(self, filename):
        self._filename = filename
        self._basename = os.path.basename(self._filename)
        self._filesize = 0
        if os.path.isfile(self._filename):
            self._filesize = getSize(self._filename)
        self._seen_so_far = 0
        self._lock = threading.Lock()
        custom_options = {
            'start': 0,
            'end': 100,
            'width': 40,
            'blank': '_',
            'fill': '#',
            'format': '%(progress)s%% [%(fill)s%(blank)s]'
        }
        self.p = ProgressBar(**custom_options)

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            self.percentdone = 0
            if self._filesize > 0:
                self.percentdone = math.floor(float(self._seen_so_far) / float(self._filesize) * 100)
            # p.set(self.percentdone)
            self.p.progress = self.percentdone
            sys.stdout.write(
                "\r       {0} --> {3} {1} bytes of {2} transferred".format(
                    self._basename, format(self._seen_so_far, ",d"), format(self._filesize, ",d"), str(self.p)) )
            sys.stdout.flush()

def getSize(filename):
    st = os.stat(filename)
    return st.st_size