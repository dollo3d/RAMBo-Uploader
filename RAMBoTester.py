#!/usr/bin/python

from tests.motors import *
from tests.analog import *
from tests.gpio import *
from tests.flashing import *
from tests.TestRunner import *
from tests.TestCase import *
from tests.TestContext import *
from avrdude import *
from atmega import *
from testinterface import *
import serial.tools.list_ports

class RAMBoTester(TestRunner):
    # Power Rails
    ExtruderRailVoltage = 24.0
    BedRailVoltage = 24.0
    VCCRailVoltage = 5.0
    ErrorMargin = 0.05 # 5%

    # VRef
    MinVRefValue = 166
    MaxVRefValue = 195

    # Thermistors
    MinThermistorValue = 967
    MaxThermistorValue = 985

    def __init__(self, config):
        TestRunner.__init__(self)
        self._config = config
        self._context = RAMBoContext(self._config)

        # Set up AVRDUDE
        avrdude = Avrdude()
        avrdude.path = configuration.avrdude_path
        avrdude.programmer = configuration.serial_programmer
        avrdude.port = self.context.target_port
        avrdude.baudrate = "115200"
        avrdude.autoEraseFlash = False

        # Set up Test firmware TestCase
        test_firmware = Atmega()
        test_firmware.name = "atmega2560"
        test_firmware.bootloader = config.test_firmware_path
        program_test_firmware = ProgramFirmware(avrdude, test_firmware,
                                     10, "Program Test Firmware")
        program_test_firmware.fatal = True
        program_test_firmware.required = True

        # Set up Vendor firmware TestCase
        vendor_firmware = Atmega()
        vendor_firmware.name = "atmega2560"
        vendor_firmware.bootloader = config.vendor_firmware_path
        program_vendor_firmware = ProgramFirmware(avrdude, vendor_firmware,
                                     120, "Program Vendor Firmware")

        # Set up M32U2 ICSP Programming TestCase
        icsp_m32u2 = Avrdude()
        icsp_m32u2.path = config.avrdude_path
        icsp_m32u2.verbose = 0
        icsp_m32u2.verify = config.icsp_verify
        icsp_m32u2.programmer = config.m32u2_icsp_programmer
        icsp_m32u2.port = config.m32u2_icsp_port

        m32u2_image = Atmega()
        m32u2_image.name = "m32u2"
        m32u2_image.bootloader = config.m32u2_bootloader_path
        m32u2_image.lockBits = "0x0F"
        m32u2_image.extFuse = "0xF4"
        m32u2_image.highFuse = "0xD9"
        m32u2_image.lowFuse = "0xEF"

        m32u2_test = ProgramFirmware(icsp_m32u2, m32u2_image,
                                     60, "Program M32U2 Bootloader")
        m32u2_test.fatal = True

        # Set up M2560 ICSP Programming TestCase
        icsp_m2560 = Avrdude()
        icsp_m2560.path = config.avrdude_path
        icsp_m2560.verbose = 0
        icsp_m2560.verify = config.icsp_verify
        icsp_m2560.programmer = config.m2560_icsp_programmer
        icsp_m2560.port = config.m2560_icsp_port

        m2560_image = Atmega()
        m2560_image.name = "m2560"
        m2560_image.bootloader = config.m2560_bootloader_path
        m2560_image.lockBits = "0x0F"
        m2560_image.extFuse = "0xFD"
        m2560_image.highFuse = "0xD0"
        m2560_image.lowFuse = "0xFF"

        m2560_test = ProgramFirmware(icsp_m2560, m2560_image,
                                     60, "Program M2560 Bootloader")
        m2560_test.fatal = True

        self.tests = [
            m32u2_test,
            m2560_test,
            FindTarget(self, avrdude), #  Required=True, Fatal=True
            program_test_firmware, #  Required=True, Fatal=True
            ConnectTarget(), #  Required=True, Fatal=True

            TestPowerRails([self.ExtruderRailVoltage * (1 - self.ErrorMargin),
                             self.BedRailVoltage * (1 - self.ErrorMargin),
                             self.VCCRailVoltage * (1 - self.ErrorMargin)],
                            [self.ExtruderRailVoltage * (1 + self.ErrorMargin),
                             self.BedRailVoltage * (1 + self.ErrorMargin),
                             self.VCCRailVoltage * (1 + self.ErrorMargin)]),

            TestMosfets(TestGPIO.HIGH),
            TestMosfets(TestGPIO.LOW),
            TestEndstops(TestGPIO.HIGH),
            TestEndstops(TestGPIO.LOW),
            # TODO: Add I2C and SPI

            TestMotor(1),
            TestMotor(2),
            TestMotor(4),
            TestMotor(8),
            TestMotor(16),

            TestVRefs([self.MinVRefValue] * len(RAMBoPinMapping.VRefPins),
                      [self.MaxVRefValue] * len(RAMBoPinMapping.VRefPins)),
            TestThermistors([self.MinThermistorValue] * \
                              len(RAMBoPinMapping.ThermistorPins),
                            [self.MaxThermistorValue] * \
                              len(RAMBoPinMapping.ThermistorPins)),

            DisconnectTarget(), # finally=True, Required=True
            program_vendor_firmware,
        ]


    @property
    def context(self):
        return self._context


