# -*- coding:utf-8 -*-
import json
import sqlite3
from time import time
from hashlib import sha256
from lzstring import LZString

# dinkycache
# version 0.4

class Dinky:
    def __init__(
            self, 
            dbfile: str = "dinkycache.db", 
            ttl: int = 2160,
            purge_rows: bool = True,
            row_limit: int = 5000,
            clean_expired: bool = True,
            clean_hrs: int = 24,
            clean_iterations: int = 100,
        ):
        """
        - Handles settings on init
        - Checks wheter the database exists, creates it if not
        - Purges overflowing rows
        - Checks for and deletes expired entries
        Args:
            dbfile (str, optional):  The name (and path) of sqlite3 database.
                                     Defaults to 'dinkycache.db'
            ttl (integer, optional): Time to live in hours
                                     Defaults to 2160 hrs / 90 days
            purge_rows (bools, optional):    Clear overflowing rows if True
                                             Defaults True
            row_limit (int, optional):       Maximum number of rows
                                             Defaults 5000
            clean_expired (bools, optional): Clean expired entries if True
                                             Defaults True
            clean_hrs (int, optional):       Clean on invocation if
                                             set hours since last clean
                                             Defaults 24
            clean_iterations: int = 100,     Clean on invocation if
                                             if > 'clean_iterations'
                                             since last clean
                                             Defaults 100
        """
        self.lz = LZString()
        self.now = int(time())
        self.setTTL(ttl)
        self.dbfile = dbfile
        self.clean_expired = clean_expired
        self.clean_hrs = clean_hrs
        self.clean_iterations = clean_iterations
        self.purge_rows = purge_rows
        self.row_limit = row_limit
        self.id = None
        self.data = None

        with self._SQLite(self.dbfile) as cur:
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS 'dinkycache' "
                f"('id' text primary key, 'data' text, "
                f"'expiry' int, 'created' int)"
            )


    def read(self, id: str = False):
        """
        Does a lookup in the database
        Args:
            id (str): The id to look for in the database
        Returns:
            The value at the corresponding id if it exists and is not expired,
            False otherwise.
        """
        self.result = False
        if not self.id:
            if not id:
                raise Exception("Dinky.read(): ID must be supplied 🤯")
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

    def write(self, id: str = False, data: str = False, ttl: int = False):
        """
        Writes a row to the database
        Args:
            id (str): The id to store the data under
            data (str): The value to store
            ttl (int, optional): Time to live for the data, specified in hours.
                Set to 0 for permanent storage. Defaults to 2160 hours / 90 days.
        Returns:
            Hash of the stored id, False otherwise.
        """
        self.result = False
        if isinstance(ttl, int):
            self.setTTL(ttl)
        if not self.id or not self.data:
            if not id or not data:
                raise Exception("Dinky.write(): ID and DATA must be supplied 🤯")
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
                    f"expiry = '{self.expires}', "
                    f"created = '{self.now}' "
                    f"WHERE id = '{hashed}'"
                )
            else:
                cur.execute(
                    f"INSERT INTO dinkycache "
                    f"VALUES ('{hashed}', '{compressed}', "
                    f"'{self.expires}', '{self.now}')"
                )
        
        if self.purge_rows:
            self._purgerows()

        if self.clean_expired:
            self._clean_expired()

        return self.result

    def delete(self, id: str = False, hash: str = False):
        """
        Deletes a row in the database, specified by either id or hash
        Args:
            id (str, optional):  The id of the row to delete, defaults to False
            hash (str, optional): The hash of the row to delete, defaults to False
        Returns:
            True
        Raises:
            Exeption: If neither id nor hash is specified
        """
        if not self.id:
            if not id and not hash:
                raise Exception("Dinky.delete() missing 1 required argument: 'id' or 'hash'")

            self.id = hash if hash else self._hash(id)
            
        with self._SQLite(self.db) as cur:
            cur.execute(f"DELETE FROM dinkycache WHERE id = '{self.id}'")
        return True
    
    def setTTL(self, ttl: int = 2160):
        """
        Public method:
        Sets Time To Live in hours
        Args:
            ttl (int): Default 2160 hours
        """
        self.ttl_millis = ttl * (60 * 60)
        self.expires = self.ttl_millis + self.now if ttl else 0
    
    def _hash(self, id):
        """Returns hash of id"""
        return sha256(id.encode("utf-8")).hexdigest()
    
    def _purgerows(self):
        """Internal method to clear overflowing rows"""
        with self._SQLite(self.dbfile) as cur:
            #count to save sorting if row_limit not met
            count = cur.execute(
                f"SELECT COUNT(*) FROM dinkycache"
            ).fetchone()[0]
            if count > self.row_limit:
                cur.execute(
                    f"DELETE FROM dinkycache WHERE id IN "
                    f"(SELECT id FROM dinkycache "
                    f"ORDER BY created DESC LIMIT -1 "
                    f"OFFSET {self.row_limit})"
                )


    def _clean_expired(self):
        """Private method: Clears expired cache entries"""
        binday = self.clean_hrs * 60 * 60
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

        if (self.now - timestamp > binday or
            iterations > self.clean_iterations):
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
    
    def _dev_runSQL(self, sql):
        """Runs SQL in contexts for testing"""
        with self._SQLite(self.dbfile) as cur:
            return cur.execute(sql).fetchall()


    class _SQLite:
        """Private method: SQLite context manager"""
        def __init__(self, dbfile):
            self.file = dbfile
        def __enter__(self):
            self.conn = sqlite3.connect(self.file)
            self.conn.row_factory = sqlite3.Row
            return self.conn.cursor()
        def __exit__(self, type, value, traceback):
            self.conn.commit()
            self.conn.close()