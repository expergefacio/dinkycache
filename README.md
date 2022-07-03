# dinkycache
A very small small name/dict cache for python. Intended to be quick to set up and run in development or small scale apps.

Uses sqlite and lzstring

##Dependencies
```
pip install lzstring==1.0.4
```

##How to use
Download the dcache.py file to your project folder and import
```
from dcache import Dinky
```

Has two methods called like so:
```
Dinky().read(str)
Dinky().write(str, dict)
```

##Example
```
from dcache import Dinky

#gets data from some slow source
def get_some_data(id):
    return {}

id = "001"


#then where you would normaly write:
results = get_some_data(id)

#write these 3 lines instead:
if (results := Dinky().read(id)) == False:
    results = get_some_data(id)
    Dinky().write(id, results)

#Then results will contain the data from cache if its there and within the specified TTL. Or it will call your get_some_data() to try and fetch the data instead.

```

##Performance

This wont ever compete with Redis, MongoDB or anything like it. This is ment to be a small, easy solution for small scale use cases where you dont want or need any big dependencies. Hence performance will be less, but might still be orders of magnitude faster than parsing the data from some website every time.

I generated 2 databases of 10000 entries. One with random dicts up 150000 characters. And one with dicts up to 1500 characters.

Reads from DB1
```
10k entries of 40 to 1500 characters:

100 reads = 0.6sec (0.006 avg)
1 read = 0.018 to 0.003 sec
```

Reads from DB2
```
10k entries of 40 to 150000 characters:
1 read = 0.003 to 0.022 sec
100 reads = 1.1 to 2.4 sec (0.015 avg)
```

So the numbers are not amazing, but well within what you could expect from sqlite3.

##Security

I dont know all that much about SQL injection, so to be on the safe side, all data is compressed to base64 string using lzstring. The id field accepts stings containing alphanumerical characters only. That way there should be no risk of injection attacks.

Beware however that there is no checking for html-tags and such. Just something to bevare of if for some reason you should use this to store and later display user provided data.


