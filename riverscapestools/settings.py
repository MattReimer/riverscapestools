from logger import Logger
from os import path, getenv, makedirs
from userinput import query_yes_no

class defaults:
    """
    There are a few constants we need to set.
    """
    ProgramXML='https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml'
    DataENVName = "RSDATADIR"

def getDataDir(args):
    """
    This will either grab the data dir from an environment variable
    or it will use one that you specify
    :param args:
    :return:
    """
    log = Logger("EnvCheck")
    envroot = None
    if args.datadir:
        log.info("datadir argument found: {0}".format(args.datadir))
        envroot = args.datadir
    else:
        envroot = getenv(defaults.DataENVName)

    # Env set and path exists. All is good.
    if envroot and path.isdir(envroot):
        log.info("Datadir `{0}` exists.".format(envroot))
    elif envroot and not path.isdir(envroot):
        log.warning("WARNING: Folder does not exist: {0}".format(envroot))
        if query_yes_no("Create this directory?"):
            try:
                makedirs(envroot)
            except Exception as e:
                raise Exception("ERROR: Directory `{0}` could not be created.".format(envroot))
    else:
        raise Exception("ERROR: You must either specify --datadir or set environment variable `{0}` to the root data directory.".format(defaults.DataENVName))
    return envroot