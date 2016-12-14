import os
from riverscapestools import Logger
from comparison import s3issame
from transfers import Transfer

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
        self.s3 = Transfer(conf['bucket'])
        self.key = key

        # Set some sensible defaults
        self.filestate = self.FileState.SAME
        self.op = self.FileOps.IGNORE

        self.force = conf['force']
        self.localroot = conf['localroot']
        self.bucket = conf['bucket']
        self.direction = conf['direction']
        self.keyprefix = conf['keyprefix']

        # And the final paths we use:
        self.abspath = self.getAbsLocalPath()
        self.fullkey = self.getS3Key()

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

        if self.op == self.FileOps.IGNORE:
            self.log.info(" [{0}] {1}: Nothing to do. Continuing.".format(self.op, self.key))

        elif self.op == self.FileOps.UPLOAD:
            self.upload()

        elif self.op == self.FileOps.DOWNLOAD:
            dirpath = os.path.dirname(self.abspath)
            if not os.path.exists(dirpath):
                try:
                    os.makedirs(dirpath)
                except Exception as e:
                    raise Exception("ERROR: Directory `{0}` could not be created.".format(dirpath))
            self.download()

        elif self.op == self.FileOps.DELETE_LOCAL:
            self.delete_local()

        elif self.op == self.FileOps.DELETE_REMOTE:
            self.delete_remote()

    def __repr__(self):
        forcestr = "(FORCE)" if self.force else ""
        opstr = "{0:10s} ={2}=> {1:10s}".format(self.filestate, self.op, forcestr)
        return "[{0:16s}] ./{1} ".format(opstr.strip(), self.key)


    def delete_remote(self):
        log = Logger('S3FileDelete')

        log.info("Deleting: {0} ==> ".format(self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.delete(self.fullkey)
        log.info("S3 Deletion Completed: {0}".format(self.fullkey))

    def delete_local(self):
        dir = os.path.dirname(self.abspath)
        os.remove(self.abspath)
        # now walk backwards and clean up empty folders
        try:
            os.removedirs(dir)
        except:
            pass

    def download(self):
        """
        Just upload one file using Boto3
        :param bucket:
        :param key:
        :param filepath:
        :return:
        """
        log = Logger('S3FileDownload')

        log.info("Downloading: {0} ==> ".format(self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.download(self.fullkey, self.abspath)
        print ""
        log.info("Download Completed: {0}".format(self.abspath))

    def upload(self):
        """
        Just upload one file using Boto3
        :param bucket:
        :param key:
        :param filepath:
        :return:
        """
        log = Logger('S3FileUpload')

        log.info("Uploading: {0} ==> s3://{1}/{2}".format(self.abspath, self.bucket, self.fullkey))
        # This step prints straight to stdout and does not log
        self.s3.upload(self.abspath, self.fullkey)
        print ""
        log.info("Upload Completed: {0}".format(self.abspath))



