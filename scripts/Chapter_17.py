#######################################################################
##############  Chapter 17: Iterables, Iterators, and Generators
#######################################################################
from utils import clear
import re
import reprlib

RE_WORD = re.compile('\w+')     # word

class SentenceV0:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)
    
    def __getitem__(self, index):
        return self.words[index]
    
    def __len__(self):
        return len(self.words)

    def __repr__(self) -> str:
        return 'Sentence(%s)' % reprlib.repr(self.text)     # If text is too long, we display the ...

# Sentence is iterable even without __iter__ (Python uses __getitem__ with index starts from 0 if founded)
s = SentenceV0("A B C")
print(list(s)) #    ['A', 'B', 'C']
list_words = [ word for word in s]
print(list_words)   #   ['A', 'B', 'C']

############# Why Sequences Are Iterable ?
# The Python interpreter performs the followings steps :
#   1. Checks whether the object implements __iter__, and calls that to obtain an iterator
#   2. If __iter__ is not implemented, but __getitem__ is implemented, Python creates an iterator that attempts to fetch items starting for 0
#   3. If no __getitem__, Python raises TypeError (C object is not iterable)
#######

############# Iterable Pattern: (In Python, it's useless to implement it from scratch !)
# The idea is to create an iterator that will be used to traverse a data structure.
# The iterator is created by an iterable.
# Each time, we invoked the iterable we get an new iterator that can be used to traverse the data again

class SentenceV1(SentenceV0):   # Sentence Now is iterable : It implements __iter__ method
    
    #  The iterable protocol  
    def __iter__(self):
        return SentenceIterator(self.words)

class SentenceIterator:     # The is the iterator : it implements __next__ and __iter__
    def __init__(self, words) -> None:
        self.words = words
        self.index = 0
    
    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration()      # an iterator should raise a StopIteration to signal no more items !
        self.index+=1
        return word

    def __iter__(self):
        return self

# Test of SentenceV1 : 
s1 = SentenceV1('Pig and Pepper')
it = iter(s1)
print(next(it))
print(next(it))
print(next(it))
# next(it)    # StopIteration

############# Don’t make the iterable an iterator for itself
# An iterable should return a new iterator each time, it's called with iter() built-in method !
# 
# iterable : implemenets  __iter__
# iterator : implemenets __next__ and __iter__
# 
clear()
############# Generator function in Python: 
# Any Python function that contains the yield keyword is a generator function.
def gen123():
    yield 1
    yield 2
    yield 3

g = gen123()
print(f'{g!r}')     # <generator object gen123 at 0x000001E1B0A60040>  -  this an iterator
print(next(g))  # 1
print(next(g))  # 2
print(next(g))  # 3
# print(next(g))  # StopIteration

#### Python provides generator functions as a convenient shortcut to building iterators:
# Using the generator function, we can simplify the build of the iterable Sequence.
#   
class SentenceV3(SentenceV0):
    def __iter__(self):
        for word in self.words:
            yield word
        
#### generators are used to save memory (we do not use load all the items to memory, instead we generate one item per call ) 
#       ==> Very usefull for large datasets

#### An optimized version of Senctence :
# The idea :
# Instead of build a list of all the words, and return word at time, using re.findalll()
# we use instead re.finditer() which returns a generator producing instances on demand !

RE_WORD = re.compile('\w+')
class Sentence():
    def __init__(self, text) -> None:
        self.text = text        # No need to have a words list. We save memory !
    
    def __iter__(self):
        for match in RE_WORD.finditer(self.text):
            yield match.group()

############# Generator Expression : A syntax sugar to build generator function :
def gen_AB():
    print("start")
    yield 'A'
    print('continue')
    yield 'B'
    print("end. ")

l = [x for x in gen_AB()]   # The words are printed all during the construction of the list. (the list loads all the items in memory: eager load)
# start
# continue
# end.

for i in l:
    print("---> ", i)
# --->  A
# --->  B

#  On the other hand: 

generator_exp = (x for x in gen_AB())
print(generator_exp)    # <generator object <genexpr> at 0x000001D232F40EB0>

for i in generator_exp:
    print("---> ", i)
# The Output of the loop :
# start
# --->  A
# continue
# --->  B
# end.

# The call of next(generator_exp) is performed only inside the loop and not at the begining like the list : Lazy load ==> Save memory

# Using Generator Expression we can simplify __iter__ even more in Sentence :
class SentenceVf(Sentence):
    def __iter__(self):
        # for match in RE_WORD.finditer(self.text):
        #     yield match.group()
        return (match.group() for match in RE_WORD.finditer(self.text))

# When a generator expression is passed as the single argument to a function or
# constructor, you don’t need to write a set of parentheses for the function call and another
# to enclose the generator expression. A single pair will do like :
# 
#        def __mul__(self, scalar):
#            if isinstance(scalar, numbers.Real):
#                return Vector(n * scalar for n in self)     # Here
#            else:
#                return NotImplemented  
#


# There are a lot of Generator Functions  in The standard libray. Think to use them
# like: 
# zip(it1, ..., itN)    Yields N-tuples built from items taken from the iterables in parallel silently stopping when the first iterable is exhausted
# zip_longest(it1, ..., itN, fillvalue=None) like zip but it doesn't stop on the first it exausted, but filling the blanks with the fillvalue

############# Subgenerators with yield from :
def sub_gen():
    yield 2
    yield 3
    return "Done !"
def gen():
    yield 1
    result = yield from sub_gen()
    yield result
    yield 4

print([x for x in gen()])   # [1, 2, 3, 'Done !', 4]

# Example with yield from : 
def tree(cls, level=0):
    yield cls.__name__, level
    for sub_cls in cls.__subclasses__():
        yield from tree(sub_cls, level+1)

def display(cls):
    for cls_name, level in tree(cls):
        indent = ' ' * 4 * level
        print(f'{indent}{cls_name}')

# if __name__ == '__main__':
    # display(BaseException)

#### Some part of the Output :
# BaseException
#     Exception
#         TypeError
#         StopAsyncIteration
#         StopIteration
#         ImportError
# ....

############# all() and any() buil-ins functions :
all([]) # Return True if bool(x) is True for all values x in the iterable. If the iterable is empty, return True.
any([]) # Return True if bool(x) is True for any x in the iterable. If the iterable is empty, return False.


############# A Closer Look at the iter Function
# As we’ve seen, Python calls iter(x) when it needs to iterate over an object x.
# But iter has another trick: 
# it can be called with two arguments to create an iterator from a regular function or any callable object. 
# In this usage, the first argument must be a callable to be invoked repeatedly (with no arguments) to yield values, 
# and the second argument is a sentinel: a marker value which, when returned by the callable, causes the iterator to raise
# StopIteration instead of yielding the sentinel
# 
import random
def d6():
    return  random.randint(1,6)

d6_iter = iter(d6, 1)   # will raise StopIteration when 1 is returned by d6()
print(d6_iter)      # <callable_iterator object at 0x000001F6BA58F460>

print([x for x in d6_iter]) # [3, 4, 5, 5, 3, 4]
