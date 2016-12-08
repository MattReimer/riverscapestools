from logging import Logger

class Program():

    def __init__(self, programET):
        self.DOM = programET
        self.Collections = {}
        self.Groups = {}
        self.Products = {}
        self.Hierarchy = {}
        self.Bucket = None
        self.log = Logger('Program')
        # Populate everything
        self.getBucket()
        self.parseCollections()
        self.parseGroups()
        self.parseProducts()
        self.parseTree(self.DOM.find('Hierarchy/*'))

    def parseCollections(self):
        for col in self.DOM.findall('Definitions/Collections/Collection'):
            self.Collections[col.attrib['id']] = {
                'name': col.attrib['name']
            }

    def parseGroups(self):
        for grp in self.DOM.findall('Definitions/Groups/Group'):
            self.Groups[grp.attrib['id']] = {
                'name': grp.attrib['name'],
                'folder': grp.attrib['folder']
            }

    def parseProducts(self):
        for prod in self.DOM.findall('Definitions/Products/Product'):
            self.Products[prod.attrib['id']] = {
                'name': prod.attrib['name'],
                'folder': prod.attrib['folder']
            }

    def parseTree(self, etNode, treeNode = None):

        obj = {}

        if etNode.tag == 'Product' and 'ref' in etNode.attrib:
            obj['type'] = 'product'
            obj['node'] = self.Products[etNode.attrib['ref']]

        elif etNode.tag in ['Group', 'Collection']:
            obj['children'] = []
            if etNode.tag == 'Group':
                obj['type'] = 'group'
                obj['node'] = self.Groups[etNode.attrib['ref']]
            else:
                obj['type'] = 'collection'
                obj['node'] = self.Collections[etNode.attrib['ref']]

            for child in etNode.getchildren():
                obj['children'].append(self.parseTree(child, obj['children']) )

        if treeNode is None:
            self.Hierarchy = obj

        return obj

    def getBucket(self):
        try:
            self.Bucket = self.DOM.find("MetaData/Meta[@name='s3bucket']").text
            self.log.info("S3 Bucket Detected: {0}".format(self.Bucket))
        except:
            msg = "ERROR: No <Meta Name='s3bucket'>riverscapes</Meta> tag found in program XML"
            self.log.error(msg)
            raise ValueError(msg)

    def findprojpath(self, prodname, node=None, path=[]):
        """
        Find the path to the desired project
        :param projname:
        :param etNode:
        :param path:
        :return:
        """
        if node is None:
            node = self.Hierarchy

        if node['type'] == 'product' and node['node']['name'] == prodname:
            path.append({'product': node['node']['folder']})
            return path
        elif node['type'] in ['group', 'collection']:

            newpath = path[:]
            if node['type'] == 'collection':
                newpath.append({node['type']: node['node']['name']})
            else:
                newpath.append({node['type']: node['node']['folder']})

            for child in node['children']:
                result = self.findprojpath(prodname, child, newpath)
                if result is not None:
                    return result