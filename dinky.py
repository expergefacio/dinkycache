# -*- coding:utf-8 -*-
import json
import sqlite3
from time import time
from hashlib import sha256
from lzstring import LZString

# dinkycache
# version 0.2

class Dinky:
    def __init__(
            self, 
            dbfile: str = "dinkycache.db", 
            ttl: int = 2160,
            garbage_collection: int = 24,
            garbage_iterations: int = 100,
            ignore_garbage_colletion: bool = False
        ):
        self.lz = LZString()
        self.now = int(time())
        self.setTTL(ttl)
        self.dbfile = dbfile
        self.garbage_timer = garbage_collection
        self.gb_iterations = garbage_iterations
        self.id = None
        self.data = None

        with self._SQLite(self.dbfile) as cur:
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS 'dinkycache' "
                f"('id' text primary key, 'data' text, 'expiry' int)"
            )

        if ignore_garbage_colletion is False:
            self._expiry_garbage_collector()

    def read(self, id: str = False):
        self.result = False
        if not self.id:
            if not id:
                raise Exception("Dinkyread: ID must be supplied 🤯")
            self.id = id

        hashed = sha256(self.id.encode("utf-8")).hexdigest()
        with self._SQLite(self.dbfile) as cur:
            dbdata = cur.execute(
                f"SELECT * FROM dinkycache WHERE id = '{hashed}'"
            ).fetchone()
        if dbdata is not None:
            expiry = dbdata["expiry"]
            if (expiry - self.now) > 0 or (expiry == 0):
                result_str = self.lz.decompressFromBase64(dbdata["data"])
                self.result = json.loads(result_str)

        return self.result

    def write(self, id: str = False, data: str = False):
        self.result = False
        if not self.id or not self.data:
            if not id or not data:
                raise Exception("Dinkywrite: ID and DATA must be supplied 🤯")
            self.id, self.data = id, data

        self.result = hashed = sha256(self.id.encode("utf-8")).hexdigest()
        str_data = json.dumps(self.data)
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
        return self.result
    
    def setTTL(self, ttl: int = 2160):
        self.ttl_millis = ttl * (60 * 60)
        self.expires = self.ttl_millis + self.now if ttl else 0

    def _expiry_garbage_collector(self):
        """Internal method to clear expired cache entries"""
        binday = self.garbage_timer * 60 * 60
        iterations = None
        timestamp = None

        with self._SQLite(self.dbfile) as cur:
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

        if (self.now - timestamp > binday) or iterations > self.gb_iterations:
            with self._SQLite(self.dbfile) as cur:
                cur.execute(
                    f"DELETE FROM dinkycache "
                    f"WHERE expiry != 0 AND expiry < {self.now}"
                )
            with self._SQLite(self.dbfile) as cur:
                cur.execute(
                    f"UPDATE binman "
                    f"SET writes = 0, timestamp = '{self.now}' "
                    f"WHERE id = 1"
                )
        else:
            with self._SQLite(self.dbfile) as cur:
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