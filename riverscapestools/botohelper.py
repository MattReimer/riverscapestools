import sys
import threading
import os
import boto3
from boto3.s3.transfer import TransferConfig, S3Transfer
import botocore
import math
import binascii
from loghelper import Logger
import hashlib
from progressbar import ProgressBar

# Max size in bytes before uploading in parts.
# Specifying this is important as it affects
# How the MD5 and Etag is calculated
AWS_UPLOAD_MAX_SIZE = 20 * 1024 * 1024
# Size of parts when uploading in parts
AWS_UPLOAD_PART_SIZE = 6 * 1024 * 1024

# Get the service client
s3 = boto3.client('s3')
S3Config = boto3.s3.transfer.TransferConfig(
    multipart_threshold=AWS_UPLOAD_MAX_SIZE,
    max_concurrency=10,
    num_download_attempts=10,
    multipart_chunksize=AWS_UPLOAD_PART_SIZE,
    max_io_queue=10000
)

def s3BuildOps(conf):
    """
    Compare a source folder with what's already in S3
    :param src_files:
    :param keyprefix:
    :param bucket:
    :return:
    """
    opstore = {}
    prefix = "{0}/".format(conf['keyprefix']).replace("//", "/")
    response = s3.list_objects(Bucket=conf['bucket'], Prefix=prefix)

    # Get all the files we have locally
    files = localProductWalker(conf['localroot'])

    # Fill in any files we find on the remote
    if 'Contents' in response:
        for result in response['Contents']:
            dstkey = result['Key'].replace(prefix, '')
            if dstkey in files:
                files[dstkey]['dst'] = result
            else:
                files[dstkey] = { 'dst': result }

    for relname in files:
        fileobj = files[relname]
        opstore[relname] = S3Operation(relname, fileobj, conf)

    return opstore


def s3issame(filepath, dst):
    """
    :param bucket: S3 bucket name
    :param key: S3 key (minus the s3://bucketname)
    :param filepath: Absolute local filepath
    :return: Boolean
    """
    etag = None
    same = False
    try:
        etag = dst['ETag'][1:-1]
    except botocore.exceptions.ClientError as e:
        pass

    if etag is None:
        same = False
    else:
        # check MD5
        md5 = md5sum(filepath)
        same = True if etag == md5 else False
    return same


def localProductWalker(projroot, currentdir="", filearr={}):
    """
    This method has a similar recursive structure to s3FolderUpload
    but we're keeping it separate since it is only used to visualize
    the files in this folder
    :param rootDir:
    :param first:
    :return:
    """
    log = Logger('localProdWalk')
    for pathseg in os.listdir(os.path.join(projroot, currentdir)):
        spaces = len(currentdir) * ' ' + '/'
        relpath = os.path.join(currentdir, pathseg)
        abspath = os.path.join(projroot, relpath)
        if os.path.isfile(abspath):
            log.debug(spaces + relpath)
            filearr[relpath] = { 'src': abspath }
        elif os.path.isdir(abspath):
            log.debug(spaces + pathseg + '/')
            localProductWalker(projroot, relpath, filearr)
    return filearr


def s3ProductWalker(bucket, patharr, currpath=[], currlevel=0):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    log = Logger('ProductWalk')
    if currlevel >= len(patharr):
        return

    # If it's a collection then we need to iterate over folders and recurse on each
    if patharr[currlevel]['type'] == 'collection':
        # list everything at this collection
        pref = "/".join(currpath)+"/" if len(currpath) > 0 else ""
        result = s3.list_objects(Bucket=bucket, Prefix=pref, Delimiter='/')
        if 'CommonPrefixes' in result:
            for o in result.get('CommonPrefixes'):
                s3ProductWalker(bucket, patharr, o.get('Prefix')[:-1].split('/'), currlevel + 1)
        else:
            return

    # If it's a container then no iteration necessary. Just append the path and recurse
    elif patharr[currlevel]['type'] == 'group':
        currpath.append(patharr[currlevel]['folder'])
        s3ProductWalker(bucket, patharr, currpath, currlevel + 1)

    # If it's a project then get the XML file and print it
    elif patharr[currlevel]['type'] == 'product':
        currpath.append(patharr[currlevel]['folder'])
        result = s3.list_objects(Bucket=bucket, Prefix="/".join(currpath)+"/", Delimiter='/')
        if 'Contents' in result:
            for c in result['Contents']:
                if os.path.splitext(c['Key'])[1] == '.xml':
                    log.info('Project: {0} (Modified: {1})'.format(c['Key'], c['LastModified']))
        return


def s3FileUpload(bucket, key, filepath):
    """
    Just upload one file using Boto3
    :param bucket:
    :param key:
    :param filepath:Y
    :return:
    """
    log = Logger('S3FileUpload')

    log.info("Uploading: {0} ==> s3://{1}/{2}".format(filepath, bucket, key))
    # This step prints straight to stdout and does not log
    s3.upload_file(filepath, bucket, key, Config=S3Config, Callback=ProgressPercentage(filepath))
    print ""
    log.info("Upload Completed: {0}".format(filepath))


