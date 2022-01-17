#######################################################################
##############  Chapter 16: Operator Overloading: Doing It Right
#######################################################################
from array import array
import reprlib
import math
import operator
import functools
import itertools
from  collections import abc

# We use Vector from chapter 12
class Vector:
    typecode = 'd'

    def __init__(self, components):
        self._components = array(self.typecode, components)
    
    def __iter__(self):
        return iter(self._components)

    def __repr__(self) -> str:
        components = reprlib.repr(self._components)
        components = components[components.find('['): -1] 
        class_name = type(self).__name__
        return f'{class_name}({components})'

    def __str__(self) -> str:
        return str(tuple(self))
    
    def __abs__(self):
        return math.hypot(*self)

    def __bool__(self):
        return bool(abs(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)]) + self._components.tobytes())   

    @classmethod
    def formbytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)    # memv is iterable

    def __len__(self):
        return len(self._components)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            cls = type(self)
            return cls(self._components[key])
        index = operator.index(key)
        return self._components[index]

    def __getattr__(self, attr):   
        cls = type(self)
        try:
            pos = cls.__match_args__.index(attr)
        except ValueError:
            pos = -1
        if 0<= pos < len(self._components):
            return self._components[pos]
        msg = f'{cls.__name__!r} has no attribute {attr!r}'
        raise AttributeError(msg)

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

############## Operator Overloading

############## Unary Operators : - , +

    def __neg__(self):
        return Vector( -x for x in self)

    def __pos__(self):
        return Vector(self)

############## Overloading + for Vector addition :

    def __add__(self, other):
        # === v0:
        # pairs = itertools.zip_longest(self, other, fillvalue=0) # we fill the shortest iterable with zeros !
        # return Vector( a + b for a, b in pairs)         # We return New Object
        
        # === v1:
        try:
            pairs = itertools.zip_longest(self, other, fillvalue=0.0)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented


#  adding the reversed special method, __radd__(), to support iterable + Vector()

    def __radd__(self, other):
        return self + other

##############  * operator :
    def __mul__(self, scalar):
        try:
            factor = float(scalar)      # Duck tuping: we do not perform an isinstance(scalar, ..), we just invoke float, and if it fails we hanle the exception: EAFP principle
        except TypeError:
            return NotImplemented   # should return NotImplemented and raise an error
        return  Vector(n * factor for n in self)
    
    def __rmul__(self, scalar):
        return self * scalar

############## @ operator :
    def __matmul__(self, other):
        if (isinstance(other, abc.Sized) and isinstance(other, abc.Iterable)):      # goose Typing
            if len(self) == len(other):
                return sum(a * b for a, b in zip(self, other))
            else:
                raise ValueError('@ requires vectors of equal length.')
        else:
            return NotImplemented

    def __rmatmul__(self, other):
        return self @ other

############## update __eq__ to returns NotImplemented
    def __eq__(self, other) -> bool:
        # === v0:
        # return len(self) == len(other) and all( a==b for a,b in zip(self, other))

        # === v1:
        if isinstance(other, Vector):
            return len(self) == len(other) and all( a==b for a,b in zip(self, other))
        else:
            return NotImplemented


############## Unary Operators :
# In general, Operators should always return new objects and not modify the operands. 
# However, for in place operators (+= -=), we modify the objects in place. But if the object is immutable (like Vector here) we should not update Vector !

v = Vector(range(4))
print(-v)       # (-0.0, -1.0, -2.0, -3.0)
print(+v)       # (0.0, 1.0, 2.0, 3.0)


############## Overloading + for Vector addition :
v1 = Vector([1,2, 3])
v2 = Vector([1,2])
print(v1 + v2)      # (2.0, 4.0, 3.0)
print(v1 + [1,1])   # (2.0, 3.0, 3.0)   Since there is not constraint on the type of second operand

print([1,2] + v1)   # TypeError: can only concatenate list (not "Vector") to list
# Why this error ?
# Here the answer: The interpreter evalutes an expression like a + b using the following steps :
# 
# 1. If a has an __add__ method, call a.__add__(b) and return result, unless a.__add__(b) return NotImplemented
# 2. If a doesn't have an __add__ or calling it returns NotImplemend, check if b has __radd__, then call b.radd__(a) and return results unless it's NotImplemented
# 3. If b doesn't have __radd__ or calling it returns NotImplemented, raise TypeError with an unsupported operands type messsage 
# This is known as the operator dispatch algorithm

############## After adding __radd__() method :
print([1,2] + v1)   # (2.0, 4.0, 3.0)

# if an operator special method cannot return a valid result because of type incompatibility, 
# it should return NotImplemented and not raise TypeError
# v1 + "ABC"  # TypeError: unsupported operand type(s) for +: 'float' and 'str'

# The new version of __add__ is :
def __add__(self, other):
    try:
        pairs = itertools.zip_longest(self, other, fillvalue=0.0)
        return Vector(a + b for a, b in pairs)
    except TypeError:
        return NotImplemented       # This not an error, it's used by the interpreter's dispatch algorithm as explained before !

############## * operator :
v3 = Vector(range(4))
print(v3 * 3)   # (0.0, 3.0, 6.0, 9.0)

############## @ operator :
print( Vector([1,2,3])  @  Vector([1,2,3])) # 14 (1*1 + 2*2 + 3*3 )

############## ==, != <, <=, >, >= 
# The handling of the rich comparison operators, ==, !=, >, <, >=, <= by the Python interpreter is similar to what we just saw, using 
# The operator dispatch algorithm:
# a > b is evaluated : a.__gt__(b) (if doesn't exist or returns NotImplementend) Then :
#  b.__lt__(a) (< special method) If doesn't exist or returns NotImplemented Then Raise TypeError
# 
# However, for == and !=, If the reverse call fails, Python compares object IDs instead of raising an error !


############## in-place operator : +=, -=, ...
# Those oporators should not be implemented for immutable types like Vector in our case.
# if python finds a method __iadd__ in the class, it uses this method to evaluate the expresssion a+=b for example. But if such method doesn't
# exist, Python simply uses __add__, since a+=b (is like a = a + b) but this time, a will not be changed in-place !
