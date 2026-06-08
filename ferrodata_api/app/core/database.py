import duckdb
from config import settings


class Database:
    def __init__(self):
        self.connection = duckdb.connect(settings.db_path)

    def execute(self, query):
        return self.connection.execute(query)

    def fetchall(self, query):
        return self.connection.execute(query).fetchall()

    def fetchone(self, query):
        return self.connection.execute(query).fetchone()

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    db = Database()
    query = """
    SELECT * FROM ferrodata.raw_sncf.gares LIMIT 5
    """
    print(db.fetchall(query))