import os
print("Hello world")
# This a comment

# This is a 
# multiligne comment

"""
This a  multiligne string
line1
line2
...etc
"""

x, y, z = 1, 2, 3
x, y, z = [1, 2, 3]

# List Comprehensions: 
print( sum(x for x in range(3)) )
_list = [(x,y,z) for x in range(3) for y in range(3) for z in range(3)]

# generator expression like List Comprehensions but for tuples and ..
#  genexp saves memory because it yields one item at a time, not like list Comprehensions
symbols = '$¢£¥€¤'
tuple(ord(symbol) for symbol in symbols)

# Function with arbitary number of arguments : using *
def my_sum(*args):
    print('args: ', args)
    print('type: ', type(args))
    return sum(args)

print(my_sum(1, 2, 3, 4))
# args:  (1, 2, 3, 4)
# type:  <class 'tuple'>
# sum :  10

# with two **: 
def func_kwargs(**kwargs):
    print('kwargs: ', kwargs)
    print('type: ', type(kwargs))

func_kwargs(key1=1, key2=2, key3=3)
# kwargs:  {'key1': 1, 'key2': 2, 'key3': 3}
# type:  <class 'dict'>

def clear():
    os.system('clear')

# hash function: since 1 == 1.0 so hash(1) should be equal to hash(1.0). 
# Remark: == tests value equality not like (a is b  <=> id(a) == id(b))
def getInfos(o):
    print(f'class: {o.__class__}')
    print(f'id: {id(o)}')
    print(f'a == b : {a == b}')
    print(f'hash(a)= {hash(a)} ')
    print(f'hash(b)= {hash(b)} ')

a, b = 1, 1.0
clear()
getInfos(a)
getInfos(b)

# 
# s = {1.0, 2.0, 3.0}
# s.add(1)
# print(s)  # {1.0, 2.0, 3.0} (because 1 == 1.0)

# Dicts comprehensions:
t = [("Maroc", 212), ("Algerie", 213)]
d = {number: country.upper() for country, number in t if(number > 100)}  # d == {212: 'MAROC', 213: 'ALGERIE'}


# Regular Expressions:
import re

## re.findall():  returns a list of strings containing all matches.

def test_findall():
  string = 'hello 12 hi 89. Howdy 34'
  pattern = '\d+'
  print(re.findall(pattern, string))    # ['12', '89', '34']

## re.split():

def test_split():
  string = '11 Twelve:12 Eighty nine:89.'
  pattern = '\d+'
  print(re.split(pattern, string))      # ['', ' Twelve:', ' Eighty nine:', '.']


## re.sub(pattern, replace, string): 
# The method returns a string where matched occurrences are replaced with the content of replace variable.

def test_sub():
  # Example remove all whitespaces:
  string = 'abc  12 \
    de 23 \n  f45  6'
  pattern = '\s+'
  replace = ''
  print (re.sub(pattern, replace, string))    # abc12de23f456









####################################################
##############  Chapter 4: Text Versus Bytes
####################################################
clear()
s = 'الاسلام'
print(len(s))   # 7
print(s.encode("utf8"))     # encode the string s to bytes using utf8 encoding.  b'\xd8\xa7\xd9\x84\xd8\xa7\xd8\xb3\xd9\x84\xd8\xa7\xd9\x85'
print(len(s.encode("utf8"))) # 14

# We need to normalize unicode strings before comparaison !
from unicodedata import normalize
clear()
string1 = 'café'
string2 = 'cafe\N{COMBINING ACUTE ACCENT}'
print(string1, string2, sep='\t') # café    café

string1 == string2 # false

normalize('NFC', string1) == normalize('NFC', string2) # True
# To read more about normalization: Check the Unicode standard : https://unicode.org/

####################################################
##############  Chapter 5: Data Class Builders
####################################################

############## 1. collections.namedtuple :
clear()
from collections import namedtuple

City = namedtuple('City', 'name country population coordinates') # City is subclass of tuple (so immutable)

tokyo = City('Tokyo', 'JP', 36.933, (35.689722, 139.691667))
print(tokyo)   # City(name='Tokyo', country='JP', population=36.933, coordinates=(35.689722, 139.691667))
tokyo.population # 36.933
tokyo[1]    # 'JP

tokyo._asdict() # City(name='Tokyo', country='JP', population=36.933, coordinates=(35.689722, 139.691667))

# import json
# print(json.dumps(tokyo._asdict())) # {"name": "Tokyo", "country": "JP", "population": 36.933, "coordinates": [35.689722, 139.691667]}

# defaults values for the rightsmost attributes: 
Coordinates = namedtuple('Coordinates', 'lat lon reference', defaults=['XXXVGFS'])
c = Coordinates(lat=0, lon=1) # (lat=0, lon=1, reference='XXXVGFS)

############## 2. typing.NamedTuple :
from typing import NamedTuple

class Coordinates(NamedTuple): # subclass of tuple and not NamedTuple
    lat: float  # Every instance field must be annotaed with a type. Those types are not checked by Python at runtime !
    lon: float
    reference: str = 'XXXVGFS'

# coord_tokyo = Coordinates("fr", 'ff')
# print(coord_tokyo)  # Coordinates(lat='fr', lon='ff', reference='XXXVGFS')


############## 3. @dataclass :
from dataclasses import dataclass
# @dataclasss decorator add some methods to the class (__init_, reper, eq  ...etc)
@dataclass(frozen=True) # mutable by default. add the option frozen=True to make the class immutable
class Coordinates:
    var1: int
    var2: float
    # This method will be added to the generated __init__() method by @dataclass.
    # Use cases: validation or compute field values based on other fields.
    def __post_init__(self):
        print("post_init is called !")

c = Coordinates(1,2)    # post_init is called !

########## Pattern matching with mach/case :

def test_match_case(a):
    match a:
        case 1:
            print("1")
        case 2:
            print("2")
        case [str(name), *_]:   # destructring and matching !
            print(name)
        # we can use nested lists and tuples.
        # *_ match any number of items without bind them to a varaible
        # using *extra instead of *_ would bind items to extra as a list with 0 or more items ! 
        case (int(age), *_, (float(lat),float(lon))):    
            print(age, lat, lon)
        case _:     # match any things
            print("unknown")

#  Pattern matching with classes !

class MatchWithClasses:
    def __init__(self, a, b):
        self.a = a
        self.b = b

def TestMatchWithClasses(aclass):
    match aclass:
        case MatchWithClasses(a = 1, b = value_of_b):   # works for all classes, but with public attributes !
            print(f'found instance of class MatchWithClasses with a = 1 and b = {value_of_b}')
        case _:
            print("No things !")
clear()
TestMatchWithClasses(MatchWithClasses(1, 20)) # found instance of class MatchWithClasses with a = 1 and b = 20


