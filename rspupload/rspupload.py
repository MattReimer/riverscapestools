import urllib2
import argparse
import sys
import re
import time
import boto3
import xml.etree.ElementTree as ET
from os import path
from userinput import query_yes_no
from botohelper import s3FolderUpload, treeprint
from loghelper import Logger
from program import Program
from project import Project

__version__ = "0.0.1"
# Initialize logger.
s3 = boto3.client('s3')

def rspupload(args):
    """
    :param inputRas:
    :param maskRas:
    :return:
    """
    log = Logger('Program')
    projectET = None
    if re.match('^https*:\/\/.*', args.program) is not None:
        try:
            request = urllib2.Request(args.program)
            request.add_header('Pragma', 'no-cache')
            file = urllib2.build_opener().open(request)
            data = file.read()
            file.close()
            programET = ET.fromstring(data)
        except:
            err = "ERROR: Could not download <{0}>".format(args.program)
            log.error(err)
            raise ValueError(err)
    else:
        programET = ET.parse(args.program).getroot()

    programObj = Program(programET)

    projectRoot = path.dirname(path.abspath(args.project.name))
    projectET = ET.parse(args.project).getroot()
    projectObj = Project(projectET, projectRoot)

    log.title('STARTING PYTHON UPLOADER', "=")

    remotePath = projectObj.getPath(programObj)

    log.title('The following files will be uploaded:')
    treeprint(projectRoot)

    log.info("\nThese files will be uploaded to: s3://{0}/{1}\n".format(programObj.Bucket, remotePath))
    time.sleep(0.25)
    result = query_yes_no("ARE YOU SURE?")

    if result:
        s3FolderUpload(programObj.Bucket, projectObj.LocalRoot, remotePath)
    else:
        log.info("\n<EXITING> No sync performed\n")



def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('project',
                        help='Path to the project XML file.',
                        type=argparse.FileType('r'))
    parser.add_argument('--program',
                        default='https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml',
                        help='Path or url to the Program XML file (optional)')
    parser.add_argument('--logfile',
                        default='',
                        help='Write the results of the operation to a specified logfile (optional)')
    parser.add_argument('--verbose',
                        help = 'Get more information in your logs.',
                        action='store_true',
                        default=False )
    args = parser.parse_args()

    log = Logger("Program")
    if len(args.logfile) > 0:
        log.setup(logfile=args.logfile,
                  verbose=args.verbose)

    try:
        rspupload(args)
    except AssertionError as e:
        log.error("Assertion Error", e)
        sys.exit(0)
    except Exception as e:
        log.error('Unexpected error: {0}'.format(sys.exc_info()[0]), e)
        raise
        sys.exit(0)


"""
This handles the argument parsing and calls our main function
If we're not calling this from the command line then
"""
if __name__ == '__main__':
    main()
