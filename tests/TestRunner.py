class TestRunner(object):
    def __init__(self):
        self._tests = []

    @property
    def tests(self):
        return self._tests

    @tests.setter
    def tests(self, tests):
        self._tests = tests

    @property
    def context(self):
        raise NotImplementedError

    def __getitem__(self, idx):
        return self.tests[idx]

    def GetTest(self, name):
        for test in self.tests:
            if test.name() == name:
                return test
        return None

    def Run(self):
        context = self.context
        no_errors = True
        fatal = False

        for test in self.tests:
            test.reset()
        context.TestingStarted()

        for test in self.tests:
            if not fatal:
                success = test.Test(context)
                no_errors &= success
                print "Success is : %s" % success
                if not success and test.enabled and test.fatal:
                    fatal = True
                    print "is fatal!"
            elif test._finally:
                test.Test(context)
            else:
                test.cancel()
        context.TestingEnded()

        return no_errors
