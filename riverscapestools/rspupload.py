import argparse
import sys
from os import path
from userinput import query_yes_no
from botohelper import s3BuildOps, S3Operation
from loghelper import Logger
from program import Program
from project import Project

def rspupload(args):
    """
    :param inputRas:
    :param maskRas:
    :return:
    """
    log = Logger('Program')
    direction = S3Operation.Direction.UP

    program = Program(args.program)
    projectroot = path.dirname(path.abspath(args.project.name))

    projectObj = Project(args.project, projectroot)

    log.title('STARTING PYTHON UPLOADER', "=")

    keyprefix = projectObj.getPath(program)

    log.title('The following operations are queued:')
    log.info('From: {0}'.format(projectroot))
    log.info('To  : s3://{0}/{1}\n'.format(program.Bucket, keyprefix))

    conf = {
        "force": args.force,
        "direction": direction,
        "localroot": projectroot,
        "keyprefix": keyprefix,
        "bucket": program.Bucket
    }

    s3ops = s3BuildOps(conf)

    result = query_yes_no("ARE YOU SURE?")
    # result = True

    if result:
        for key in s3ops:
            s3ops[key].execute()
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
    parser.add_argument('--force',
                        help = 'Force overwriting of online files.',
                        action='store_true',
                        default=False)
    parser.add_argument('--verbose',
                        help = 'Get more information in your logs.',
                        action='store_true',
                        default=False)
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
