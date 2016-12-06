from rspupload import *


def rsplist(args):
    """
    :param inputRas:
    :param maskRas:
    :return:
    """
    setuplogs(args.logfile)
    if re.match('^https*:\/\/.*', args.program) is not None:
        try:
            file = urllib2.urlopen(args.program)
            data = file.read()
            file.close()
            programET = ET.fromstring(data)
        except:
            err = "ERROR: Could not download <{0}>".format(args.program)
            logging.error(err)
            raise ValueError(err)
    else:
        programET = ET.parse(args.program).getroot()


    printTitle('STARTING PYTHON LISTER', "=")

    bucket = getBucket(programET)
    logprint("Found bucket: {0}".format(bucket) )
    remotePath = getPathFromName(args.projectname, programET)

    print "yo"


def getPathFromName(projType, program):
    """
    Figure out what the repository path should be
    :param project:
    :param program:
    :return:
    """
    printTitle('Getting remote path...')

    # First let's get the project type
    assert not _strnullorempty(projType), "ERROR: <ProjectType> not found in project XML."
    logprint("Project Type Detected: {0}".format(projType))

    # Now go get the product node from the program XML
    patharr = findprojpath(projType, program)
    assert patharr is not None,  "ERROR: Product '{0}' not found anywhere in the program XML".format(projType)
    printTitle("Building Path to Product: ".format(projType))

    extpath = []
    for idx, seg in enumerate(patharr):
        if 'Level' in seg:
            logprint("{0}/Level:{1}".format(idx*'  ', seg['Level']))
            extpath.append({'Level': seg['Level']})
        elif 'Container' in seg:
            logprint("{0}/Container:{1}".format(idx * '  ', seg['Container']))
            extpath.append({'Container': seg['Container']})
        elif 'Project' in seg:
            logprint("{0}/Project:{1}".format(idx * '  ', seg['Project']))
            extpath.append({'Project': seg['Project']})

    # Trim the first slash for consistency elsewhere
    if len(extpath) > 0 and extpath[0] == '/':
        extpath = extpath[1:]
    logprint("Final remote path to product: {0}".format(extpath))

    return extpath


def _strnullorempty(str):
    return str is None or len(str.strip()) == 0

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
    args = parser.parse_args()
    try:
        rsplist(args)
    except:
        print 'Unxexpected error: {0}'.format(sys.exc_info()[0])
        raise
        sys.exit(0)

"""
This handles the argument parsing and calls our main function
If we're not calling this from the command line then
"""
if __name__ == '__main__':
    main()
