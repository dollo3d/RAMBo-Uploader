import time
from tests.TestCase import TestStatus

class TextLogger():
    def __init__(self, path):
        self.path = path
        self.fd = None

    def open(self):
        if self.fd is None:
            self.fd = open(self.path, 'a')

    def isOpen(self):
        return self.fd is not None

    def close(self):
        if self.fd:
            self.fd.close()
            self.fd = None

    def post(self, start, end, tests, results):
        was_open = self.isOpen()
        self.open()
        self.fd.write("************ Started testing %s ****************\n" % \
                      (time.strftime("%Y-%m-%d %H:%M:%S", start)))
        for test in tests:
            # Do not print disabled or canceled tests
            if test.status == TestStatus.SUCCESS or test.status == TestStatus.FAILED:
                self.fd.write("%s (%s) : %s\n" % (test.name(),
                                                  ("%s (%s)" % (test.error_string, TestStatus.ToName(test.status))) \
                                                  if test.error_string else TestStatus.ToName(test.status),
                                                  test.results))
        self.fd.write("------------ Ended testing %s  -----------------\n\n" % \
                      (time.strftime("%Y-%m-%d %H:%M:%S", end)))
        self.fd.flush()
        if not was_open:
            self.close()
