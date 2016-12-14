import unittest

class TestuserInput(unittest.TestCase):
    TESTARR = [0, 2, 3, 435, 234, "2343"]
    TESTOBJ = {
        "test1": "test1val",
        "test2": "test2val",
        "test3": "test3val",
        "test4": "test4val",
        "test5": "test5val"
    }

    def test_validateChoices(self):
        from userinput import validateChoices

        self.assertTrue(validateChoices('1', self.TESTARR))
        self.assertTrue(validateChoices('1,', self.TESTARR))
        self.assertTrue(validateChoices('1,2,3,4,5', self.TESTARR))

        self.assertFalse(validateChoices('-1,2,3,4,5', self.TESTARR))
        self.assertFalse(validateChoices('1,2,3,10,5', self.TESTARR))

        self.assertTrue(validateChoices('1', self.TESTOBJ))
        self.assertTrue(validateChoices('1,', self.TESTOBJ))
        self.assertTrue(validateChoices('1,2,3,4,5', self.TESTOBJ))

        self.assertFalse(validateChoices('-1,2,3,4,5', self.TESTOBJ))
        self.assertFalse(validateChoices('1,2,3,10,5', self.TESTOBJ))

        self.assertFalse(validateChoices('1,SOMETHING', self.TESTOBJ))
