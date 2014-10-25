from TestCase import *
from TestContext import TestContext


class TestMotor(TestCase):
    def __init__(self, steps):
        TestCase.__init__(self)
        self.steps = int(steps)
        self.monitorFrequency = 1000
        # Rotations per second for the stepper test
        self.stepperTestRPS = 3

    def name(self):
        if self.steps == 1:
            step = "Full"
        elif self.steps == 2:
            step = "Half"
        else:
            step = "1/%d" % self.steps
        return "Motors %s Step" % step

    def _test(self, context):
        monitorPin = context.pinmapping.get('StepperMonitorPin', -1)
        triggerPin = context.pinmapping.get('StepperTriggerPin', -1)

        context.log("Testing %s forward..." % self.name(),
                    TestContext.LOG_LEVEL_INFO)
        context.target.setMicroStepping(self.steps)
        context.target.runSteppers(frequency = 200 * self.steps * self.stepperTestRPS,
                                   steps = 200 * self.steps,
                                   direction = context.target.UP,
                                   triggerPin = triggerPin, wait = False)
        self.forward = context.controller.monitorSteppers(pin = monitorPin, \
                                        frequency = self.monitorFrequency)

        context.log("Testing %s reverse..." % self.name(),
                    TestContext.LOG_LEVEL_INFO)
        context.target.setMicroStepping(self.steps)
        context.target.runSteppers(frequency = 200 * self.steps * self.stepperTestRPS,
                                   steps = 200 * self.steps,
                                   direction = context.target.UP,
                                   triggerPin = triggerPin, wait = False)
        self.reverse = context.controller.monitorSteppers(pin = monitorPin,
                                                           frequency = self.monitorFrequency)
        self.results = self.forward + self.reverse

        finished = context.target.waitForFinish(commands = 2, timeout = 2, clear = True)
        if not finished:
            self.error_string = "Monitoring failed"
            self.status = TestStatus.FAILED


    def _verify(self, context):
        if -1 in self.results:
            self.error_string = "Timed out"
            self.status = TestStatus.FAILED
        else:
            self.status = TestStatus.SUCCESS
            self.error_string = None
            failed_idx = []
            for i in range(5): #Iterate over each stepper
                forward = self.forward[i]
                reverse = self.reverse[i]
                context.log("Forward -> " + str(forward) + \
                            "Reverse -> " + str(reverse),
                            TestContext.LOG_LEVEL_DEBUG)
                for j in range(5): #Iterates over each entry in the test list
                    #Here we fold the recording values onto each other and make sure
                    #each residency time in a flag section is within +- 10 for
                    #the forward and reverse segments
                    validRange = range(reverse[4-j]-10,reverse[4-j]+10)
                    if forward[j] not in validRange and i not in failed_idx:
                        failed_idx += (i,)
                        self.status = TestStatus.FAILED
            if len (failed_idx) > 0:
                self.error_string = "Failed Steppers : %s" % ", ".join(
                    map(lambda x: context.pinmapping.getName('Axis', x),
                        failed_idx))
                context.failedAxes = failed_idx

