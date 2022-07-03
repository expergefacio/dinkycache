import sqlite3
import time
import json
import lzstring


class Dinky:
    id = None
    data = None
    timestamp = None
    days = 90 * (60 * 60 * 24)

    def __init__(self):
        pass

    def read(self, id:str = None):
        lz = lzstring.LZString()
        con = sqlite3.connect('dinkycache.db')
        cur = con.cursor()
        now = int(time.time())

        #region init table
        count = cur.execute(
            f"SELECT count(name) "
            f"FROM sqlite_master "
            f"WHERE type='table' "
            f"AND name='dinkycache'"
        ).fetchone()[0]
        if (count == 0):
            cur.execute(
                f"CREATE TABLE 'dinkycache' "
                f"('id' text, 'data' text, 'timestamp' int, "
                f"PRIMARY KEY('id'))"
            )
        #endregion init table


        if id == None:
            con.close()
            return False

        for char in id:
            if not char.isalnum():
                print(f"Privided id '{id}' contains "
                      f"non alphanumeric chars")
                con.close()
                return False

        compressed = cur.execute(
            "SELECT * FROM dinkycache "
            "WHERE id = '%s'"
            % id
        ).fetchone()

        if compressed == None:
            con.close()
            return False

        # check ttl
        ttl = compressed[2]
        if ((now - ttl) > self.days):
            con.close()
            return False

        result_str = lz.decompressFromBase64(compressed[1])
        result = json.loads(result_str)

        con.commit()
        con.close()
        return result


    def write(self, id:str = None, data:str = None):
        if id == None or data == None:
            print("Id and data must be supplied")
            return False

        for char in id:
            if not char.isalnum():
                print(f"Privided id '{id}' contains "
                      f"non alphanumeric chars")
                return False

        con = sqlite3.connect('dinkycache.db')
        cur = con.cursor()
        lz = lzstring.LZString()
        now = int(time.time())


        #region init table
        count = cur.execute(
            f"SELECT count(name) "
            f"FROM sqlite_master "
            f"WHERE type='table' "
            f"AND name='dinkycache'"
        ).fetchone()[0]
        if (count == 0):
            cur.execute(
                f"CREATE TABLE 'dinkycache' "
                f"('id' text, 'data' text, 'timestamp' int, "
                f"PRIMARY KEY('id'))"
            )
        #endregion init table


        str_data = json.dumps(data)
        compressed = lz.compressToBase64(str_data)

        #If exists and outdated, then update
        cached = cur.execute(
            "SELECT COUNT() FROM dinkycache "
            "WHERE id = '%s'"
            % id
        ).fetchone()[0]

        if (cached > 0):
            cur.execute(
                f"UPDATE dinkycache "
                f"SET data = '{compressed}', timestamp = {now} "
                f"WHERE id = {id}"
            )
            con.commit()
            con.close()
            return True

        #If dont exist, then make entry
        cur.execute(
            f"INSERT INTO dinkycache "
            f"VALUES ({id}, '{compressed}', {now})"
        )
        con.commit()
        con.close()