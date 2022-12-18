import os
import sqlite3

class DB:
    def __init__(self, db_file='db.sqlite3', tables={'usernames': 't_username TEXT PRIMARY KEY, m_username TEXT', 'queue': 't_username TEXT PRIMARY KEY, tweet_id INTEGER, timestamp INTEGER'}):
        self.database = sqlite3.connect(f"{os.path.dirname(os.path.realpath(__file__))}/{db_file}")
        self.cursor = self.database.cursor()
        for table, structure in tables.items():
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table}({structure})')

    def select(self, sql):
        """Returns a list of dicts from DB."""
        self.database.row_factory = sqlite3.Row
        things = self.database.execute(sql).fetchall()
        unpacked = [{k: item[k] for k in item.keys()} for item in things]
        return unpacked

    def commit(self, sql):
        """ Inserts from a query. """
        self.cursor.execute(sql)
        self.database.commit()

        