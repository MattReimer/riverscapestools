import logging


def logprint(msg):
    print msg
    logging.info(msg)

def setuplogs(filename):
    logging.basicConfig(filename=filename,
                        filemode='w',
                        datefmt='%m-%d %H:%M',
                        level=logging.INFO)
