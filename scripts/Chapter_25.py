#########################################################################################
##############  Chapter 25: Class Metaprogramming                                       #
#########################################################################################

############## Classes as Objects :
class Class_As_Object:
    pass

print(Class_As_Object.__class__)        # <class 'type'>   
print(Class_As_Object.__qualname__)     # Class_As_Object
print(Class_As_Object.__bases__)        # (<class 'object'>,)
print(Class_As_Object.__name__)         # Class_As_Object


############## type: The Built-in Class Factory :
# 
# type is a class that creates a new class when invoked with three arguments :
# 

# We can create the following class with type :
"""
class MyClass(Class_As_Object):
    x = 42
    def x2(self):
        return self.x * 2
"""
# With type() :

MyClass = type('MyClass', (Class_As_Object,), {'x': 42, 'x2': lambda self: self.x * 2})

# The type class is a metaclass: a class that builds classes. In other words, instances of the type class are classes.


############## A Class Factory Function :
import collections
from typing import Union, Any
from collections.abc import Iterable, Iterator

FieldNames = Union[str, Iterable[str]]

def parse_identifiers(names: FieldNames) -> tuple[str, ...]:
    if isinstance(names, str):
        names = names.replace(',', ' ').split()
    if not all(s.isidentifier() for s in names):
        raise ValueError('names must be all valid identifiers')
    return tuple(names)


def record_factory(cls_name: str, field_names: FieldNames) -> type[tuple]:
    slots = parse_identifiers(field_names)

    def __init__(self, *args, **kwargs) -> None:
        attrs = dict(zip(self.__slots__, args))
        attrs.update(kwargs)
        for name, value in attrs.items():
            setattr(self, name, value)
    
    def __iter__(self) -> Iterable[Any]:
        for name in self.__slots__:
            yield getattr(self, name)
    
    def __repr__(self):
        values = ', '.join(
            '{}={!r}'.format(*i) for i in zip(self.__slots__, self)
        )
        cls_name = self.__class__.__name__
        return f'{cls_name}({values})'
    
    cls_attrs = dict(
        __slots__= slots,
        __init__ = __init__,
        __iter__ = __iter__,
        __repr__ = __repr__,
    )

    return type(cls_name, (object,), cls_attrs)

# Test :
"""
Dog = record_factory('Dog', 'name weight owner')

rex = Dog('Rex', 30, 'Bob')
print(f'{rex!r}')           # Dog(name='Rex', weight=30, owner='Bob')

name, weight, _ = rex
print(name, weight)         # Rex 30

rex.weight = 100
print(f'{rex!r}')           # Dog(name='Rex', weight=100, owner='Bob')

print(Dog.__mro__)          # (<class '__main__.Dog'>, <class 'object'>)  - The newly created class inherits from object—no relationship to our factory.

"""
# Remarks: Instances of classes created with record_factory are not serializable !



##############  Introducing __init_subclass__ :
# 
# __init_subclass__ is called whenever the containing class is subclassed.
# 
from collections.abc import Callable
from typing import Any, NoReturn, get_type_hints

class Field:
    def __init__(self, name: str, constructor: Callable) -> None:
        if not callable(constructor) or constructor is type(None):
            raise TypeError(f'{name!r} type hint must be callable')
        self.name = name
        self.constructor = constructor
    
    def __set__(self, instance: Any, value: Any) -> None:
        if value is ...:
            value = self.constructor()
        else:
            try:
                value = self.constructor(value)
            except (ValueError, TypeError) as e:
                type_name = self.constructor.__name__
                msg = f'{value!r} is not compatible with {self.name}:{type_name}'
                raise TypeError(msg) from e
        instance.__dict__[self.name] = value
        

