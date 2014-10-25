from testinterface import TestInterface
from termcolor import colored
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
            if index:
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

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        self._log_level = max(0, min(level, TestContext.LOG_LEVEL_DEBUG))

    def TestingStarted(self):
        self.log("Test started at " + time.strftime("%Y-%m-%d %H:%M:%S",
                                                    time.localtime()),
                 TestContext.LOG_LEVEL_INFO)

    def TestingEnded(self):
        self.log("Writing results to database...", TestContext.LOG_LEVEL_INFO)
        # TODO write to database

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
