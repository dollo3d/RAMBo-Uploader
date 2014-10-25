from motors import TestMotor

class TestProcessor(object):
    def __init__(self, config):
        self._config = config

        self.tests = (
#            ProgramICSP(), # Fatal=True
#            ProgramTestFirmware(), #  Required=True, Fatal=True
#            ConnectTarget(), #  Required=True, Fatal=True

#            TestPower(),

#            TestMosfets(TestMosfets.HIGH),
#            TestMosfets(TestMosfets.LOW),
#            TestEndStops(TestEndstops.HIGH),
#            TestEndStops(TestEndstops.LOW),
#            TestMXExt(TestEndstops.HIGH),
#            TestMXExt(TestEndstops.LOW),
#            TestPWMExt(TestEndstops.HIGH),
#            TestPWMExt(TestEndstops.LOW),

            TestMotor(1),
            TestMotor(2),
            TestMotor(4),
            TestMotor(8),
            TestMotor(16),

#            TestVRefs(),
#            TestThermistors(),

#            ProgramMarlin(),
#            DisconnectTarget(), # finally=True, Required=True
        )

    @property
    def context(self):
        return TestContext(self._config) # TODO: Fill the context

    def RunTests(self):
        context = self.context
        no_errors = True

        for test in self.tests:
            test.reset()

        for test in self.tests:
            if no_errors:
                no_errors = test.Execute(context)
            elif test._finally:
                test.Execute(context)
            else:
                test.cancel()

        return no_errors


class TestContext(object):
    """ The context object to be sent to every test case.
    The context will be used to communicate data to the test cases, such as
    the configuration used, the target/controller objects, store metadata from
    tests that can be used by other tests (such as the ConnectTarget test could
    fetch the serial number and store it in the context and it can be used by
    other test cases when writing to the log file), etc..
    """
    def __init__(self, config):
        self.config = config
        self.target = None
        self.controller = None

    def log(self, string):
        print string
