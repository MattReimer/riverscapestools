from rspupload import *
from botohelper import s3ProductWalker
from loghelper import Logger
from program import Program

def rsplist(args):
    """
    :param inputRas:
    :param maskRas
    :return:
    """
    log = Logger('Program')

    program = Program(args.program)

    log.title('STARTING Project Lister', "=")

    remotePath = program.getProdPath(args.projectname)

    log.title('Walking through and finding projects:')
    s3ProductWalker(program.Bucket, remotePath)

    log.title("Done")


def main():
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument('projectname',
                        help='Name of the program we are looking for.',
                        type=str)
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
        rsplist(args)
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
