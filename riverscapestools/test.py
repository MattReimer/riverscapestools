import unittest
import __builtin__
from logger import Logger

class TestuserInput(unittest.TestCase):
    PROGRAMXML = './test/testprogram.xml'

    def test_downloadFHM(self):
        from rspdownload import rspdownload
        downloadinputs = InputFaker([
            '2', # (1) Network (2) Site)
            '1', # (1) FHM (2) GCD
            'Y',
            'Y'])

        scaffold = init(datadir='./test/dataDir', logfile='./test/logs/download_fhm.log')
        rspdownload(scaffold.args)
        self.assertTrue(True)

    def test_downloadGCD(self):
        from rspdownload import rspdownload
        downloadinputs = InputFaker([
            '2', # (1) Network (2) Site)
            '2', # (1) FHM (2) GCD
            'Y',
            'Y'])

        scaffold = init(datadir='./test/dataDir', logfile='./test/logs/download_gcd.log')
        rspdownload(scaffold.args)
        self.assertTrue(True)

    def test_downloadVBET(self):
        from rspdownload import rspdownload
        downloadinputs = InputFaker([
            '1', #  Network/Site)
            'Y',
            'Y'])

        scaffold = init(datadir='./test/dataDir', logfile='./test/logs/download_vbet.log')
        rspdownload(scaffold.args)
        self.assertTrue(True)

    def test_uploadFHM(self):
        from rspupload import rspupload
        inputs = InputFaker(['Y'])
        scaffold = init(project=FileTypeFaker('./test/sampleFHM/fhm_project.xml'), logfile='./test/logs/upload_fhm.log')
        rspupload(scaffold.args)

    def test_uploadGCD(self):
        from rspupload import rspupload
        inputs = InputFaker(['Y'])
        scaffold = init(project=FileTypeFaker('./test/sampleGCD/gcd_project.xml'), logfile='./test/logs/upload_gcd.log')
        rspupload(scaffold.args)

    def test_uploadVBET(self):
        from rspupload import rspupload
        inputs = InputFaker(['Y'])
        scaffold = init(project=FileTypeFaker('./test/sampleVBET/vbet_project.xml'), logfile='./test/logs/upload_vbet.log')
        rspupload(scaffold.args)

    def test_list(self):
        from rsplist import rsplist
        inputs = InputFaker(['Y'])
        scaffold = init(project='FHM', logfile='./test/logs/list VBET.log')
        rsplist(scaffold.args)
        self.assertTrue(True)

class init:

    class Arguments:
        PROGRAMXML = './test/testprogram.xml'
        __allowed = ("verbose", "force", "program", "project", "datadir", "logfile")

        def __init__(self, **kwargs):
            self.program = self.PROGRAMXML
            self.verbose = False
            self.delete = False
            self.force = False

            for k, v in kwargs.iteritems():
                assert( k in self.__class__.__allowed ), "NOT PERMITTED: {0}".format(k)
                setattr(self, k, v)

    def __init__(self, **kwargs):
        self.args = self.Arguments(**kwargs)
        self.log = Logger("Testing")
        self.log.setup(self.args)

class FileTypeFaker:
    def __init__(self, filename):
        self.name = filename

class InputFaker:
    """
    Just a happy little class to monkey-patch raw_inpout
    """
    def __init__(self, inputs):
        self.counter = 0
        self.inputs = inputs
        self.original_raw_input = __builtin__.raw_input
        print "--------------<MONKEY PATCH>--------------"
        __builtin__.raw_input = self.FakeIt

    def FakeIt(self):
        if self.counter >= len(self.inputs):
            raise ValueError("Ran out of inputs to use")
        val = self.inputs[self.counter]
        self.counter += 1
        return val

    def __exit__(self):
        # Remember to put things back the way they were
        print "--------------</MONKEY PATCH>--------------"
        __builtin__.raw_input = self.original_raw_input