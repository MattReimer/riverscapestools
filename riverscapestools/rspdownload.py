import argparse
from settings import defaults, getDataDir
from os import path
from userinput import *
from s3.operations import S3Operation
from s3.walkers import s3BuildOps, menuwalk
from program import Program
from logger import Logger

def rspdownload(args):
    datadir = getDataDir(args)
    log = Logger('Program')
    direction = S3Operation.Direction.DOWN
    program = Program(args.program)

    log.title('STARTING PYTHON DOWNLOADER', "=")

    downloadPath = menuwalk(program)
    assert downloadPath, "No Product chosen. Exiting"

    keyprefix = '/'.join(downloadPath)
    conf = {
        "delete": args.delete,
        "force": args.force,
        "direction": direction,
        "localroot": path.join(datadir, keyprefix),
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


def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir',
                        help='Local path to the root of the program on your local drive. You can omit this argument if you have `{0}` set as an environment variable.'.format(defaults.DataENVName))
    parser.add_argument('--program',
                        default=defaults.ProgramXML,
                        help='Path or url to the Program XML file (optional)')
    parser.add_argument('--logfile',
                        default='',
                        help='Write the results of the operation to a specified logfile (optional)')
    parser.add_argument('--delete',
                        help = 'Local files that are not on S3 will be deleted (Default: False).',
                        action='store_true',
                        default=False)
    parser.add_argument('--force',
                        help = 'Force a download, even if files are the same (disabled by default)',
                        action='store_true',
                        default=False)
    parser.add_argument('--verbose',
                        help = 'Get more information in your logs.',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    log = Logger("Program")
    log.setup(args)

    try:
        rspdownload(args)
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



