#######################################################################
##############  Chapter 18: Context Managers and else Blocks
#######################################################################

############## Basic Behavior of a Generator Used as a Coroutine :
def simple_coroutine():
    print(" -> coroutine started")
    x = yield
    print(" -> coroutine recieved", x)

c = simple_coroutine()
print(c)        # <generator object simple_coroutine at 0x000001D05AE01FC0>
next(c)         #  -> coroutine started
# c.send(100)     # -> coroutine recieved 100 and raise StopIteration

# The states of coroutine: there is 4 states :
#   - GEN_CREATED   : Waiting to start execution
#   - GEN_RUNNING   : Currently being executed by the interpreter
#   - GEN_SUSPENDED : Currently suspended at a yield expression
#   - GEN_CLOSED    : Execution has completed
#   
# To check the state of a coroutine, we use inspect.getgeneratorstate(coroutine_object)
import inspect
import queue
print(inspect.getgeneratorstate(c))    # GEN_SUSPENDED

# We can send data to the coroutine only if it has been started already (once created, we need to call .next() or .send(None) ):
c1 = simple_coroutine()
# c1.send(10) # TypeError: can't send non-None value to a just-started generator

c1.send(None)   #   -> coroutine started

############## Example: Coroutine to Compute a Running Average: 
def averager():
    count = 0
    total = 0
    average = None
    while True:
        number = yield average
        count+=1
        total+=number
        average = total/count

a = averager()
next(a)     # we prime the coroutine - (we can't use it before make it started )
print(a.send(10))  # 10.0
print(a.send(30))  # 20.0
print(a.send(5))  # 15.0

############## Decorators for Coroutine Priming: 
from functools import wraps

def coroutine(func):
    @wraps(func)            # so the decorated function, does not loose the name and its docstrings ... We can omit it, without affecting this example
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer
# With the coroutime decorator, we can use a generator object from a generator function decorted with coroutine directlty 
# (without need to call .next() or .send(None)), as illustrated in the following: 
@coroutine
def f():
    x = yield
    print("recieved from the user: ", x)

g = f()
# g.send("Hello ")    # recieved from the user:  Hello "and raise StopIteration"


############## Coroutine Termination and Exception Handling: 

# An unhandled exception within a coroutine propagates to the caller of the next or send that triggered it: 
a = averager()
next(a)
print(a.send(10))       # 10.0
# print(a.send("mols"))   # TypeError: unsupported operand type(s) for +=: 'int' and 'str'

# We can use this technique to stop a coroutine :  We can use send with some sentinel value that tells the coroutine to exit like None or Ellipsis constant

# generator objects have two methods that allow the client to explicitly send exceptions into the coroutine: .throw() and .close()

#### .throw(): 
class DemoException(Exception):
    """An exception type for the demonstration."""

@coroutine
def demo_exc_handling():
    while True:
        try:
            x = yield
        except DemoException:
            print('*** DemoException handled. Continuing...')

d = demo_exc_handling()
d.throw(DemoException)      # *** DemoException handled. Continuing...
print(inspect.getgeneratorstate(d)) # GEN_SUSPENDED

try:
    d.throw(ZeroDivisionError)  # error raised: ZeroDivisionError (for unhandled exception, the exception propogates to the caller)
except Exception:
    pass
print(inspect.getgeneratorstate(d)) # GEN_CLOSED

# If we need to do some cleanup in a coroutine, whatever the thrown exception is :we  should use : try/finally (like normal exception handling)

#### .close():
dd = demo_exc_handling()
print(inspect.getgeneratorstate(dd))    # GEN_SUSPENDED
dd.close()
print(inspect.getgeneratorstate(dd))    # GEN_CLOSED



############## Returning a Value from a Coroutine :
# We can return a value from a coroutine. The coroutine should terminate normally to return the value :
from collections import namedtuple

Result = namedtuple('Result', 'count average')

@coroutine
def averager_with_return():
    count = 0
    total = 0
    average = None
    while True:
        term = yield
        if term is None:
            break
        count+=1
        total+=term
        average = total/count
    return Result(count, average)

ar = averager_with_return()
ar.send(10)
ar.send(30)
ar.send(5)
# ar.send(None)   # We send to make the coroutine stops.

# Output:
# Traceback (most recent call last):
#   File "c:\Users\lenovo\Desktop\Python mastery\Python Scripts\Chapter_19.py", line 138, in <module>
#    ar.send(None)   # We send to make the coroutine stops.
# StopIteration: Result(count=3, average=15.0)

# To get the value from the coroutine :
ar1 = averager_with_return()
ar1.send(10)
ar1.send(30)
ar1.send(5)
try:
    ar1.send(None)
except StopIteration as exc:
    result = exc.value

print(result)       # Result(count=3, average=15.0)

############## Using yield from :
# yield from can be used with any iterable :
def gen123():
    yield from [1, 2, 3]

g = gen123()
print(next(g))  # 1
print(next(g))  # 2
print(next(g))  # 3



############## Basic behavior of yield from:
# - the delegating generator:   The generator function that contains the yield from <iterable> expression.
# - the subgenerator:  The generator obtained from the <iterable> part of the yield from expression
# - the caller:  the client code that calls the delegating generator

def subgenerator():
    term = yield "subgenerator"
    if term is None:
        return "Terminated !"

    print("subgenerator: Recieved from the caller: ", term)
    return "I am happy !"

def generator():
    result = yield from subgenerator()
    print("generator: recieved result from subgenerator: ", result)

# the client code, a.k.a. the caller
def caller():
    g = generator()
    returned_from_subgen = next(g) # prime the generator
    try:
        g.send("Hello World !")
    except StopIteration as exc:
        pass
    print("caller: recieved from subgenerator: ", returned_from_subgen)    

caller()
#  Output:
#  
# subgenerator: Recieved from the caller:  Hello World !
# generator: recieved result from subgenerator:  I am happy !
# caller: recieved from subgenerator:  subgenerator
#  
# # #


# # # The main points here are : The client and subgenerator communicates directly when send or yieding data (the delegating generator is suspended)
# 
# - Any values that the subgenerator yields are passed directly to the caller of the delegating generator (i.e., the client code).
# - Any values sent to the delegating generator using send() are passed directly to the subgenerator. If the call raises StopIteration, 
#   the delegating generator is resumed. Any other exception is propagated to the delegating generator
# - return expr in a generator (or subgenerator) causes StopIteration(expr) to be raised upon exit from the generator
# - The value of the yield from expression is the first argument to the StopIteration exception raised by the subgenerator when it terminates



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#              Use Case: Coroutines for Discrete Event Simulation                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# => The point of this example was to show a main loop processing events and driving coroutines by sending data to them.

# # # # # # # # The Taxi Fleet Simulation: 

# CHeck out the code in the file named: taxi_sum.py


