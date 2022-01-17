#######################################################################
##############  Chapter 14: Inheritance: For Good or For Worse
#######################################################################
from utils import clear

############## Subclassing Built-In Types Is Tricky :
class DoubleDict(dict):
    def __setitem__(self, key, value) -> None:
        return super().__setitem__(key, [value] * 2)

dd = DoubleDict(one = 1)
print(dd)               # {'one': 1} : __init__ did not take into account the overide __setitem__

dd["two"] = 2
print(dd)               # {'one': 1, 'two': [2, 2]} : __setitem__ works here as expected !

dd.update(three = 3)
print(dd)               # {'one': 1, 'two': [2, 2], 'three': 3} : update did not take into account the overide __setitem__

# To solve this problem, we need to subclass from UserDict instead of dict (and the same: UsetList, UserString ...)
from collections import UserDict

clear()
class DoubleUserDict(UserDict):
    def __setitem__(self, key, value) -> None:
        return super().__setitem__(key, [value] * 2)

ud = DoubleUserDict(one = 1)
print(ud)               # {'one': [1, 1]}

ud["two"] = 2
print(ud)               # {'one': [1, 1], 'two': [2, 2]}

ud.update(three = 3)
print(ud)               # {'one': [1, 1], 'two': [2, 2], 'three': [3, 3]}

############## Multiple Inheritance and Method Resolution Order :
clear()
class A:
    def ping(self):
        print("ping: ", self)

class B(A):
    def pong(self):
        print("pong: ", self)

class C(A):
    def pong(self):
        print("PONG: ", self)

class D(B,C):
    def ping(self):
        super().ping()
        print("post-ping", self)

    def pingpong(self):
        self.ping()
        super().ping()  # uses __mro__
        self.pong()     # uses __mro__
        super().pong()  # uses __mro__
        C.pong(self)    # This syntax to call a specific method (pong of class C). Remark that pong() is not a classmethod !

d = D()
print(D.__mro__)    # __mro__ is a class attribute used for method resolution order. (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
d.pong()    # we look for pong() in B first and its superclasses(), and then C (as specified in __mro__). 
            # The mro is based on the order in which superclasses are declared ! class D(B, C) (B and its superclasses() first than C)

d.pingpong()

############## Best Practises for Multiple Inheretence: 

# When you inherets from a class just to have some functionnality, in this case, composition may be better that inheretence
# Prefer Composition Over Inherentence.( But Not always)
