# dinkycache for python projects
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A very small and flexible name/value cache for python. 

Intended for quick set up, in development and small scale projects.

Uses `sqlite` for storage and `lzstring` for compression.

Stores any data that can be parsed in to a string with `json.dumps()` and `json.loads()`  
Returns `int`, `dict` and `str` just fine, but returns a `list` if supplied a `tuple`

## Dependencies
```python
pip install lzstring==1.0.4
```

## How to use
Download the dcache.py file to your project folder and import
```python
from dinky import Dinky
```

Has 3 main methods called like so:
```python
Dinky().read(str: id)
Dinky().write(str: id, str:data, int:ttl)
Dinky().delete(str: id) -> int
```

## Examples with default settings
```python
from dcache import Dinky

#gets data from some slow source
def fetch_data(id):
    return "some data"

id = "001"

```
Then where you would normaly write:
```python
results = fetch_data(id)
```
Write these two lines instead:
```python
if (result := Dinky().read(id) == False):
    Dinky().write(id, result := fetch_data(id))
```
If you are running Python < 3.8 or just don't like [walruses](https://peps.python.org/pep-0572/):
```python
results = Dinky().read(id)
if results == False:
    results = fetch_data(id)
    Dinky().write(id, results)
```
This is also an option, its there, fully supported, however not further documented:
```python
    #Write:
    d = Dinky()
    d.id = "test"
    d.data = {"whatever": "floats"}
    d.setTTL(24) #hr
    d.write()
    print(d.data)

    #Read:
    d = Dinky(clean_expired = False)
    d.id = "test
    print(results := d.read())
```

In either case `results` will contain the data from cache if its there and within the specified TTL. Or it will call your get_some_data() to try and fetch the data instead.

## Settings

Avaialble settings and default values
```python
    dbfile: str = "dinkycache.db",  # name of sqlite file
    ttl: int = 2160,                # time to live in hours, default 2160 = 90 days, 0 = no expiry
    purge_rows: bool = True,        # will enforce row_limit if true
    row_limit: int = 10000,         # maximum number of rows in db
    row_overflow: int = 1000,       # buffer zone above row_limit before anything is deleted
    clean_expired: bool = True,     # will delete outdated entries if true
    clean_hrs: int = 24,            # time between cleanups of expried entries
    clean_iterations: int = 100,    # iterations (reads/writes) between cleanups
```

Set them in one of the following ways
```python
# Positional arguments:
Dinky('preferred.db', 24).read(id)
```
OR
```python
# Keyword arguments:
Dinky(dbfile='preferred.db').read(id)
```
OR
```python
# Unpack list as positional arguments:
settings = ['preferred.db', 24]
Dinky(*settings).read(id)
```
OR
```python
# Unpack dict as keyword arguments:
settings = {
    'dbfile' = 'preferred.db',
    'ttl' = 24,
}
Dinky(**settings).read(id)
```

## Examples of use with user-defined settings

You can destruct a dict an pass it as settings each time you invoke `Dinky(**settings)`,
or do the same, but assign the new `Dinky object` to a `variable` and reuse it that way:

### Invoke on every use:
```python
settings = {
    'dbfile' = 'preferred.db',
    'purge_rows' = True,
    'clean_expired' = False,
    'row_limit' = 100,
    'ttl' = 0,
}

if (result := Dinky(**settings).read(id) == False):
    Dinky(**settings).write(id, result := fetch_data(id))

```

### Retain Dinky object:
```python
d = Dinky(
    dbfile = 'preferred.db',
    purge_rows = True,
    clean_expired = False,
    row_limit = 100,
    ttl = 0,
)

if (result := d.read(id) == False):
    d.write(id, result := fetch_data(id))
```

## clean_expired, clean_hrs and clean_iterations
If `clean_expired = True`, script will try to clean out expired entries every time data is **written** if one of the following conditions are met.  
It has been minimum `clean_hrs: int = 24` hours since last cleanup  
OR  
There have been more than `clean_iterations: int = 100` invocations since last cleanup  

The cleanup function comes at a 75% performance cost, so if it runs on every 100 write, that amounts to a 7.5% average performance cost.

`clean_expired` might therefore be a much better alternative than using `purge_rows` for larger amounts of data.

## purge_rows, row_limit and row_overflow
If `purge_rows = True`, script will try to clean out overflowing lines every time data is **written**.  
`row_limit = int` sets the maximum lines in the database.  
`row_overflow = int` how many lines over `row_limit` before `row_limit`is enforced

This comes at a great performance cost for larger databases. 462 ms to sort 100k rows on a 1.8 ghz Intel Core i5. For this reason `row_overflow` is added as a threshold as a buffer, so that deletion dont happen on every call to `.write`.

It is probably best used for small databases and/or databases with small entries.

## Public methods
### .read()
Arguments `id` (string, required)
Returns data corresponding to `id`, or False if there is no data
Can be called without arguments on existing object if id has alredy been set.
### .write()
Arguments `id` (string, required), `data` (string, required), `tll` (int, optional)
Stores the supplied `data` to that `id`, `tll` can be set here if not already passed on invocation
Returns the hashed `id` or False
Will do `clean_expired`and `purge_rows` if they are set True
Can be called without arguments on existing object if id and data has alredy been set.

### .delete()
Arguments `id` (string, required)
Deletes entry corresponding to that `id`
Returns number of rows deletet, `1` or `0`.
Can be called without arguments on existing object if id has alredy been set.

## Performance

This wont ever compete with Redis, MongoDB or anything like that. This is ment to be a small, easy solution for small scale use cases where you dont want or need any big dependencies. Hence performance will be less, but might still be orders of magnitude faster than repeatedly parsing the data from some website.

### Tests:

Reads from DB 1
```
10k entries of 40 to 1500 characters:

1 read = 0.018 to 0.003 sec
100 reads = 0.6 sec (0.006 avg)
```

Reads from DB 2
```
10k entries of 40 to 150000 characters:
1 read = 0.003 to 0.022 sec
100 reads = 1.1 to 2.4 sec (0.015 avg)
```

Test DB 3:
```
38.1mb: 100k writes str_len 40~1500: avg 11.3ms (incl generation)

10k reads: 6.57 ms avg 
```


## Security
Ids are hashed, so you may put anything in there
Data is compressed to a string of base 64 characters, so you may put anything in there.

Lzstring seem to have very high integrity, we have not been able to produce a test result where the input and output has not been equal.

That said, what you put in is what you'll get out. There is no checking for html-tags and such. Just something to bevare of if for some reason you'll use it to store and later display user provided data.


## Compression
Lzstring is not great for shorter strings, and does sometimes even increase to string lenght. However in testing we found that short strings (80 to 1500 chars) have an average compression rate of 98%, while strings longer than 60000 characters have an average compression rate of 48%. Testing was done with random as well as real world data.

So there is most likely some performance loss, but it is outweighed by smaller database files and the fact that base 64 strings makes life very easy.
