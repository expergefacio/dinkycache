# changelog
Intended for display in vscode, not as document 😅

## Todo

✅ Consider default options/settings  
✅ Create package for Pypi 😁  
✅ Look over code  
✅ Change .write to 'INSERT OR REPLACE'  
✅ Make sure readme is on spot  
✅ Docstrings?
✅ Added delete()
        Used Expeption instead of TypeError, not sure if thats correct tho
        however we are checing if argument is supplied, not type of the argument supplied?
✅ Added _hash() to wrap the string sha256(id.encode("utf-8")).hexdigest()
✅ Added _purgerows() and row_limit
✅ Added field 'created' in db so oldest can be cleared
✅ Custom TTL  
✅ Test if _expiry_garbage_collector() actually need its own db-file  
        or could it use the default file with its own table or  
        would that affect performance if dafault file gets large  
✅ Added support for common OOP usecase
✅ TTL default 2160 hrs (90days)


##  1.0.3
ttl now float for half hr like ttl = 0.5 or ttl = 30 / 60, or 30 seconds as ttl = 30 / 3600

## Moved to version nr 1.0.1 as uploaded to pypi

## From version 0.4 -> 0.5
    added row_overflow
    cleaned up code and testes SQL
    fixed: .delete() returns True without checking


## From version 0.3 -> 0.4
Added delete()
        Used Expeption instead of TypeError, not sure if thats correct tho
        however we are checing if argument is supplied, not type of the argument supplied?
Added _hash() to wrap the string sha256(id.encode("utf-8")).hexdigest()
Added some docstring


## From version 0.2 (unfinished) -> 0.3
### 🔵 NEW: added _purgelines and max_rows ets
### 🔴 CHANGE: some argument and propertie names changed

## From version 0.1 (unfinished) -> 0.2 (time to get the bugs out)
### 🔴 CHANGE: everything uses self.variable
To allow for this sort of usercase
Write
```python
    d = Dinky()
    d.id = "test"
    d.data = {"whatever": "floats"}
    d.setTTL(24) #hr
    d.write()

    print(d.data)
```
Read:
```python
    d = Dinky(ignore_garbage_colletion = true)
    d.id = "test
    print(D.read())
```
### 🔵 NEW: Added .setTTL() for more non defacto use cases

### 🔵 NEW: Added more config to __init__:
```python
    dbfile: str = "dinkycache.db", 
    ttl: int = 2160,
    garbage_collection: int = 24,
    garbage_iterations: int = 100,
    ignore_garbage_colletion: bool = False
```


## testing:
testing DB:
38.1mb: 100k writes str_len 40~1500: avg 11.3ms (incl generation)

10k reads 10.6 ms avg
10k reads no ui: 6.57 ms avg 

test:
.db-file segregation for garbage collection
5k reads and garbage_iterations set to 2,
6.4673496099999990 avg without segregation
6.3988324038000005 avg with segregation



## no testing for edge cases:


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