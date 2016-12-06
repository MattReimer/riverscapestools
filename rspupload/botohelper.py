import sys
import threading
import os
import boto3
import botocore
import math
import logging
from loghelper import logprint
import hashlib
from progressbar import ProgressBar

# Get the service client
s3 = boto3.client('s3')

class ProgressPercentage(object):
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

def getSize(filename):
    st = os.stat(filename)
    return st.st_size

def treeprint(rootDir, first=True):
    """
    This method has a similar recursive structure to s3FolderUpload
    but we're keeping it separate since it is only used to visualize
    the files in this folder
    :param rootDir:
    :param first:
    :return:
    """
    if first:
        logprint(rootDir + '/')
    currentdir = rootDir
    for lists in os.listdir(rootDir):
        spaces = len(currentdir) * ' ' + '/'
        path = os.path.join(rootDir, lists)
        if os.path.isfile(path):
            logprint(spaces + lists)
        elif os.path.isdir(path):
            logprint(spaces + lists + '/')
            treeprint(path, False)


def s3ProductWalker(bucket, patharr, currpath=[], currlevel=0):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    if currlevel >= len(patharr):
        return

    # If it's a level then we need to iterate over folders and recurse on each
    if 'Level' in patharr[currlevel]:
        # list everything at this level
        pref = "/".join(currpath)+"/" if len(currpath) > 0 else ""
        result = s3.list_objects(Bucket=bucket, Prefix=pref, Delimiter='/')
        if 'CommonPrefixes' in result:
            for o in result.get('CommonPrefixes'):
                s3ProductWalker(bucket, patharr, o.get('Prefix')[:-1].split('/'), currlevel + 1)
        else:
            return

    # If it's a container then no iteration necessary. Just append the path and recurse
    elif 'Container' in patharr[currlevel]:
        currpath.append(patharr[currlevel]['Container'])
        s3ProductWalker(bucket, patharr, currpath, currlevel + 1)

    # If it's a project then get the XML file and print it
    elif 'Project' in patharr[currlevel]:
        currpath.append(patharr[currlevel]['Project'])
        result = s3.list_objects(Bucket=bucket, Prefix="/".join(currpath)+"/", Delimiter='/')
        if 'Contents' in result:
            for c in result['Contents']:
                if os.path.splitext(c['Key'])[1] == '.xml':
                    logprint('Project: {0} (Modified: {1})'.format(c['Key'], c['LastModified']))
        return


def s3FolderUpload(bucket, localroot, remotepath, relpath=""):
    """
    Recurse through a folder and upload all the files in it
    :param bucket: constant string. The bucket we are uploading to
    :param localroot:
    :param remotepath: variable. The path on the remote system
    :param relpath:
    :return:
    """
    # TODO: Investigate if we need to do a MD5 comparison first to speed up already-uploaded files
    for objpath in os.listdir(localroot):
        abspath = os.path.join(localroot, objpath)
        key = os.path.join(remotepath, objpath)
        if os.path.isfile(abspath):
            s3FileUpload(bucket, key, abspath)
        elif os.path.isdir(abspath):
            s3FolderUpload(bucket, abspath, key, relpath=relpath)

def s3FileUpload(bucket, key, filepath):
    """
    Just upload one file using Boto3
    :param bucket:
    :param key:
    :param filepath:
    :return:
    """
    etag = None
    upload = False
    try:
        s3HeadObj = s3.head_object(
            Bucket=bucket,
            Key=key
        )
        etag = s3HeadObj['ETag'][1:-1]
    except botocore.exceptions.ClientError as e:
        pass

    if etag is None:
        # Download object at bucket-name with key-name to tmp.txt
        upload = True
    else:
        # check MD5
        md5 = get_md5(filepath)
        if etag != md5:
            print(filepath + ": " + md5 + " != " + etag)
            upload = True

    if upload:
        logprint("Uploading: {0} ==> s3://{1}/{2}".format(filepath, bucket, key))
        s3.upload_file(filepath, bucket, key, Callback=ProgressPercentage(filepath))
        logging.info("Upload Completed: {0}".format(filepath))
        print ""
    else:
        logprint("Same. Doing nothing: {0} = s3://{1}/{2}".format(filepath, bucket, key))


# Shortcut to MD5
def get_md5(filename):
  f = open(filename, 'rb')
  m = hashlib.md5()
  while True:
    data = f.read(10240)
    if len(data) == 0:
        break
    m.update(data)
  return m.hexdigest()
