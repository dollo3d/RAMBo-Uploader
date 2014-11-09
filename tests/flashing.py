from TestCase import *

class ProgramFirmware(TestCase):
    def __init__(self, avrdude, image, timeout = 15, name = None):
        TestCase.__init__(self)
        self.avrdude = avrdude
        self.image = image
        self.timeout = timeout
        self._name = name

    def name(self):
        return self._name if self._name else "Program Firmware"

    def _test(self, context):
        if self.avrdude.upload(self.image, self.timeout):
            self.status = TestStatus.SUCCESS
            self.error_string = None
        else:
            self.error_string = "Upload failed"
            self.status = TestStatus.FAILED
        self.results = [self.avrdude.stdout, self.avrdude.stderr]

    # Will never be called
    def _verify(self, context):
        pass

