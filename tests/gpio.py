from TestCase import *

class TestGPIO(TestCase):
    LOW = 'pinLow'
    HIGH = 'pinHigh'
    TARGET_TO_CONTROLLER = 0
    CONTROLLER_TO_TARGET = 1
    DIRECTION_BOTH = 2
    def __init__(self, name, gpios_controller, gpios_target,
                 direction, write_pin, expected_result = None):
        TestCase.__init__(self)
        self.gpios_controller = gpios_controller
        self.gpios_target = gpios_target
        self.direction = direction
        self.write_pin = write_pin
        self.high = True if write_pin == self.HIGH else False
        self.expected = expected_result
        if self.expected is None:
            self.expected = 1 if self.high else 0
        self._name = name

    def reset(self):
        TestCase.reset(self)
        self._failed_idx = []

    def name(self):
        return "%s %s" % (self._name if self._name else "GPIO",
                          "High" if self.high else "Low")

    def _test(self, context):
        passed = True
        gpios_target = context.pinmapping.get(self.gpios_target)
        gpios_controller = context.pinmapping.get(self.gpios_controller)

        if self.direction == TestGPIO.TARGET_TO_CONTROLLER or \
           self.direction == TestGPIO.DIRECTION_BOTH:
            for pin in gpios_target:
                passed &= getattr(context.target, self.write_pin)(pin)
            for pin in gpios_controller:
                # We need to pullup in case a connection is floating (mosfet or disconnected wire)
                self.results += context.controller.pullupReadPin(pin)
        if self.direction == TestGPIO.CONTROLLER_TO_TARGET or \
           self.direction == TestGPIO.DIRECTION_BOTH:
            for pin in gpios_controller:
                passed &= getattr(context.controller, self.write_pin)(pin)
            for pin in gpios_target:
                # We need to pullup in case a connection is floating (mosfet or disconnected wire)
                self.results += context.target.pullupReadPin(pin)

        if -1 in self.results or not passed:
            self.error_string = "Reading pin value failed."
            self.status = TestStatus.FAILED


    def _verify(self, context):
        if -1 in self.results:
            self.error_string = "Timed out"
            self.status = TestStatus.FAILED
        else:
            self.status = TestStatus.SUCCESS
            self.error_string = None
            for idx, val in enumerate(self.results):
                if val != self.expected:
                    self._failed_idx += (idx,)
                    self.error_string = "Read pin returned wrong value"
                    self.status = TestStatus.FAILED


class TestEndstops(TestGPIO):
    def __init__(self, high):
        TestGPIO.__init__(self, "Endstops", 'EndstopControllerPins',
                          'EndstopTargetPins',
                          TestGPIO.CONTROLLER_TO_TARGET, high)

    def _verify(self, context):
        TestGPIO._verify(self, context)

        if self.status == TestStatus.FAILED and len (self._failed_idx) > 0:
            self.error_string = "Failed Endstops : %s" % ", ".join(
                map(lambda x: context.pinmapping.getName('Endstop', x),
                    self._failed_idx))
        context.failedEndstops = self._failed_idx

class TestMosfets(TestGPIO):
    def __init__(self, high):
        TestGPIO.__init__(self, "Mosfets", 'MosfetControllerPins',
                          'MosfetTargetPins', TestGPIO.TARGET_TO_CONTROLLER,
                          high)
        self.expected = 0 if self.high else 1

    def _verify(self, context):
        TestGPIO._verify(self, context)

        if self.status == TestStatus.FAILED and len (self._failed_idx) > 0:
            self.error_string = "Failed Mosfets : %s" % ", ".join(
                map(lambda x: context.pinmapping.getName('Mosfet', x),
                    self._failed_idx))
        context.failedMosfets = self._failed_idx