class Checked:
    @classmethod
    def _fields(cls) -> dict[str, type]:
        return get_type_hints(cls)
    
    def __init_subclass__(subclass) -> None:        # This is like a classmethod, however, the first argument is not the current class, but the class that subclasses Checked !
        super().__init_subclass__()
        for name, constructor in subclass._fields().items():
            setattr(subclass, name, Field(name, constructor))
    
    def __init__(self, **kwargs) -> None:
        for name in self._fields():
            value = kwargs.pop(name, ...)       # dictonary_object.pop(key, defaut_value[in case no valid key]). Here ... as default value !
            setattr(self, name, value)
        if kwargs:
            self.__flag_unknown_attrs(*kwargs)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._fields():
            cls = self.__class__
            descriptor = getattr(cls, name)
            descriptor.__set__(self, value)
        else:
            self.__flag_unknown_attrs(name)
    
    def __flag_unknown_attrs(self, *names: str) -> NoReturn :
        plural = 's' if len(names) > 1 else ''
        extra = ', '.join(f'{name!r}' for name in names)
        cls_name = repr(self.__class__.__name__)
        raise AttributeError(f'{cls_name} object has no attribute{plural} {extra}')
    
    def _asdict(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name, attr in self.__class__.__dict__.items() if isinstance(attr, Field)
        }
    
    def __repr__(self) -> str:
        kwargs = ', '.join(
            f'{key}={value!r}' for key, value in self._asdict().items()
        )
        return f'{self.__class__.__name__}({kwargs})'

# Test :
"""
class Movie(Checked):
    title: str
    year: int
    box_office: float

movie = Movie(title = "The Father", year = 1997, box_office = 137)
print(movie.title)                   # The Father
print(movie)                         # Movie(title='The Father', year=1997, box_office=137.0)

print(Movie(title='Life of Brian'))  # Movie(title='Life of Brian', year=0, box_office=0.0)

# blockbuster = Movie(title='Avatar', year=2009, box_office='billions')   # TypeError: 'billions' is not compatible with box_office:float

# movie.year = "Mohamed"                                                  # TypeError: 'Mohamed' is not compatible with year:int
# movie.test = "Fake"                                                     # AttributeError: 'Movie' object has no attribute 'test

"""

############## Enhancing Classes with a Class Decorator :
#  
#  A class decorator is a callable that behaves similarly to a function decorator: 
# it gets the decorated class as an argument, and must return a class 
# which will replace the decorated class.
#  
#  

# This is a class decorator that adds a method to the deorated class :
def add_test(cls : type):
    def test(self):
        print('test method ........')

    setattr(cls, 'test', test)

    return cls

@add_test
class Klass:
    pass

# Test :

k = Klass()
k.test()    # test method ........


############## Metaclasses:
#  
#   [Metaclasses] are deeper magic than 99% of users should ever worry about. If you wonder whether you need them, you don’t (the people who
# actually need them know with certainty that they need them, and don’t need an explanation about why) -- Tim Peters, Inventor of the timsort algorithm.
#  

#  - A metaclass is a class factory. A metaclass is class whose instances are classes
#  - type is the superclass of classes (object is an instance of the class type).
#  - A metaclass should inheret from type

# print(isinstance(object, type))     # True

# Example: 
class MetaBunch(type):  
    def __new__(meta_cls, cls_name, bases, cls_dict):
        defaults = {}

        def __init__(self, **kwargs):
            for name, default in defaults.items():
                setattr(self, name, kwargs.pop(name, default))
            if kwargs:
                setattr(self, *kwargs.popitem())
        
        def __repr__(self): 
            rep = ', '.join(
                        f'{name}={value!r}' for name, default in defaults.items() if (value := getattr(self, name)) != default
                            )
            return f'{cls_name}({rep})'

        new_dict = dict(__slots__=[], __init__ = __init__, __repr__ = __repr__)

        for name, value in cls_dict.items():
            if name.startswith('__') and name.endswith('__'):
                if name in new_dict:
                    raise AttributeError(f"Can't set {name!r} in {cls_name!r}")
                new_dict[name] = value
            else:
                new_dict['__slots__'].append(name)
                defaults[name] = value
        return super().__new__(meta_cls, cls_name, bases, new_dict)

class Bunch(metaclass=MetaBunch):
    pass

# Test :
class Point(Bunch):
    x = 0.0
    y = 0.0
    color = 'gray'

p = Point(x=1.2, y=3.4, color= 'green')
print(p)         # Point(x=1.2, y=3.4, color='green')

print(Point())  # Point()

# Point(x=1.2, y=3.4, z= 34)  # AttributeError: 'Point' object has no attribute 'z'

p.x = 1000
print(p)    # Point(x=1000, y=3.4, color='green')

# p.flavor = 'banana'         # AttributeError: 'Point' object has no attribute 'flavor'


# A Class Can Only Have One Metaclass :
from abc import ABC

class Record(ABC, metaclass=MetaBunch): # TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
    pass


# 
# الحمد لله رب العالمييييييييين
# 