class S3Operation:
    """
    A Simple class for storing src/dst file information and the operation we need to perform
    """
    class FileOps:
        DELETE_REMOTE = "Delete Remote"
        DELETE_LOCAL = "Delete Local"
        UPLOAD = "Upload"
        DOWNLOAD = "Download"
        IGNORE = "Ignore"

    class Direction:
        UP = "up"
        DOWN = "down"

    class FileState:
        LOCALONLY = "Local-Only"
        REMOTEONLY = "Remote-Only"
        UPDATENEEDED = "Update Needed"
        SAME = "Files Match"

    def __init__(self, key, fileobj, conf):
        """
        :param src: relative src key
        :param dst: relative dst key
        """
        self.log = Logger('S3Ops')
        self.key = key

        # Set some sensible defaults
        self.filestate = self.FileState.SAME
        self.op = self.FileOps.IGNORE

        self.force = conf['force']
        self.localroot = conf['localroot']
        self.bucket = conf['bucket']
        self.direction = conf['direction']
        self.keyprefix = conf['keyprefix']

        # Figure out what we have
        if 'src' in fileobj and 'dst' not in fileobj:
            self.filestate = self.FileState.LOCALONLY
        if 'src' not in fileobj and 'dst' in fileobj:
            self.filestate = self.FileState.REMOTEONLY
        if 'src' in fileobj and 'dst' in fileobj:
            if s3issame(fileobj['src'], fileobj['dst']):
                self.filestate = self.FileState.SAME
            else:
                self.filestate = self.FileState.UPDATENEEDED

        # The Upload Case
        if self.direction == self.Direction.UP:
            # Two cases for uploading the file: New file or different file
            if self.filestate == self.FileState.LOCALONLY or self.filestate == self.FileState.UPDATENEEDED:
                self.op = self.FileOps.UPLOAD
            elif self.FileState.SAME and self.force:
                self.op = self.FileOps.UPLOAD
            # If the remote is there but the local is not and we're uploading then clean up the remote
            elif self.filestate == self.FileState.REMOTEONLY:
                self.op = self.FileOps.DELETE_REMOTE

        # The Download Case
        elif self.direction == self.Direction.DOWN:
            if self.filestate == self.FileState.REMOTEONLY or self.filestate == self.FileState.UPDATENEEDED:
                self.op = self.FileOps.DOWNLOAD
            elif self.FileState.SAME and self.force:
                self.op = self.FileOps.DOWNLOAD
            elif self.filestate == self.FileState.LOCALONLY:
                self.op = self.FileOps.DELETE_LOCAL
        self.log.info(str(self))

    def getS3Key(self):
        # Not using path.join because can't be guaranteed a unix system
        return "{1}/{2}".format(self.bucket, self.keyprefix, self.key)

    def getAbsLocalPath(self):
        # Not using path.join because can't be guaranteed a unix system
        return os.path.join(self.localroot, self.key)

    def execute(self):
        remotekey = self.getS3Key()
        localpath = self.getAbsLocalPath()

        if self.op == self.FileOps.IGNORE:
            self.log.info(" [{0}] {1}: Nothing to do. Continuing.".format(self.op, self.key))
        elif self.op == self.FileOps.UPLOAD:
            s3FileUpload(self.bucket, remotekey, localpath)
        elif self.op == self.FileOps.DOWNLOAD:
            self.log.info("   Downloading file.")
        elif self.op == self.FileOps.DELETE_LOCAL:
            self.log.info("   Deleting local file.")
        elif self.op == self.FileOps.DELETE_REMOTE:
            self.log.info("   Deleting remote file.")

    def __repr__(self):
        forcestr = "(FORCE)" if self.force else ""
        opstr = "{0:10s} ={2}=> {1:10s}".format(self.filestate, self.op, forcestr)
        return "[{0:16s}] ./{1} ".format(opstr.strip(), self.key)


#
# Function : md5sum
# Purpose : Get the md5 hash of a file stored in S3
# Returns : Returns the md5 hash that will match the ETag in S3
def md5sum(sourcePath):

    filesize = os.path.getsize(sourcePath)
    hash = hashlib.md5()

    if filesize > AWS_UPLOAD_MAX_SIZE:

        block_count = 0
        md5string = ""
        with open(sourcePath, "r+b") as f:
            for block in iter(lambda: f.read(AWS_UPLOAD_PART_SIZE), ""):
                hash = hashlib.md5()
                hash.update(block)
                md5string = md5string + binascii.unhexlify(hash.hexdigest())
                block_count += 1

        hash = hashlib.md5()
        hash.update(md5string)
        return hash.hexdigest() + "-" + str(block_count)

    else:
        with open(sourcePath, "r+b") as f:
            for block in iter(lambda: f.read(AWS_UPLOAD_PART_SIZE), ""):
                hash.update(block)
        return hash.hexdigest()


# Shortcut to MD5
# def get_md5(filename):
#   f = open(filename, 'rb')
#   m = hashlib.md5()
#   while True:
#     data = f.read(10240)
#     if len(data) == 0:
#         break
#     m.update(data)
#   return m.hexdigest()


class ProgressPercentage(object):
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

def getSize(filename):
    st = os.stat(filename)
    return st.st_size
