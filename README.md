# dinkycache for python projects
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A very small name/value cache for python. 

Intended for quick set up, in development and small scale projects.

Uses `sqlite` for storage and `lzstring` for compression.

Accepts any data that can be parsed in to a string with `json.loads()`

## Dependencies
```python
pip install lzstring==1.0.4
```

## How to use
Download the dcache.py file to your project folder and import
```python
from dinky import Dinky
```

Has two methods called like so:
```python
Dinky().read(str)
Dinky().write(str, dict)
```

## Example
```python
from dcache import Dinky

#gets data from some slow source
def get_some_data(id):
    return "some data"

id = "001"

```
Then where you would normaly write:
```python
results = get_some_data(id)
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
    results = get_some_data(id)
    Dinky().write(id, results)
```
Third option is to use it like this:

```python
    #Write:
    d = Dinky()
    d.id = "test"
    d.data = {"whatever": "floats"}
    d.setTTL(24) #hr
    d.write()
    print(d.data)

    #Read:
    d = Dinky(ignore_garbage_colletion = true)
    d.id = "test
    print(d.read())
```

In either case `results` will contain the data from cache if its there and within the specified TTL. Or it will call your get_some_data() to try and fetch the data instead.

## Settings

Avaialble settings and default values
```python
    dbfile: str = "dinkycache.db",  # name of sqlite file
    ttl: int = 2160,                # time to live in hours, default 2160 = 90 days, 0 = no expiry
    purge_rows: bool = True,        # will enforce row_limit if true
    row_limit: int = 5000,          # maximum number of rows in db
    clean_expired: bool = True,     # will delete outdated entries if true
    clean_hrs: int = 24,            # time between cleanups of expried entries
    clean_iterations: int = 100,    # iterations (reads/writes) between cleanups
```

Set them in one of the following ways
```python
Dinky('preferred.db', 24)
Dinky(dbfile='preferred.db').read(id)
Dinky(ttl=24).read(id)
```
OR
```python
settings = ['preferred.db', 24]
Dinky(*settings).read(id)
Dinky(*settings).write(id, results)
```
OR
```python
settings = {
    'dbfile' = 'preferred.db',
    'ttl' = 24,
}
Dinky(**settings).read(id)
Dinky(**settings).write(id, results)

```
## Cleanup / Garbage Collection
Script will try to clean out expired entries every time it is run if one of the following is met.
It has been minimum `garbage_collection: int = 24` hours since last cleanup
OR
There have been more than `garbage_iterations: int = 100` invocations since last cleanup

The cleanup function will make the script 75% slower when it runs

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
