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


def rspdownload(args):
    print "hu"


def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('somevar',
                        help='Path to the project XML file.',
                        type=argparse.FileType('r'))
    parser.add_argument('--localroot',
                        help='Local path to the root of the program on your local drive')
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