class RAMBoPinMapping(TestPinMapping):
    """ The pin mappings for the various RAMBo functions """

    # [X-min, Y-min, Z-min, X-max, Y-max, Z-max]
    EndstopTargetPins = [12, 11, 10, 24, 23, 30]
    # [EXT2-10, EXT2-12, EXT2-14, EXT2-16, EXT2-18, EXT2-20 ]
    EndstopControllerPins = [83, 82, 81, 80, 79, 78]
    EndstopNames = ["X-Min", "Y-Min", "Z-Min", "X-Max", "Y-Max", "Z-Max"]

    # [Bed, Fan2, Fan1, Heat1, Fan0, Heat0]
    MosfetTargetPins = [3, 2, 6, 7, 8, 9]
    # [MX1-5, MX1-4, MX2-5, MX2-4, MX3-5, MX3-4]
    MosfetControllerPins = [44, 32, 45, 31, 46, 30]
    MosfetNames = ["Heat-Bed","Fan-2","Fan-1","Heat-1","Fan-0","Heat-0"]

    # For stepper's trigger/monitor pins, we use existing mosfet connections
    # The steppers's opto-endstops are however monitored by the firmware
    # using bits [2..6] of Arduino PORTJ which is :
    # [EXT2-9, EXT2-11, EXT2-15, EXT2-17, EXT2-19]
    StepperTriggerPin = MosfetTargetPins[0] # = 3 = Bed
    StepperMonitorPin = MosfetControllerPins[0] # = 44 = MX1-5

    # [Analog-EXT-8, Analog-EXT-6, Analog-EXT-5, Analog-EXT-4, Analog-EXT-3]
    VRefPins = [8, 6, 5, 4, 3]
    AxisNames = ["X","Y","Z","E0","E1"]

    # [T0, T1, T2, T3]
    ThermistorPins = [0, 1, 2, 7];
    ThermistorNames = ["T0","T1","T2","T3"]

    # [T3, T2, T0]
    PowerRailPins = [7, 2, 0]
    PowerRailNames = ["Extruder rail", "Bed rail", "5V rail"]

    # Bed on controller
    PowerPin = 3


class RAMBoException(Exception):
    pass

