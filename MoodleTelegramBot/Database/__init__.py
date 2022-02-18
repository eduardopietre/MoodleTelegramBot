import sqlite3


class DatabaseConnection:
    def __init__(self, file: str):
        self.file = file
        self.conn = None

    def __enter__(self) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.file)
        return self.conn.cursor()

    def __exit__(self, type_, value, traceback):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    @classmethod
    def exists_database_table(cls, cursor: sqlite3.Cursor, table: str) -> bool:
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table,))
        return cursor.fetchone()[0] == 1