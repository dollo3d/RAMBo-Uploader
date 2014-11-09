from testinterface import TestInterface
from termcolor import colored
from collections import OrderedDict
import time

class TestPinMapping(object):
    """ The pin mappings for the various test cases """
    def __init__(self):
        pass

    def get(self, pins, default = []):
        return getattr(self, pins, default)

    def getName(self, item, index = None, default = "Unknown"):
        try:
            names = getattr(self, item + "Names", default)
            if index is not None:
                return names[index]
            else:
                return names
        except:
            return default

class TestContext(object):
    """ The context object to be sent to every test case.
    The context will be used to communicate data to the test cases, such as
    the configuration used, the target/controller objects, store metadata from
    tests that can be used by other tests (such as a serial number, or
    common data needed by multiple similar tests), etc..
    """
    LOG_LEVEL_LOG=0
    LOG_LEVEL_WARNING=1
    LOG_LEVEL_ERROR=2
    LOG_LEVEL_INFO=3
    LOG_LEVEL_DEBUG=4

    def __init__(self, config):
        self.config = config
        self.target = TestInterface()
        self.controller = TestInterface()
        self.pinmapping = TestPinMapping()
        self.log_level = config.log_level
        self.start_time = None
        self.end_time = None

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        self._log_level = max(0, min(level, TestContext.LOG_LEVEL_DEBUG))

    def TestingStarted(self, tests):
        self.start_time = time.localtime()
        self.log("Test started at " + time.strftime("%Y-%m-%d %H:%M:%S",
                                                    self.start_time),
                 TestContext.LOG_LEVEL_INFO)

    def createResultsDictionary(self, tests):
        results = OrderedDict()
        for test in tests:
            results[test.name()] = {"status": test.status,
                                    "id": test.id,
                                    "results":test.results}

        return results

    def TestingEnded(self, tests, total, successful, failed, disabled, canceled):
        self.end_time = time.localtime()
        self.log("Writing results to database...", TestContext.LOG_LEVEL_INFO)

        if self.config.database:
            self.config.database.post(self.start_time, self.end_time, tests,
                                      self.createResultsDictionary(tests))

        self.log("\nTesting ended at " + time.strftime("%Y-%m-%d %H:%M:%S",
                                                       self.end_time),
                 TestContext.LOG_LEVEL_LOG)
        self.log("Total Tests      : %d" % total,
                 TestContext.LOG_LEVEL_LOG)
        self.log("Disabled Tests   : %d" % disabled,
                 TestContext.LOG_LEVEL_LOG)
        self.log("Successful Tests : %d" % successful,
                 TestContext.LOG_LEVEL_LOG, color='green')
        self.log("Failed Tests     : %d" % failed,
                 TestContext.LOG_LEVEL_LOG,
                 color=None if failed == 0 else 'red')
        self.log("Canceled Tests   : %d" % canceled,
                 TestContext.LOG_LEVEL_LOG,
                 color=None if canceled == 0 else 'red')
        self.log("\nOverall result   : %s\n" % ('Successful' if failed == 0
                                                else 'Failed'),
                    TestContext.LOG_LEVEL_LOG,
                    color='green' if failed == 0 else 'red')

    def log(self, string, level=LOG_LEVEL_LOG, color=None):
        if color is None:
            if level == TestContext.LOG_LEVEL_DEBUG:
                color = 'grey'
            elif level == TestContext.LOG_LEVEL_WARNING:
                color = 'orange'
            elif level == TestContext.LOG_LEVEL_ERROR:
                color = 'red'
        if level <= self.log_level:
            if color:
                print colored(string, color)
            else:
                print string
