import psycopg2

class PostgresDatabase():
    def __init__(self, host, name, user, password):
        self.info = "dbname='%s' user='%s' host='%s' password='%s'" % \
                    (name, user, host, password)
        self.storage = None

    def open(self):
        if not self.isOpen():
            self.storage = psycopg2.connect(self.info)
            if self.storage is None:
                raise Exception("Could not open database")

    def isOpen(self):
        return self.storage is not None

    def close(self):
        if self.storage:
            self.storage.close()
            self.storage = None

    def post(self, start, end, tests, results):
        was_open = self.isOpen()
        self.open()
        cursor = self.storage.cursor()
        # TODO: Define database format and insert results values (dict of dicts)
        #cursor.execute("""INSERT INTO testdata(serial, timestamp, testresults, testversion, testdetails) VALUES (%s, %s, %s, %s, %s)""", (serial, 'now', results, version, details))
        self.storage.commit()
        if not was_open:
            self.close()
