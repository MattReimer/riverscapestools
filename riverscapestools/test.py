import unittest
import __builtin__

class TestuserInput(unittest.TestCase):

    def test_download(self):
        from rspdownload import rspdownload
        inputs = InputFaker(['1', 'Y', 'Y'])

        class args:
            datadir='./test/dataDir'
            program='https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml'
            logfile=''
            force=False
            verbose=False

        rspdownload(args)
        self.assertTrue(True)

    def test_upload(self):
        from rspupload import rspupload
        inputs = InputFaker(['Y'])

        class args:
            project=FileTypeFaker('./test/SampleProject/fhm_project.xml')
            program='https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml'
            logfile=''
            force=True
            verbose=False

        rspupload(args)
        self.assertTrue(True)

    def test_list(self):
        from rsplist import rsplist
        inputs = InputFaker(['Y'])
        class args:
            projectname='FHM'
            program='https://raw.githubusercontent.com/Riverscapes/Program/master/Program/Riverscapes.xml'
            logfile=''
            force=True
            verbose=False

        rsplist(args)
        self.assertTrue(True)

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