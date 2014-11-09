from TestCase import *

class TestAnalog(TestCase):
    READ_FROM_TARGET = 0
    READ_FROM_CONTROLLER = 1
    def __init__(self, name, pins_name, read_from, mins, maxs):
        TestCase.__init__(self)
        self.pins_name = pins_name
        self.read_from = read_from
        self.mins = mins
        self.maxs = maxs
        self._name = name

    def reset(self):
        TestCase.reset(self)
        self._failed_idx = []

    def name(self):
        return self._name if self._name else "Analog read"


    def _analogToVoltage(self, analog_values, dividerFactor, voltage = 5.0,
                         resolution = 1023.0):
        voltage_values = []
        for val in analog_values:
            voltage_values += [(val/resolution)*(voltage/dividerFactor)]

        return voltage_values

    def _test(self, context):
        if self.read_from == TestAnalog.READ_FROM_TARGET:
            board = 'target'
        else:
            board = 'controller'

        for pin in context.pinmapping.get(self.pins_name):
            self.results += getattr(context, board).analogRead(pin)
        if -1 in self.results:
            self.error_string = "Reading analog value failed."
            self.status = TestStatus.FAILED


    def _verify(self, context):
        if -1 in self.results:
            self.error_string = "Timed out"
            self.status = TestStatus.FAILED
        else:
            self.status = TestStatus.SUCCESS
            self.error_string = None
            for idx, val in enumerate(self.results):
                if not self.mins[idx] <= val <= self.maxs[idx]:
                    self._failed_idx += (idx,)
                    self.error_string = "Value outside acceptable range"
                    self.status = TestStatus.FAILED

class TestThermistors(TestAnalog):
    def __init__(self, mins, maxs):
        TestAnalog.__init__(self, "Thermistors", 'ThermistorPins',
                            TestAnalog.READ_FROM_TARGET, mins, maxs)

    def _verify(self, context):
        TestAnalog._verify(self, context)

        if self.status == TestStatus.FAILED and len (self._failed_idx) > 0:
            self.error_string = "Failed Thermistors : %s" % ", ".join(
                map(lambda x: context.pinmapping.getName('Thermistor', x),
                    self._failed_idx))
        context.failedThermistors = self._failed_idx

class TestPowerRails(TestAnalog):
    def __init__(self, dividerFactor, mins, maxs):
        TestAnalog.__init__(self, "Supply Voltages", 'PowerRailPins',
                            TestAnalog.READ_FROM_CONTROLLER, mins, maxs)
        self.dividerFactor = dividerFactor

    def _verify(self, context):
        self.analog_results = self.results
        self.results = self._analogToVoltage(self.analog_results,
                                             self.dividerFactor)
        context.log("Analog result: %s" % str(self.analog_results),
                    context.LOG_LEVEL_DEBUG)
        TestAnalog._verify(self, context)

        if self.status == TestStatus.FAILED and len (self._failed_idx) > 0:
            self.error_string = "Failed Supply Rails : %s" % ", ".join(
                map(lambda x: context.pinmapping.getName('PowerRail', x),
                    self._failed_idx))
        context.failedSupplies = self._failed_idx

class TestVRefs(TestAnalog):
    def __init__(self, dividerFactor, mins, maxs):
        TestAnalog.__init__(self, "Stepper's Voltage reference", 'VRefPins',
                            TestAnalog.READ_FROM_CONTROLLER, mins, maxs)
        self.dividerFactor = dividerFactor


    def _verify(self, context):
        self.analog_results = self.results
        self.results = self._analogToVoltage(self.analog_results,
                                             self.dividerFactor)
        context.log("Analog result: %s" % str(self.analog_results),
                    context.LOG_LEVEL_DEBUG)
        TestAnalog._verify(self, context)

        if self.status == TestStatus.FAILED and len (self._failed_idx) > 0:
            self.error_string = "Axis VRef incorrect  : %s" % ", ".join(
                map(lambda x: context.pinmapping.getName('Axis', x),
                    self._failed_idx))
        elif self.status == TestStatus.SUCCESS:
            if max(self.analog_results) - min(self.analog_results) >= 15:
                self.error_string =  "Vref variance too high"
                self.status = TestStatus.FAILED
