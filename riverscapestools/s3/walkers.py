import os
from riverscapestools import Logger
from transfers import Transfer
from operations import S3Operation

def s3BuildOps(conf):
    """
    Compare a source folder with what's already in S3 and given
    the direction you specify it should figure out what to do.
    :param src_files:
    :param keyprefix:
    :param bucket:
    :return:
    """
    s3 = Transfer(conf['bucket'])
    opstore = {}
    prefix = "{0}/".format(conf['keyprefix']).replace("//", "/")
    response = s3.list(prefix)

    # Get all the files we have locally
    if os.path.isdir(conf['localroot']):
        files = localProductWalker(conf['localroot'])
    else:
        files = {}

    # Fill in any files we find on the remote
    if 'Contents' in response:
        for result in response['Contents']:
            dstkey = result['Key'].replace(prefix, '')
            if dstkey in files:
                files[dstkey]['dst'] = result
            else:
                files[dstkey] = { 'dst': result }

    for relname in files:
        fileobj = files[relname]
        opstore[relname] = S3Operation(relname, fileobj, conf)

    return opstore

def localProductWalker(projroot, currentdir="", filedir={}):
    """
    This method has a similar recursive structure to s3FolderUpload
    but we're keeping it separate since it is only used to visualize
    the files in this folder
    :param rootDir:
    :param first:
    :return:
    """
    log = Logger('localProdWalk')
    for pathseg in os.listdir(os.path.join(projroot, currentdir)):
        spaces = len(currentdir) * ' ' + '/'
        relpath = os.path.join(currentdir, pathseg)
        abspath = os.path.join(projroot, relpath)
        if os.path.isfile(abspath):
            log.debug(spaces + relpath)
            filedir[relpath] = { 'src': abspath }
        elif os.path.isdir(abspath):
            log.debug(spaces + pathseg + '/')
            localProductWalker(projroot, relpath, filedir)
    return filedir


def s3GetFolderList(bucket, prefix):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    log = Logger('CollectionList')
    s3 = Transfer(bucket)
    results = []
    # list everything at this collection
    response = s3.list(prefix, Delimiter='/')
    if 'CommonPrefixes' in response:
        for o in response.get('CommonPrefixes'):
            results.append(o['Prefix'].replace(prefix, '').replace('/', ''))
    return results

def s3ProductWalker(bucket, patharr, currpath=[], currlevel=0):
    """
    Given a path array, ending in a Product, snake through the
    S3 bucket recursively and list all the products available
    :param patharr:
    :param path:
    :param currlevel:
    :return:
    """
    log = Logger('ProductWalk')
    s3 = Transfer(bucket)
    if currlevel >= len(patharr):
        return

    # If it's a collection then we need to iterate over folders and recurse on each
    if patharr[currlevel]['type'] == 'collection':
        # list everything at this collection
        pref = "/".join(currpath)+"/" if len(currpath) > 0 else ""
        result = s3.list(pref, Delimiter='/')
        if 'CommonPrefixes' in result:
            for o in result.get('CommonPrefixes'):
                s3ProductWalker(bucket, patharr, o.get('Prefix')[:-1].split('/'), currlevel + 1)
        else:
            return

    # If it's a container then no iteration necessary. Just append the path and recurse
    elif patharr[currlevel]['type'] == 'group':
        currpath.append(patharr[currlevel]['folder'])
        s3ProductWalker(bucket, patharr, currpath, currlevel + 1)

    # If it's a project then get the XML file and print it
    elif patharr[currlevel]['type'] == 'product':
        currpath.append(patharr[currlevel]['folder'])
        result = s3.list("/".join(currpath)+"/", Delimiter='/')
        if 'Contents' in result:
            for c in result['Contents']:
                if os.path.splitext(c['Key'])[1] == '.xml':
                    log.info('Project: {0} (Modified: {1})'.format(c['Key'], c['LastModified']))
        return