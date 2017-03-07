import argparse
import sys
from os import path
from userinput import query_yes_no
from s3.operations import S3Operation
from s3.walkers import s3BuildOps
from logger import Logger
from program import *
from settings import defaults

def rspupload(args):
    """
    :param inputRas:
    :param maskRas:
    :return:
    """
    log = Logger('Program')
    direction = S3Operation.Direction.UP

    program = Program(args.program)

    if path.isdir(args.project):
        projectroot = path.abspath(args.project)

        projectObj = Project(projectroot, program.ProjectFile)

        log.title('STARTING PYTHON UPLOADER', "=")

        keyprefix = projectObj.getPath(program)

        conf = {
            "delete": args.delete or False,
            "force": args.force or False,
            "direction": direction,
            "localroot": projectroot,
            "keyprefix": keyprefix,
            "bucket": program.Bucket
        }

        s3ops = s3BuildOps(conf)

        log.title('Please Confirm that you wish to proceed?')
        result = query_yes_no("Begin?")


        if result:
            for key in s3ops:
                s3ops[key].execute()
        else:
            log.info("\n<EXITING> No sync performed\n")
    else:
        log.error("Path specified is not a valid project folder: {}".format(args.project))

def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('project',
                        help='Path to the project folder containing the project xml file',
                        type=str)
    parser.add_argument('--program',
                        default=defaults.ProgramXML,
                        help='Path or url to the Program XML file (optional)')
    parser.add_argument('--logfile',
                        help='Write the results of the operation to a specified logfile (optional)')
    parser.add_argument('--delete',
                        help = 'Remote files that are not on local will be deleted (disabled by default)',
                        action='store_true',
                        default=False)
    parser.add_argument('--force',
                        help = 'Force a download, even if files are the same (disabled by default)',
                        action='store_true',
                        default=False)
    parser.add_argument('--verbose',
                        help = 'Get more information in your logs (optional)',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    log = Logger("Program")
    log.setup(args)

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
