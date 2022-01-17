#######################################################################
##############  Chapter 12: Writing Special Methods for Sequences
#######################################################################
from array import array
import reprlib
import math
import operator
import functools
import itertools

class Vector:
    typecode = 'd'
    __match_args__ = ('x', 'y', 'z', 't')

    def __init__(self, components):
        self._components = array(self.typecode, components)   # protected attribute start with _
    
    def __iter__(self):
        return iter(self._components)

    def __repr__(self) -> str:
        components = reprlib.repr(self._components)     # to produce ... for large data. [1, 2, 3, ...]
        components = components[components.find('['): -1]   # Here we can use : reprli.repr(list(self._components)) But it's a waste (copy the whole components ...! innefficient)
        class_name = type(self).__name__
        return f'{class_name}({components})'

    def __str__(self) -> str:
        return str(tuple(self))
    
    def __abs__(self):
        return math.hypot(*self)

    def __bool__(self):
        return bool(abs(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) + self._components.tobytes())   # remarque: bytes(65) is diferent than bytes([65])

    @classmethod
    def formbytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)    # memv is iterable

    # Sequence Protocol: __len__ and __getitem__
    def __len__(self):
        return len(self._components)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            cls = type(self)
            return cls(self._components[key])
        index = operator.index(key)
        return self._components[index]

    # Dynamic attribute access: 
    def __getattr__(self, attr):    # This method is invoked by the interpreter when Python to find the attribute we try to access to.
        cls = type(self)
        try:
            pos = cls.__match_args__.index(attr)
        except ValueError:
            pos = -1
        if 0<= pos < len(self._components):
            return self._components[pos]
        msg = f'{cls.__name__!r} has no attribute {attr!r}'
        raise AttributeError(msg)

    # We define this method to remove the inconsistency  ! (In general - when we define __getattr__ we define also __setattr__)
    def __setattr__(self, name, value) -> None:
        cls = type(self)
        if len(name) == 1:
            if name in self.__match_args__:
                error = 'readonly attribute {attr_name!r}'
            elif name.islower():
                error = "can't set attributes 'a' to 'z' in {cls_name!r}"
            else:
                error = ''
            if error:
                msg = error.format(cls_name=cls.__name__, attr_name = name)
                raise AttributeError(msg)
        
        super().__setattr__(name, value)       

    def __eq__(self, other) -> bool:
        # if isinstance(other, self.__class__):
        #     return self._components == other._components
        # return False
        return len(self) == len(other) and all( a==b for a,b in zip(self, other))

    # Hash function :
    def __hash__(self) -> int:
        hashes = (hash(x) for x in self._components)
        return functools.reduce(operator.xor, hashes, 0)

    # Formatting:
    def __format__(self, fmt_spec='') -> str:
        if fmt_spec.endswith('h'):     # hyperspherical cordinates
            fmt_spec = fmt_spec[:-1]
            coords = itertools.chain([abs(self)], self.angels())
            outer_fmt = '<{}>'
        else:
            coords = self
            outer_fmt = '({})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(','.join(components))
        
    def angel(self, n):
        r = math.hypot(*self[n:])
        a = math.atan2(r, self[n-1])
        if (n == len(self) - 1) and (self[-1] < 0):
            return math.pi * 2 - a
        else:
            return a

    def angels(self):
        return (self.angel(n) for n in range(1,len(self)))

v = Vector(range(3))
print(repr(Vector(range(1000))))    # Vector([0.0, 1.0, 2.0, 3.0, 4.0, ...])
print(v)    # (0.0, 1.0, 2.0)

print(bytes(v)) # b'd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@

v_clone = Vector.formbytes(bytes(v))
print(v_clone == v)     # True

print(abs(Vector([3,4])))  # 5.0
print(bool(Vector([0, 0, 0])))  # False

############## Sequence Protocol: 
# You do not need to inheret from special classes to create a full functional sequences
# You Just need to implement the methods that fulfill the sequence protocol (a definition of duck Typing)

# A protocol is an informal interface define in documentation and not in code. For Example: 
# The sequence protocol in Python ==> entails the __len__ and getitem__ methods

v1 = Vector([3, 4, 5])
print(len(v1))  # 3
print(v1[-1])   # 5.0

v7 = Vector(range(7))
print(v7[1:4])      # array('d', [1.0, 2.0, 3.0])

############## Fix: print(v7[1:4])  gives   # array('d', [1.0, 2.0, 3.0]), we want: Vector([1.0, 2.0, 3.0])
#  After modifying __getitem__:
print(repr(v[1:4]))     # Vector([1.0, 2.0])

############## Dynamic attribute access: 
v2 = Vector([1,2,3,4,5])
# print(v2.a)      # AttributeError: 'Vector' has no attribute 'a'
print(v2.x, v2.y, v2.y, v2.z)  # 1.0 2.0 2.0 3.0

############## Inconsistency: 
# print(v2.x) # 1
# v2.x = 3
# print(v2.x) # 3
# print(v2)   #  (1.0, 2.0, 3.0, 4.0, 5.0) inconsistent !

# This inconsistency was introduced because of the way how __getatttr__ works ! 
# Python calls this method on an attribute Only when he didn't find the attribue defined in the object (or in object's super classes)

# To prevent this inconsistency, we add __setattr__ method (in our case, we prevent the modification of the object)
print(v2.x) # 1
# v2.x = 3    # AttributeError: readonly attribute 'x'


############## Add Hashing and update ==:
print(list(zip('abcdefg', range(3), range(4))))       # [('a', 0, 0), ('b', 1, 1), ('c', 2, 2)]

############## formatting: 

print(format(Vector([0, 0, 0]), '0.5fh'))   # <0.00000,0.00000,0.00000>
print(format(Vector([2, 2, 2, 2]), '.3eh')) # <4.000e+00,1.047e+00,9.553e-01,7.854e-01>

