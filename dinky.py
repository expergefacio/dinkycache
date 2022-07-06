# -*- coding:utf-8 -*-
import json
import sqlite3
from time import time
from hashlib import sha256
from lzstring import LZString


# dinkycashe
# version 0.1


class Dinky:
    def __init__(self, dbfile: str = "dinkycache.db", ttl: int = 2160):
        self.lz = LZString()
        self.now = int(time())
        self.dbfile = dbfile
        self.ttl_millis = ttl * (60 * 60)
        self.expires = self.ttl_millis + self.now if ttl else 0
        self.garbage_timer = 24 #hours
        self.garbage_iterations = 100

        with self._SQLite(self.dbfile) as cur:
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS 'dinkycache' "
                f"('id' text primary key, 'data' text, 'expiry' int)"
            )

        self._expiry_garbage_collector()


    def read(self, id: str = False):
        result = False
        if not id:
            raise Exception("Dinkyread: id must be supplied 🤯")

        hashed = sha256(id.encode("utf-8")).hexdigest()
        with self._SQLite(self.dbfile) as cur:
            dbdata = cur.execute(
                f"SELECT * FROM dinkycache WHERE id = '{hashed}'"
            ).fetchone()
        if dbdata is not None:
            expiry = dbdata["expiry"]
            if (expiry - self.now) > 0 or (expiry == 0):
                result_str = self.lz.decompressFromBase64(dbdata["data"])
                result = json.loads(result_str)

        return result




    def write(self, id: str = False, data: str = False):
        result = False
        if not id or not data:
            raise Exception("Dinkywrite: id and data must be supplied 🤯")

        result = hashed = sha256(id.encode("utf-8")).hexdigest()
        str_data = json.dumps(data)
        compressed = self.lz.compressToBase64(str_data)

        with self._SQLite(self.dbfile) as cur:
            cached = cur.execute(
                f"SELECT COUNT() FROM dinkycache WHERE id = '{hashed}'"
            ).fetchone()[0]
            if cached > 0:
                cur.execute(
                    f"UPDATE dinkycache "
                    f"SET data = '{compressed}', "
                    f"expiry = '{self.expires}' "
                    f"WHERE id = '{hashed}'"
                )
            else:
                cur.execute(
                    f"INSERT INTO dinkycache "
                    f"VALUES ('{hashed}', '{compressed}', '{self.expires}')"
                )
        return result



    def _expiry_garbage_collector(self):
        """Internal method to clear expired cache entries"""
        binday = self.garbage_timer * 60 * 60
        iterations = None
        timestamp = None

        with self._SQLite('.__dinky__') as cur:
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS 'binman' "
                f"('id' int primary key, 'writes' int, 'timestamp' int);"
            )
            cur.execute(
                f"INSERT OR IGNORE INTO binman VALUES (1, 0, 0);"
            )
            iterations, timestamp = cur.execute(
                f"SELECT writes, timestamp FROM binman WHERE id = 1"
            ).fetchone()

        if (self.now - timestamp > binday) or iterations > self.garbage_iterations:
            with self._SQLite(self.dbfile) as cur:
                cur.execute(
                    f"DELETE FROM dinkycache "
                    f"WHERE expiry != 0 AND expiry < {self.now}"
                )
            with self._SQLite('.__dinky__') as cur:
                cur.execute(
                    f"UPDATE binman "
                    f"SET writes = 0, timestamp = '{self.now}' "
                    f"WHERE id = 1"
                )
        else:
            with self._SQLite('.__dinky__') as cur:
                cur.execute(
                    f"UPDATE binman "
                    f"SET writes = {iterations + 1} "
                    f"WHERE id = 1"
                )


    class _SQLite:
        def __init__(self, dbfile):
            self.file = dbfile

        def __enter__(self):
            self.conn = sqlite3.connect(self.file)
            self.conn.row_factory = sqlite3.Row
            return self.conn.cursor()

        def __exit__(self, type, value, traceback):
            self.conn.commit()
            self.conn.close()
