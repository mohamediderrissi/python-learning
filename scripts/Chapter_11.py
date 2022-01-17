#####################################################
##############  Chapter 11: A Pythonic Object
#####################################################
import math
import array
from utils import clear

class Vector2d:
    typecode = 'd'      # a class attribute will be used in bytes() and frombytes methods

    __match_args__ = ('x', 'y')  # we add this class attribute to support Postional Pattern matching

    def __init__(self, x, y):
        # self.x = float(x)        
        # self.y = float(y)
        self.__x = float(x)        # we make x and y privates
        self.__y = float(y)
    
    # we add getters : 
    # The code that use x, y when they were public, is unchanged ! 
    # ==> One advantage of Python: We can start by public attributes 
    # and later on, we make them privates without changing the code that use those attribute before the change !
    @property
    def x(self):
        return self.__x

    @property    
    def y(self):
        return self.__y


    def __repr__(self) -> str:  # Good Practice : The string returned by __repr__ is simiar to the way how we create a new object !
        class_name = type(self).__name__
        return '{}({!r}, {!r})'.format(class_name, *self)

    def __str__(self) -> str:
        return str(tuple(self))

    def __iter__(self):     # used to unpack items: x,y = Vector2d(1,2)
        return (i for i in (self.x, self.y))

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return (self.x == other.x) and (self.y == other.y)
        return False

    def __hash__(self) -> int:
        return hash(self.x) ^ hash(self.y)  # Using ^ : Xor operator to mix hashes is recommended !

    def __bytes__(self):
        return (
            bytes([ord(self.typecode)]) +
            bytes(array.array(self.typecode, self))     # self is iterable (__iter__ method is implemented !)
        )

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))
    
    @classmethod        # This is a classmethod. No self argument, instead the class itself - conventionally named cls ! 
    def frombytes(cls, octets: bytes):
        typecode = chr(octets[0])       # slicing of bytes (even [0:1]) return byte-type. But retriving one element (by index) returns integer, that way here we need chr()
        memv = memoryview(octets[1:]).cast(typecode)
        return(cls(*memv))      # unpacking memoryview with *
    
    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('p'):
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{},{}>'
        else:
            coords = self
            outer_fmt = '({},{})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)
    
    def angle(self):
        return math.atan2(self.y, self.x)



v1 = Vector2d(1,2)
# print(v1.x, v1.y)   # 1.0 2.0

x, y = v1   # x=1.0 y=2.0
print(tuple(v1))    # (1.0, 2.0)

v1    # if v1 is used in the console, we see Vector2d(1.0, 2.0)
print(repr(v1)) # Vector2d(1.0, 2.0)

v1_clone = eval(repr(v1))
print(v1_clone == v1)   # True

print(v1)   # (1.0, 2.0)

octets = bytes(v1)
print(octets)   # b'd\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@'

print(abs(Vector2d(3,4))) # 5.0

print((bool(v1), bool(Vector2d(0,0))))  # (True, False)

print(v1 == Vector2d.frombytes(bytes(v1)))  # True

############## @classmethod  Vs @staticmethod
# @classmethod is the same like @staticmethod but: @classmethod recieves the class as a first argument while @staticmethod does not recieve the classe !
# Cocnsluion: Most or all of the time, we use @classmethod

############## Formatted Displays : 
# __format__  is used to format the display of an object. It's used by : 
#  - format() build-in function
#  - f-strings
#  - str.format()

# for the example, we use 'p' as a letter for custom format code of Vector2d, to display the polar coordiantes.
# The letter 'p' is not used by any built-in types to format the display. (Good practice: not reuse existing format codes )

print(format(Vector2d(1,1), '.2f'))    # (1.00,1.00)
print(format(Vector2d(1,1), '.3e'))    # (1.000e+00,1.000e+00)
print(format(Vector2d(1,1), 'p'))      # <1.4142135623730951,0.7853981633974483>
print(format(Vector2d(1,1), '.3ep'))    # <1.414e+00,7.854e-01>
print(format(Vector2d(1,1), '.5fp'))    # <1.41421,0.78540>


############## Make Vector2d Hashable : 

# 1. we need first make the class immutable: 
#   - we make x and y private (Even if in Python, someone can still access x and y indirectly )
clear()

class T:
    def __init__(self, x) -> None:
        self.__x = x
    
    @property 
    def x(self):
        return self.__x

t = T(10)
# Indirectly, we can access and modify private attributes in Python
# t.__x   # 'T' object has no attribute '__x'   Never use this technique in a production code !
# t._T__x # object._className__privateAttribue
# print(t._T__x)  # 10 even if x is private ! we have access to it !
# t._T__x = 7
# print(t._T__x)  # 7   

# Directly, we can't modify but we can read through the getter @property x() !
# t.x = 4 # AttributeError: can't set attribute 'x'
print(t.x)  # 10

# 2. we add the __hash__ and __eq__ functions in Vector2d:
print(hash(Vector2d(3.1675, 4.1)))     # 463619827915582471

# Now we can set of Vector2d:
# print(set([Vector2d(1,1), Vector2d(2,2)]))          # {Vector2d(1.0, 1.0), Vector2d(2.0, 2.0)}

##############  Other possible special methods to implement in Vector2d:
#   - __int__       : invoked by int()    
#   - __float__     : invoked by float()
#   - __complex__   : invoked by complex()

############## Provide support for match with Positional Patterns : 
# Normally, Keywords patterns works as it's the case for all classes, as shown in the following example:

def keywordMatch(v):
    match v:
        case Vector2d(x = 0, y = 0):
            print(f'{v!r} is null ')
        case Vector2d(x=0):
            print(f'{v!r} is vertical ')
        case Vector2d(y=0):
            print(f'{v!r} is horizontal')
        case _:
            print(f'{v!r} is awesome !')

keywordMatch(Vector2d(0, 123))      # Vector2d(0.0, 123.0) is vertical
keywordMatch(Vector2d(1, 0))        # Vector2d(1.0, 0.0) is horizontal

## But: With Positional Patterns: It doesn't work :

def MatchWithPostionalPatterns(v):
    match v:
        case Vector2d(0, _):
            print(f'{v!r} is vertical ')

# MatchWithPostionalPatterns(Vector2d(0,17865))   #TypeError: Vector2d() accepts 0 positional sub-patterns (2 given)

# To add the support of Match With Postional Patterns, we need to add a class attribute 
# named   __match_args__ , wich lists the instance attributes in the order they will 
# be used for positional pattern matching: 
# 
# __match_args__ = ('x', 'y')

MatchWithPostionalPatterns(Vector2d(0,17865))   # Vector2d(0.0, 17865.0) is vertical

############## Subclass to customize Vector2d: 

class ShortVector2d(Vector2d):
    typecode = 'f'      # We modify the class attribute inhereted from the parent class.

sv = ShortVector2d(1/11, 1/12)
print(repr(sv))     # ShortVector2d(0.09090909090909091, 0.08333333333333333) because class_name is not harded coded in the parent class

print(len(bytes(Vector2d(1/11, 1/12)))) # 17
print(len(bytes(sv)))                   # 9