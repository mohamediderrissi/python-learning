####################################################
##############  Chapter 7: Functions as First-Class Objects
####################################################

from utils import clear

#  Functions in Python are first class object (like string, integer, and dict), which means :
#   - we can pass function as parms to other functions:
#   - ...

#  Exmaple : Pass function as an argument :
clear()
def test(a,b):
    return a + b

# print(test(1,2))  # 3

def exec_test(function):
    a,b = 2,8
    print(function(a,b))

exec_test(test) # 10

#  Example : use a varaible to call the function 
test_function = test
print(test_function(1,2))   # 3
print(type(test))   # <class 'function'>

# Example: return a function
def return_a_function():
    def a():
        print("I am the a function")
    return a
return_a_function()()   # I am the a function

# map and filter using listcomprehension :
from math import factorial
print(list(map(factorial, filter(lambda n: n%2, range(6)))))    # [1, 6, 120]

print([factorial(n) for n in range(6) if n%2])  # [1, 6, 120]

# Callable objects in pythons are not just functions (there are 9 types !)
# we can chech if an object is callable with callable() built-in function.

print(callable(len))    # True

# We can create objects that are callable by implementing __call__ method :
# We can use this to create functions with an internal state !
clear()
class TestCallableClass:
    def __call__(self):
        print(f'Object of {self.__class__} has been called like a function !')

test_callable_class = TestCallableClass()
callable(test_callable_class)   # True
test_callable_class()   # Object of <class '__main__.TestCallableClass'> has been called like a function !

# Postional Parameters and Keywords Parameters :
def f(name, *t, class_=None, **args):   # name can be passed as positional parm (The first parms ) or as a keyword (name ='sthg')
    pass
