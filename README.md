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
from dcache import Dinky
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

In either case `results` will contain the data from cache if its there and within the specified TTL. Or it will call your get_some_data() to try and fetch the data instead.

## Performance

This wont ever compete with Redis, MongoDB or anything like it. This is ment to be a small, easy solution for small scale use cases where you dont want or need any big dependencies. Hence performance will be less, but might still be orders of magnitude faster than repeatedly parsing the data from some website.

### Tests:

Reads from DB1
```
10k entries of 40 to 1500 characters:

1 read = 0.018 to 0.003 sec
100 reads = 0.6 sec (0.006 avg)
```

Reads from DB2
```
10k entries of 40 to 150000 characters:
1 read = 0.003 to 0.022 sec
100 reads = 1.1 to 2.4 sec (0.015 avg)
```

## Security
Ids are hashed, so you may put anything in there
Data is compressed to a string of base 64 characters, so you may put anything in there.

Lzstring seem to have very high integrity, we have not been able to produce a test result where the input and output has not been equal.

That said, what you put in is what you'll get out. There is no checking for html-tags and such. Just something to bevare of if for some reason you'll use it to store and later display user provided data.

## Compression
Lzstring is not great for shorter strings, and does sometimes even increase to string lenght. However in testing we found that short strings (80 to 1500 chars) have an average compression rate of 98%, while strings longer than 60000 characters have an average compression rate of 48%. Testing was done with random as well as real world data.

So there is most likely some performance loss, but it is outweighed by smaller database files and the fact that base 64 strings makes life very easy.
