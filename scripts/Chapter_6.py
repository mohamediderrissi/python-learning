####################################################
##############  Chapter 6: Object References, Mutability, and Recycling
####################################################

from utils import clear

a = None
# The way to check something is None : 
a is None # instead of a == None

# Tuples in Python are immutable, we can not change their contents directly.
# ⚠ However:
#  if the tuple contains some mutable objects like lists, the content of the tuple will change indirectly
# 

t_conatins_list = (1,2, [3,4])
t_conatins_list[-1].append("test changing a list inside a tuple")
print(t_conatins_list)  # (1, 2, [3, 4, 'test changing a list inside a tuple'])

# copy of object is shallow by defaut !
from copy import copy, deepcopy

l=[1,2,(3,4), [5,6]]
l1 = l[:]       # shallow copy 
l1 = list(l)    # shallow copy

l2 = deepcopy(l1)   # deep copy

# The Function Parameters in Python are passed by References.
# which means: any function may change any mutable object it recieves !
clear()

def f(a,b):
    a += b
    return a
x = [1,2]
y = [3,4]
print(f(x,y))   # [1, 2, 3, 4]
print(x,y)      # [1, 2, 3, 4] [3, 4] x changed and becomes [1, 2, 3, 4]


clear()
# When you create a function or a method inside a class, with default parms.
# The function points to or refers to the same defaults parms ! each time invoked !

# Example 1:
def function_with_defaults_parms(parm=[1]):
    parm.append(len(parm)+1)

function_with_defaults_parms()  
function_with_defaults_parms()

print(dir(function_with_defaults_parms))    # there is a __defaults__ attribute wich refers to defaults parms
print(function_with_defaults_parms.__defaults__)    # the output is ([1, 2, 3],) !

# Example 2:
class HauntedBus:
    def __init__(self, passengers=[]) -> None:
        self.passengers = passengers
    def pick(self, name):
        self.passengers.append(name)
    def drop(self, name):
        self.passengers.remove(name)

h1 = HauntedBus()
h1.pick('A')
h1.pick('B')

h2 = HauntedBus()
print(h2.passengers)    # ['A', 'B']
# h1 and h2 shares the same passengers list ! and the list is mutable, any change in
# the list affects all the instances !
print(h1.passengers is h2.passengers)   # True

#  string interning : Technique used by Python interpreter ! to optimize space
clear()
x = (1,2,3)
y = (1,2,3)
print(x is y)   # True

a = "ABCD"
b = "ABCD"
print(a is b)   # True

# Good Practise, when dealing with references of mutable objects is to create a copy :
class GoodPracticeForMutableTypes:
    def __init__(self, list_as_param) -> None:
        self.passengers = list(list_as_param)   # crerate a copy of the list