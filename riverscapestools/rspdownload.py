import argparse
from userinput import *
from botohelper import s3BuildOps, S3Operation
from program import Program

DATA_ENV_VAR = "RSDATADIR"

def rspdownload(args):
    datadir = getDataDir(args)
    log = Logger('Program')
    direction = S3Operation.Direction.DOWN
    program = Program(args.program)

    log.title('STARTING PYTHON DOWNLOADER', "=")

    downloadPath = program.menuWalk()

    assert downloadPath, "No Product chosen. Exiting"

    log.info('Found download path: {0}'.format('/'.join(downloadPath)))
    keyprefix = '/'.join(downloadPath)
    conf = {
        "force": args.force,
        "direction": direction,
        "localroot": os.path.join(datadir, keyprefix),
        "keyprefix": keyprefix,
        "bucket": program.Bucket
    }

    log.title('The following operations are queued:')
    log.info('From: s3://{0}/{1}'.format(program.Bucket, conf['keyprefix']))
    log.info('To  : {0}\n'.format(conf['localroot']))

    s3ops = s3BuildOps(conf)

    result = query_yes_no("ARE YOU SURE?")
    # result = True

    if result:
        for key in s3ops:
            s3ops[key].execute()
    else:
        log.info("\n<EXITING> No sync performed\n")



def getDataDir(args):
    log = Logger("EnvCheck")
    envroot = None
    if args.datadir:
        log.info("datadir argument found: {0}".format(args.datadir))
        envroot = args.datadir
    else:
        envroot = os.getenv(DATA_ENV_VAR)

    # Env set and path exists. All is good.
    if envroot and os.path.isdir(envroot):
        log.info("Datadir `{0}` exists.".format(envroot))
    elif envroot and not os.path.isdir(envroot):
        log.warning("WARNING: Folder does not exist: {0}".format(envroot))
        if query_yes_no("Create this directory?"):
            try:
                os.makedirs(envroot)
            except Exception as e:
                raise Exception("ERROR: Directory `{0}` could not be created.".format(envroot))
    else:
        raise Exception("ERROR: You must either specify --datadir or set environment variable `{0}` to the root data directory.".format(DATA_ENV_VAR))
    return envroot

def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir',
                        help='Local path to the root of the program on your local drive')
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



