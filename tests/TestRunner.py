from TestContext import TestContext

class TestRunner(object):
    def __init__(self):
        self._tests = []
        self._successful = 0
        self._failed = 0
        self._disabled = 0
        self._canceled = 0
        self._total = 0

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

    def Run(self, tests_to_run=None):
        context = self.context
        no_errors = True
        fatal = False

        self._successful = 0
        self._failed = 0
        self._disabled = 0
        self._canceled = 0
        self._total = 0
        for test in self.tests:
            test.reset()

        context.TestingStarted(self.tests)

        for test in self.tests:
            if not fatal or test._finally:
                if (tests_to_run is None and test.enabled) or \
                   (tests_to_run and (test.required or test in tests_to_run)):
                    self._total += 1
                    success = test.Test(context)
                    no_errors &= success
                    if success:
                        self._successful += 1
                    else:
                        self._failed += 1
                        if test.fatal:
                            fatal = True
                else:
                    self._disabled += 1
            else:
                test.cancel()
                self._canceled += 1
        context.TestingEnded(self.tests, self._total, self._successful,
                             self._failed, self._disabled, self._canceled)

        return no_errors
