# -*- coding:utf-8 -*-
import json
import sqlite3
from time import time
from hashlib import sha256
from lzstring import LZString


class Dinky:
    def __init__(self, dbfile: str = "dinkycache.db"):
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
        expired = []
        with self._SQLite(self.db) as cur:
            rows = cur.execute(
                f"SELECT id, timestamp FROM 'dinkycache'"
                f"WHERE timestamp > 0 ORDER BY timestamp ASC LIMIT 3"
            )
            for row in rows:
                now = int(time())
                print(
                    f"init: timestamp {row['timestamp']} expires in {row['timestamp'] - now}"
                )
                if now > row["timestamp"]:
                    expired.append(row["id"])
        for item in expired:
            self.delete(hash=item)

    def read(self, id: str):
        result = False
        hashed = sha256(id.encode("utf-8")).hexdigest()
        with self._SQLite(self.db) as cur:
            dbdata = cur.execute(
                f"SELECT id, data, timestamp FROM dinkycache WHERE id = '{hashed}'"
            ).fetchone()
        if dbdata is not None:
            now = int(time())
            timestamp = int(dbdata["timestamp"])
            if now < timestamp:
                result_str = self.lz.decompressFromBase64(dbdata["data"])
                result = json.loads(result_str)
            else:
                self.delete(id)
        return result

    def write(self, id: str, data: str, ttl: int = 172800):  # 48hours ttl
        result = hashed = sha256(id.encode("utf-8")).hexdigest()
        if ttl:
            timestamp = int(time()) + int(ttl)
        else:
            timestamp = 0
        str_data = json.dumps(data)
        compressed = self.lz.compressToBase64(str_data)
        with self._SQLite(self.db) as cur:
            cached = cur.execute(
                f"SELECT COUNT() FROM dinkycache WHERE id = '{hashed}'"
            ).fetchone()[0]
            if cached > 0:
                cur.execute(
                    f"UPDATE dinkycache "
                    f"SET data = '{compressed}', timestamp = '{timestamp}' "
                    f"WHERE id = '{hashed}'"
                )
            else:
                cur.execute(
                    f"INSERT INTO dinkycache VALUES "
                    f"('{hashed}', '{compressed}', '{timestamp}')"
                )
        return result

    def delete(self, id: str = False, hash: str = False):
        if id:
            hashed = sha256(id.encode("utf-8")).hexdigest()
        elif hash:
            hashed = hash
        else:
            raise TypeError("delete() missing 1 required argument: 'id' or 'hash'")
        with self._SQLite(self.db) as cur:
            cur.execute(f"DELETE FROM dinkycache WHERE id = '{hashed}'")
        return True

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
