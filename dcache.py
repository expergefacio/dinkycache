# -*- coding:utf-8 -*-
import json
import sqlite3
from time import time
from hashlib import sha256
from lzstring import LZString


class Dinky:
    def __init__(self, dbfile: str = "dinkycache.db"):
        self.days = 90 * (60 * 60 * 24)
        self.lz = LZString()
        self.db = dbfile

        with self._SQLite(self.db) as cur:
            count = cur.execute(
                f"SELECT count(name) "
                f"FROM sqlite_master "
                f"WHERE type='table' "
                f"AND name='dinkycache'"
            ).fetchone()[0]
            if count == 0:
                cur.execute(
                    f"CREATE TABLE 'dinkycache' "
                    f"('id' text, 'data' text, 'timestamp' int, "
                    f"PRIMARY KEY('id'))"
                )

    def read(self, id: str = False):
        result = False
        if not id:
            print("Dinkyread: id must be supplied")
        else:
            hashed = sha256(id.encode("utf-8")).hexdigest()
            now = int(time())
            with self._SQLite(self.db) as cur:
                dbdata = cur.execute(
                    f"SELECT id, data, timestamp FROM dinkycache WHERE id = '{hashed}'"
                ).fetchone()
            if dbdata is not None:
                ttl = dbdata["timestamp"]
                if (now - ttl) < self.days:
                    result_str = self.lz.decompressFromBase64(dbdata["data"])
                    result = json.loads(result_str)
        return result

    def write(self, id: str = False, data: str = False):
        result = False
        if not id or not data:
            print("Dinkywrite: id and data must be supplied")
        else:
            result = hashed = sha256(id.encode("utf-8")).hexdigest()
            now = int(time())
            str_data = json.dumps(data)
            compressed = self.lz.compressToBase64(str_data)
            with self._SQLite(self.db) as cur:
                cached = cur.execute(
                    f"SELECT COUNT() FROM dinkycache WHERE id = '{hashed}'"
                ).fetchone()[0]
                if cached > 0:
                    cur.execute(
                        f"UPDATE dinkycache "
                        f"SET data = '{compressed}', timestamp = '{now}' "
                        f"WHERE id = '{hashed}'"
                    )
                else:
                    cur.execute(
                        f"INSERT INTO dinkycache VALUES "
                        f"('{hashed}', '{compressed}', '{now}')"
                    )
        return result

    class _SQLite:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            self.conn = sqlite3.connect(self.file)
            self.conn.row_factory = sqlite3.Row
            return self.conn.cursor()

        def __exit__(self, type, value, traceback):
            self.conn.commit()
            self.conn.close()
