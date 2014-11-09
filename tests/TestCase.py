from TestContext import TestContext

class TestStatus:
    DISABLED = 0
    PENDING = 1
    SUCCESS = 2
    FAILED = 4
    TESTING = 8
    CANCELED = 16

    @staticmethod
    def ToName(status):
        return {
            TestStatus.DISABLED: "Disabled",
            TestStatus.PENDING: "Pending",
            TestStatus.SUCCESS: "Success",
            TestStatus.FAILED: "Failed",
            TestStatus.TESTING: "Testing",
            TestStatus.CANCELED: "Canceled",
        }.get(status, "Unknown")

class TestCase(object):
    def __init__(self):
        self._enabled = True
        self._required = False
        self.__finally = False
        self._fatal = False
        self._hidden = False
        self._id = None
        self.reset()

    def name(self):
        """ The name of the test case """
        return "Unnamed Test Case"

    @property
    def id(self):
        return self._id if self._id else self.__class__.__name__
    @id.setter
    def id(self, id):
        self._id = id

    @property
    def required(self):
        """Whether this test case is required (cannot be disabled)"""
        return self._required

    @required.setter
    def required(self, required):
        self._required = required

    @property
    def hidden(self):
        """Whether this test case should be hidden from the user/GUI"""
        return self._hidden

    @hidden.setter
    def hidden(self, hidden):
        self._hidden = hidden

    @property
    def fatal(self):
        """Whether this test case is fatal (stop subsequent tests)"""
        return self._fatal

    @fatal.setter
    def fatal(self, fatal):
        self._fatal = fatal

    @property
    def _finally(self):
        """Whether this test case is required should always be called even if
        previous tests in the list have failed (such as poweroff/disconnect)"""
        return self.__finally

    @_finally.setter
    def _finally(self, _finally):
        self.__finally = _finally

    @property
    def enabled(self):
        """Whether this test case is enabled or not """
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        # Can't disable a required test case
        if self.required:
            enabled = True
        self._enabled = enabled
        self.reset()

    def reset(self):
        """ Reset the test case before running the test again """
        self.results = []
        if self.enabled:
            self.status = TestStatus.PENDING
            self.error_string = None
        else:
            self.status = TestStatus.DISABLED
            self.error_string = "This test is disabled"

    def cancel(self):
        self.status = TestStatus.CANCELED
        self.error_string = "Testing was canceled"


    def success(self):
        """ Whether the test was successful """
        return self.status == TestStatus.SUCCESS

    def failed(self):
        """ Whether the test failed """
        return self.status == TestStatus.FAILED or \
            self.status == TestStatus.CANCELED

    def Test(self, context):
        """ Execute the test and fill self.results with the result """
        self.reset()
        if self.status == TestStatus.DISABLED:
            return False
        self.status = TestStatus.TESTING

        if not self.hidden:
            context.log("Testing %s started" % self.name(),
                        TestContext.LOG_LEVEL_LOG)
        try:
            self._test(context)
        except Exception, e:
            self.status = TestStatus.CANCELED
            self.error_string = "Error executing test : %s" % e
        return self.Verify(context)

    def _test(self, context):
        """ Function to be overridden by child class """
        raise NotImplementedError

    def Verify(self, context):
        """ Verify self.results and set self.status and self.error_string """
        # Do not verify results more than once and we only need to verify them
        # After we just finished testing
        if self.status == TestStatus.TESTING:
            if not self.hidden:
                context.log("Verifying %s..." % self.name(),
                        TestContext.LOG_LEVEL_LOG)
            self._verify(context)
        if not self.hidden:
            context.log("%s : %s" % (self.name(), \
                        "Success" if self.status == TestStatus.SUCCESS else \
                        "%s (%s)" % (self.error_string, \
                                     TestStatus.ToName(self.status))),
                        TestContext.LOG_LEVEL_LOG,
                        color = 'green' if self.success() else 'red')
            context.log("Results : %s" % str(self.results),
                        TestContext.LOG_LEVEL_DEBUG)
        return not self.failed()


    def _verify(self, context):
        """ Function to be overridden by child class """
        raise NotImplementedError

