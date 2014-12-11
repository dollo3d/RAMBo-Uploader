import time
import json
from tests.TestCase import TestStatus

class MultiLogger():
    def __init__(self, loggers):
        self.loggers = loggers

    def open(self):
        for logger in self.loggers:
            logger.open()

    def isOpen(self):
        for logger in self.loggers:
            if not logger.isOpen():
                return False
        return True

    def close(self):
        for logger in self.loggers:
            logger.close()

    def post(self, start, end, tests, results):
        for logger in self.loggers:
            logger.post(start, end, tests, results)
