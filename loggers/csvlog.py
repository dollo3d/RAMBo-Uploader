import time
import json
from tests.TestCase import TestStatus

class CSVLogger():
    def __init__(self, path):
        self.path = path
        self.fd = None
        self.print_header = False

    def open(self):
        if self.fd is None:
            self.fd = open(self.path, 'a')
            if self.fd.tell() == 0:
                self.print_header = True
            else:
                self.print_header = False

    def isOpen(self):
        return self.fd is not None

    def close(self):
        if self.fd:
            self.fd.close()
            self.fd = None

    def post(self, start, end, tests, results):
        was_open = self.isOpen()
        self.open()

        if self.print_header:
            self.fd.write("Serial,Start time,End time,Overall result,")
            self.fd.write("Program M32U2 BL,Program M2560 BL,Finding target,Program Test FW,Connect,")
            self.fd.write("Supply Voltages,Mosfets High,Mosfets Low,")
            self.fd.write("Endstops High,Endstops Low,I2C Low,I2C High,SPI Low,SPI High,")
            self.fd.write("Thermistors,Stepper's VRef,Motors Full Step,Motors Half Step,")
            self.fd.write("Motors 1/4 Step,Motors 1/16 Step,Program Vendor Firmware\n")

        start_time = time.ctime(time.mktime(start))
        end_time = time.ctime(time.mktime(end))
        try:
            serial = results['Finding target RAMBo board']['results'][1]
        except:
            serial = "?????"
        all_tests =["Program M32U2 Bootloader",
                    "Program M2560 Bootloader",
                    "Finding target RAMBo board",
                    "Program Test Firmware",
                    "Connecting to target",
                    "Supply Voltages",
                    "Mosfets High",
                    "Mosfets Low",
                    "Endstops High",
                    "Endstops Low",
                    "I2C Low",
                    "I2C High",
                    "SPI Low",
                    "SPI High",
                    "Thermistors",
                    "Stepper's Voltage reference",
                    "Motors Full Step",
                    "Motors Half Step",
                    "Motors 1/4 Step",
                    "Motors 1/16 Step",
                    "Program Vendor Firmware"]
        overall_result = "Success"
        for test in all_tests:
            try:
                if results[test]['status'] == TestStatus.FAILED:
                    overall_result = "Failed"
            except:
                pass

        self.fd.write("%s,%s,%s,%s," % (serial, start_time,
                                            end_time, overall_result))
        for test in all_tests:
            try:
                status = TestStatus.ToName(results[test]['status'])
                if status == "Failed":
                    status = "\"" + results[test]['error'] + "\""
                self.fd.write(status)
            except:
                pass
            finally:
                self.fd.write(",")
        self.fd.write("\n")

        self.fd.flush()
        if not was_open:
            self.close()
