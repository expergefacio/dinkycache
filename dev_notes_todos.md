# changelog
Intended for display in vscode, not as document 😅

## TODO to complete version 0.1
⏺ Look over code  
⏺ Run tests  
⏺ Make sure readme is on spot  
⏺ Test if _expiry_garbage_collector() actually need its own db-file  
        or could it use the default file with its own table or  
        would that affect performance if dafault file gets large  
⏺ Consider adding option to use as common OOP:  
```python
d = Dinky()
d.setTTT(24)
d.setFile("db.db")
d.id = "something"
d.data = {"what": "ever"}
d.write()
```
⏺ Create package for Pypi 😁  

## From version Null -> 0.1 (unfinished)

### 🔴 CHANGE: Timstamp changes to "valid until" model

ttl bygges om til å kunne settes i write funksjon, som timestamp frem i tid  
❗️ TTL passed to `init` for now, might make sense to move  
✅ default value?  
✅ value 0 som no-expiration?  
~~ bruke pytimeparse2 ?~~  
ttl sjekkes ved read (eller __init__?), ~~hente 5 rader sortert etter ttl med lavest verdi over 0?~~  
                                        `DELETE FROM dinkycache WHERE timestamp != 0 AND timestamp < {self.now}`  
✅ slette hvis de er utgått  
✅ ytelsepåvirkning?  
        -> runs a cleanup on every 100 `init` or if 24 hrs since last cleanup  
        -> cleanup function called: `self._expiry_garbage_collector()`  

### 🔴 CHANGE: RAISE replaces PRINT+ELSE
Check for supplied arguments now raises `Exeption` instead of `print()`
`raise` keyword stops execution similar to return
therefore else is not neded after `raise`, i.e. if/else are now guard clauses

### 🔴 CHANGE: 

file, self.db, self.file, dbfile
are now in most places either dbfile or self.dbfile
exept in _SQLite where self.file makes sense as it is

### 🔴 CHANGE:
Rename dcache.py to dinky.py

### 🔴 CHANGE:
Some improvements to SQL Queries

### 🔵 NEW: GARBAGE COLLECTOR

Cleanup function called: `self._expiry_garbage_collector()`

### 🔵 NEW: VERSION NUMBERING
To track changes and fixes

### 🔵 NEW: ARGUMENTS TO `__INIT__`

Added:
`ttl: int = 2160`
to
`def __init__(self, dbfile: str = "dinkycache.db", ttl: int = 2160):`
Which might seem counter intuitive, but would allow for this usage case:

```python
s = ['preferred.db', 24]
Dinky(*s).read(id)
Dinky(*s).write(id, results)

#OR

s = {
    'dbfile' = 'preferred.db',
    'ttl' = 24,
}
Dinky(**s).read(id)
Dinky(**s).write(id, results)
```


### 🔵 NEW: TESTFILE
Included in repo my slap bang testfile sturctured like so:

```python
def run():
        #where to run the test functions
        test()

#test function declarations
def test():
        #test code
        pass

run()
```