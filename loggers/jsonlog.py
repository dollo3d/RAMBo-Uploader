import time
import json

class JsonLogger():
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
        self.fd.write(json.dumps({"start_time": time.mktime(start), "end_time": time.mktime(end),
                                  "results": results}) + "\n")
        self.fd.flush()
        if not was_open:
            self.close()
