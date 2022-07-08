from cgi import test
from dinky import Dinky
import random
import json
import time
import lzstring
import urllib.request


print("  _       _   ")
print(" | |_ ___| |_ ")
print(" | __/ __| __|")
print(" | |_\__ \ |_ ")
print("  \__|___/\__|")
print("              ")


#"run" test funtions in here
#exec at end of file
def run():
    #generate_random()
    #compression_test()
    #openfoodfacts_data_test()
    #read_test()
    #generate100k()
    #generatenr(100000)
    #read10k()
    #poop()
    sql()
    pass

def sql():
    #SELECT id FROM mytable ORDER BY id ASC LIMIT 100
    #DELETE FROM dinkycache WHERE id IN (SELECT id FROM dinkycache ORDER BY created DESC LIMIT -1 OFFSET 1000)
    #(SELECT id FROM dinkycache ORDER BY created DESC LIMIT -1 OFFSET 100)
    strt = time.perf_counter()
    result = Dinky()._dev_runSQL(
        "SELECT id FROM dinkycache ORDER BY created DESC LIMIT -1 OFFSET 100"
    )
    nd = time.perf_counter()
    for x in result:
        print(x[0])
    
    print((nd - strt), " exec")

#region: generation/helper functions
def r():
    return random.randint(1,10)

def rnd():
    rn = r()
    if rn == 1:
        return dic(4)
    if rn < 4:
        return p()
    if rn < 7:
        return r()
    if rn < 11:
        return b()

def dic(it = 4):
    d = {}
    for i in range(1, it):
        d[str(i)] = rnd()
    return d

def p():
    num_sentences = random.randint(2,10)
    paragraph = ""
    for i in range(0, num_sentences):
        paragraph += generate_sentence()
    return paragraph

def generate_sentence():
    num_words = random.randint(5,10)
    sentence = ""
    for i in range(0, num_words):
        sentence += generate_word() + " "
    return sentence.capitalize()

def generate_word():
    word = ["the", "of", "and", "a", "to", "in", "is", "you", "that", 
            "it", "he", "was", "for", "on", "are", "as", "with", "his", 
            "they", "I", "at", "be", "this", "have", "from", "or", "one",
            "had", "by", "word", "but", "not", "what", "all", "were", "we", 
            "when", "your", "can", "said", "there", "use", "an", "each", 
            "which", "she", "do", "how", "their", "if", "will", "up", "other", 
            "about", "out", "many", "then", "them", "these", "so", "some", 
            "her", "would", "make", "like", "him", "into", "time", "has", 
            "look", "two", "more", "write", "go", "see", "number", "no", 
            "way", "could", "people", "my", "than", "first", "water", "been", 
            "call", "who", "oil", "its", "now", "find", "long", "down", "day", 
            "did", "get", "come", "made", "may", "part"]
    return word[random.randint(0,99)]

def b():
    return bool(random.randint(0,1)) 
#endregion

def generate100k():
    strt = time.perf_counter()
    for i in range(1, 100000):
        now1 = time.perf_counter()
        rd = dic(4)

        Dinky().write(str(i), rd)

        now = time.perf_counter()
        print(now1 - now)
    nd = time.perf_counter()
    print((nd - strt) / 100000, "avg")


def generatenr(nr):
    strt = time.perf_counter()
    rd = dic(5)
    for i in range(1, nr):
        Dinky(clean_expired=False, purge_rows=False).write(str(i), rd)

    nd = time.perf_counter()
    print((nd - strt) / nr, "avg")
    
def read10k():
    strt = time.perf_counter()
    for i in range(1, 10000):
        Dinky().read(str(i))
    nd = time.perf_counter()
    print((nd - strt) / 10000, "avg")

def poop():
    strt = time.perf_counter()
    dink = Dinky()
    dink.id = "test2"
    dink.data = {"whatever": "floats"}
    dink.setTTL(24) #hr
    dink.write()
    first = time.perf_counter()

    print(Dinky().read("test2"))

    sec = time.perf_counter()
    print(f"{first - strt}, {sec - first}")



#generate random
def generate_random():
    for i in range(1, 1000):
        rd = dic(4)

        Dinky().write(str(i), rd)

        ret = Dinky().read(str(i))

        ln = len(json.dumps(ret))

        if rd == ret:
            print(f"it: {i} TRUE   {ln} chars")
        else:
            print(f"it: {i} FALSE  {ln} chars")



#read test
def read_test():
    st = time.time()
    for i in range(0, 100):
        Dinky().read(str(random.randint(1,10000)))

    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')



#real world data compression test avg 49%
def openfoodfacts_data_test():
    min = 1000
    max = 0
    all = []

    barcodes = [3017620422003, 3274080005003, 7622210449283, 5449000000996, 3017620425035, 3175680011480,
                5449000131805, 3046920022651, 8000500310427, 3168930010265, 5900649063785, 5000128677127,
                5400141431537, 8719324347129, 3229820129488, 8001505005592, 3760020507350, 3229820100234,
                3228857000166, 7613034626844, 3268840001008, 7300400481588, 5010477348678, 3175681851849]
    for i in barcodes:
        page = urllib.request.urlopen(f'https://world.openfoodfacts.org/api/v0/product/{i}.json')
        jsn = json.loads(page.read())
        if jsn["status"] != 0:
            rd = jsn

            lz = lzstring.LZString()
            str_data = json.dumps(rd)
            compressed = lz.compressToBase64(str_data)

            ln1 = len(str_data)
            ln2 = len(compressed)
            diff = int((ln2 / ln1) * 100)

            if diff > max:
                max = diff
            if diff < min:
                min = diff

            all.append(diff)

            print(f"iteration: {i}  "
                f"original:{str(ln1).rjust(6, ' ')}  "
                f"compressed:{str(ln2).rjust(6, ' ')}   "
                f"compression: {diff} ")

    total = 0
    for x in all:
        total = total + x
    avg = total / len(all)

    print(f"Min {min}")
    print(f"Max {max}")
    print(f"Avg {avg}")  




#test compression avg 98% for small dicts, 
#      47% best case for large dicts
def compression_test():
    min = 1000
    max = 0
    all = []

    for i in range(1, 101):
        rd = dic(1000)

        lz = lzstring.LZString()
        str_data = json.dumps(rd)
        compressed = lz.compressToBase64(str_data)

        ln1 = len(str_data)
        ln2 = len(compressed)
        diff = int((ln2 / ln1) * 100)

        if diff > max:
            max = diff
        if diff < min:
            min = diff

        all.append(diff)

        print(f"iteration: {i}  "
            f"original:{str(ln1).rjust(6, ' ')}  "
            f"compressed:{str(ln2).rjust(6, ' ')}   "
            f"compression: {diff} ")

    total = 0
    for x in all:
        total = total + x
    avg = total / len(all)

    print(f"Min {min}")
    print(f"Max {max}")
    print(f"Avg {avg}")



run()