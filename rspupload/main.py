import argparse
import sys
import os
import subprocess
import time
from os import path

import xml.etree.ElementTree as ET
from userinput import query_yes_no

def main(args):
    """
    :param inputRas:
    :param maskRas:
    :return:
    """
    printTitle('STARTING PYTHON UPLOADER', "=")
    programET = ET.parse(args.program.name).getroot()
    projectET = ET.parse(args.project.name).getroot()

    projectRoot = path.dirname(path.abspath(args.project.name))
    remotePath = GetPath(projectET, programET)

    printTitle('Creating AWS command:')
    cmd = ["aws", "s3", "sync", projectRoot, remotePath]
    print ' '.join(cmd)

    printTitle('The following files will be uploaded:')
    treeprint(projectRoot)

    print "\nThese files will be uploaded to: {0}\n".format(remotePath)
    result = query_yes_no("ARE YOU SURE?")

    if result:

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.poll() is None:
            for line in process.stdout:
                print line
            time.sleep(0.5)
    else:
        print "\n<EXITING> No sync performed\n"


def GetPath(project, program):
    """
    Figure out what the repository path should be
    :param project:
    :param program:
    :return:
    """
    printTitle('Getting remote path...')

    # First let's get the project type
    projType = project.find('.//ProjectType').text
    assert not _strnullorempty(projType), "ERROR: <ProjectType> not found in project XML."
    print "Project Type Detected: {0}".format(projType)
    try:
        bucketname = program.find("MetaData/Meta[@name='s3bucket']").text
        print "S3 Bucket Detected: {0}".format(bucketname)
    except:
        raise "ERROR: No <Meta Name='s3bucket'>riverscapes</Meta> tag found in program XML"

    # Now go get the product node from the program XML
    patharr = findprojpath(projType, program)
    assert patharr is not None,  "ERROR: Product '{0}' not found anywhere in the program XML".format()
    printTitle("Building Path to Product: ".format(projType))

    extpath = 's3://{0}'.format(bucketname)
    for idx, seg in enumerate(patharr):
        if 'Level' in seg:
            lvl= getlvl(seg['Level'], project)
            print "{0}/Level:{1} => {2}".format(idx*'  ', seg['Level'], lvl)
            extpath += '/' + lvl
        elif 'Container' in seg:
            print "{0}/Container:{1}".format(idx * '  ', seg['Container'])
            extpath += '/' + seg['Container']
        elif 'Project' in seg:
            print "{0}/Project:{1}".format(idx * '  ', seg['Project'])
            extpath += '/' + seg['Project']
    print "\n Final path to product: {0}".format(extpath)

    return extpath

def getlvl(lvlname, project):
    """
    Try to pull the level out of the project file
    :param lvlname: string with the level we're looking for
    :param project: the ET node with the project xml
    :return:
    """
    try:
        val = project.find("MetaData/Meta[@name='{0}']".format(lvlname)).text
        raise
    except:
        "ERROR: Could not find <Meta name='{0}'>########</Meta> tag in project XML".format(lvlname)
    return val

def findprojpath(projname, etNode, path=[]):
    """
    Find the path to the desired project
    :param projname:
    :param etNode:
    :param path:
    :return:
    """
    proj = etNode.find('Product[@id="{0}"]'.format(projname))
    children = etNode.findall('*')
    if proj is not None:
        path.append({'Project': proj.attrib['folder']})
        return path
    elif children is not None:
        for c in children:
            if 'name' in etNode.attrib:
                newpath = path[:]
                newpath.append({etNode.tag: etNode.attrib['name']})
                result = findprojpath(projname, c, newpath)
                if result is not None:
                    return result


def _strnullorempty(str):
    return str is None or len(str.strip()) == 0

def printTitle(str, sep='-'):
    print "\n{0}\n{1}".format(str, (len(str) + 2) * sep )

def treeprint(rootDir, first=True):
    if first:
        print rootDir + '/'
    currentdir = rootDir
    for lists in os.listdir(rootDir):
        spaces = len(currentdir) * ' ' + '/'
        path = os.path.join(rootDir, lists)
        if os.path.isfile(path):
            print spaces + lists
        elif os.path.isdir(path):
            print spaces + lists + '/'
            treeprint(path, False)



"""
This handles the argument parsing and calls our main function
If we're not calling this from the command line then
"""
if __name__ == '__main__':
    # parse command line options
    parser = argparse.ArgumentParser()

    parser.add_argument('project',
                        help='Path to the project XML file.',
                        type=argparse.FileType('r'))

    parser.add_argument('--program', type=argparse.FileType('r'), default=path.join('xml', 'Sample_Program.xml'),
                        help='Path to the Program XML file (optional)')

    args = parser.parse_args()

    try:
        main(args)
    except:
        print 'Unxexpected error: {0}'.format(sys.exc_info()[0])
        raise
        sys.exit(0)
