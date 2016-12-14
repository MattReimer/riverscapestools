import sys
import os
import re
from loghelper import Logger

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def querychoices(title, options, question):
    # cls()
    if len(options) == 1:
        return options[0]

    log = Logger("MENU")
    log.title(title, "=")
    for idx, cstr in enumerate(options):
        print "({0}) {1}".format(idx+1, cstr)

    while True:
        sys.stdout.write(question + " [Choose One] ")
        choice = raw_input()

        try:
            nchoice = int(choice.strip())
            if nchoice < 1 or nchoice > len(options):
                raise ValueError("Choice is out of range")
            return options[nchoice-1]
        except ValueError as e:
            sys.stdout.write(
                "Please respond with a single integer value. \n".format(default))