class RAMBoContext(TestContext):
    """ The context object to be sent to every test case.
    The context will be used to communicate data to the test cases, such as
    the configuration used, the target/controller objects, store metadata from
    tests that can be used by other tests (such as the ConnectTarget test could
    fetch the serial number and store it in the context and it can be used by
    other test cases when writing to the log file), etc..
    """
    def __init__(self, config):
        TestContext.__init__(self, config)
        self.pinmapping = RAMBoPinMapping()

        self.controller_port = config.controller_port
        self.target_port = config.target_port

        if self.controller_port is None:
            self.controller_port = self.find_rambo_port(config.controller_snr)
        if self.controller_port is None:
            raise RAMBoException("Can't find controller board.")

        if not self.controller.open(port = self.controller_port):
            raise RAMBoException("Check controller connection.")

        self.controller.pinLow(self.pinmapping.PowerPin)

    def TestingStarted(self):
        TestContext.TestingStarted(self)
        self.target_port = self.config.target_port
        self.target = TestInterface()
        self.log("Powering target board...", self.LOG_LEVEL_INFO)
        if self.controller.pinHigh(self.pinmapping.PowerPin):
            time.sleep(self.config.powering_delay);

    def TestingEnded(self):
        TestContext.TestingEnded(self)
        self.log("Restarting test controller...", TestContext.LOG_LEVEL_INFO)
        self.controller.restart()
        self.controller.pinLow(self.pinmapping.PowerPin)

    def find_rambo_port(self, serial_number = None):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if "RAMBo" in port[1] or "VID:PID=27b1:0001" in port[2]:
                self.log("Found RAMBo board %s" % port[0], self.LOG_LEVEL_DEBUG)
                if serial_number is None:
                    return port[0]
                elif serial_number in port[2]:
                    self.log("Found port with correct serial : %s" % port[0],
                             self.LOG_LEVEL_DEBUG)
                    return port[0]
            else:
                self.log("Ignoring non-RAMBo board : %s" % port[0],
                         self.LOG_LEVEL_DEBUG)

    def find_target_port(self):
        ports = list(serial.tools.list_ports.comports())
        rambos = []
        for port in ports:
            if "RAMBo" in port[1] or "VID:PID=27b1:0001" in port[2]:
                ignore = False
                if port[0] == self.config.controller_port or \
                   port[2].endswith("SNR=%s" % self.config.controller_snr):
                    ignore = True
                if self.config.ignore_rambo_snr:
                    for snr in self.config.ignore_rambo_snr:
                        if port[2].endswith("SNR=%s" % snr):
                            self.log ("Ignoring this board : %s" % port[0],
                                      self.LOG_LEVEL_DEBUG)
                            ignore = True

                if ignore is False:
                    rambos.append(port[0])

        self.log("Found target boards : %s" % str(rambos), self.LOG_LEVEL_DEBUG)
        if len(rambos) != 1:
            return None
        return rambos[0]

    def find_serial_number(self, from_port):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if port[0] == from_port:
                snr = port[2].find("SNR=")
                if snr >= 0:
                    return port[2][snr+4:]
                break
        return None

class FindTarget(TestCase):
    def __init__(self, tester, avrdude):
        TestCase.__init__(self)
        self.tester = tester
        self.avrdude = avrdude
        self.fatal = True
        self.required = True
        self.hidden = True

    def name(self):
        return "Finding target"

    def _test(self, context):
        if self.tester.GetTest("Program M32U2 Bootloader").enabled or \
           self.tester.GetTest("Program M2560 Bootloader").enabled:
            time.sleep(5)

        if context.target_port is None:
            context.target_port = context.find_target_port()
        if context.target_port is None:
            context.log("Can't find target board.", TestContext.LOG_LEVEL_ERROR)
            self.error_string = "Connect failed"
            self.status = TestStatus.FAILED
        else:
            self.avrdude.port = context.target_port
            self.status = TestStatus.SUCCESS
            self.error_string = None


    def _verify(self, context):
        pass


class ConnectTarget(TestCase):
    def __init__(self):
        TestCase.__init__(self)
        self.fatal = True
        self.required = True

    def name(self):
        return "Connecting to target"

    def _test(self, context):
        if context.target.open(port = context.target_port):
            self.status = TestStatus.SUCCESS
            self.error_string = None
        else:
            self.error_string = "Connect failed"
            self.status = TestStatus.FAILED


    def _verify(self, context):
        pass

class DisconnectTarget(TestCase):
    def __init__(self):
        TestCase.__init__(self)
        self._finally = True
        self.required = True

    def name(self):
        return "Disconnecting target"

    def _test(self, context):
        if context.target.serial.isOpen():
            context.target.close()
        self.status = TestStatus.SUCCESS
        self.error_string = None
        time.sleep(1)

    def _verify(self, context):
        pass

if __name__ == "__main__":
    import config.configuration as configuration
    r = RAMBoTester(configuration)
    r.GetTest("Program M32U2 Bootloader").enabled = False
    r.GetTest("Program M2560 Bootloader").enabled = False
    r.GetTest("Program Vendor Firmware").enabled = False
    r.Run()
