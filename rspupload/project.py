from loghelper import Logger

class Project():

    def __init__(self, programET, projectRoot):
        self.log = Logger('Project')
        self.DOM = programET
        self.LocalRoot = projectRoot

    def getPath(self, program):
        """
        Figure out what the repository path should be
        :param project:
        :param program:
        :return:
        """
        self.log.title('Getting remote path...')

        # First let's get the project type
        projType = self.DOM.find('./ProjectType').text
        assert not _strnullorempty(projType), "ERROR: <ProjectType> not found in project XML."
        self.log.info("Project Type Detected: {0}".format(projType))

        # Now go get the product node from the program XML
        patharr = program.findprojpath(projType)
        assert patharr is not None,  "ERROR: Product '{0}' not found anywhere in the program XML".format(projType)
        self.log.title("Building Path to Product: ".format(projType))

        extpath = ''
        for idx, seg in enumerate(patharr):
            if 'collection' in seg:
                col = self.getcollection(seg['collection'])
                self.log.info("{0}/collection:{1} => {2}".format(idx*'  ', seg['collection'], col))
                extpath += '/' + col
            elif 'group' in seg:
                self.log.info("{0}/group:{1}".format(idx * '  ', seg['group']))
                extpath += '/' + seg['group']
            elif 'product' in seg:
                self.log.info("{0}/product:{1}".format(idx * '  ', seg['product']))
                extpath += '/' + seg['product']

        # Trim the first slash for consistency elsewhere
        if len(extpath) > 0 and extpath[0] == '/':
            extpath = extpath[1:]
        self.log.info("Final remote path to product: {0}".format(extpath))

        return extpath

    def getcollection(self, colname):
        """
        Try to pull the Collection out of the project file
        :param colname: string with the Collection we're looking for
        :param project: the ET node with the project xml
        :return:
        """
        try:
            val = self.DOM.find("MetaData/Meta[@name='{0}']".format(colname)).text
        except AttributeError:
            raise ValueError("ERROR: Could not find <Meta name='{0}'>########</Meta> tag in project XML".format(colname))
        return val

def _strnullorempty(str):
    return str is None or len(str.strip()) == 0