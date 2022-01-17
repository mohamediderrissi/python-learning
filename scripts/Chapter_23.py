#########################################################################################
##############  Chapter 23: Dynamic Attributes and Properties                           #
#########################################################################################

############## A method is an attribute that is callable :
"""
d = {"a": 2}
pointer_to_keys_method_of_dict = getattr(d, "keys")     # Here we get a reference to the keys() method of dict. like ref = key
print(pointer_to_keys_method_of_dict())                 # dict_keys(['a'])
"""

############## Exploring JSON-Like Data with Dynamic Attributes :
# 
#   The Problem:
#   ============ 
#  With json data, if we want to access values in Python, we need to do somthing like:
# 
#  json_data['key_1']['key_1_1']["name"] ===> This is cumberstom (not handy, especially for nesting with many levels)
#  
# Instead, what we want is: 
# ========================= 
#  
# json_data.key_1.key_1_1.name (like in JavaScript)
#  
#  The main part of the solution is to use (__getattr__ method). This method is called as a falllback, when given the attribute is not found neiter in the class, nor  to its superclasses.
#  
# 

from collections import abc

class FrozenJSON:
    """A read-only façade for navigating a JSON-like object
       using attribute notation 
    """
    def __init__(self, mapping) -> None:
        self.__data = dict(mapping)
    
    def __getattr__(self, name: str):           # This method is only invoked as a fallback !
        try:
            return getattr(self.__data, name)   # This why all available methods of dict can be used with FrozenJSON.
        except AttributeError:
            try:
                return FrozenJSON.build(self.__data[name])
            except KeyError:
                raise AttributeError            # because __getattr__ is supposed to return AttributeError and not KeyError !
    
    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):        # Example of goose typing
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        return obj

# Test :
"""
from pathlib import Path
import json
PATH = Path(__file__).parent / "osconfeed.json"

json_data = json.load(open(PATH, mode='r'))
print(json_data['Schedule']['speakers'][-1]['name'])    # Robert Lefkowitz


frozenjson = FrozenJSON(json_data)
print(frozenjson.Schedule.speakers[-1].name)            # Robert Lefkowitz
print(frozenjson.keys())                                # dict_keys(['Schedule'])

"""
############## The Invalid Attribute Name Problem:
# In the prevouis example, we generate attributes of a FrozenJSON object dynamically using the json data.
# But the keys used in the json file, might not be a corrrect attribute names. For example, a key with "class", is not possible to be
# a valid attribute name. We cannot do something like: o.class  (SyntaxError: invalid syntax).
# In general,  This is true for situations where we generate attributes dynamically from an arbitrary source.
#  
# To deal with the problem: 
#   - We might check the keys in constructor (__init__), and if a key is Python keyword, we add _ at the end for example.  


############## The  __new__ :
# - In Python, __init__ gets self as the first argument, therefore the object already exists when __init__ iscalled by the interpreter.
# - The special method that Python calls to construct an instance is __new__.
# -  __new__ is a class method. Python takes the instance returned by __new__ and passes it as the first argument self of __init__.
# - If necessary, the __new__ method can also return an instance of a different class. When that happens, the interpreter does not 
#  call __init__. In other words, Python’s logic for building an object is similar to this pseudocode :
# 
#       # pseudo-code for object construction
#       def make(the_class, some_arg):
#           new_object = the_class.__new__(some_arg)
#           if isinstance(new_object, the_class):
#               the_class.__init__(new_object, some_arg)
#           return new_object
# 
import keyword

class FrozenJSON_V1:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg
    
    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if keyword.iskeyword(key):
                key += '_'
            self.__data[key] = value
    
    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON(self.__data[name])


############## A Python hack: update __dict__ :

class Record:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

# Test: 
"""
r = Record(a = 100, b = 2000)
print(vars(r))      # {'a': 100, 'b': 2000}
print(r.a)          # 100
"""


############## Using a Property for Attribute Validation: 
class LineItem:
    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

# LineItem class can accepts weight as a negative value ! (and the same for price !)
l = LineItem("some desc.", -100, 109)
print(l.subtotal())     # -10900 !!!


class LineItem_v1:
    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight        # In this assignement, the wight setter will be used (and raise ValueError if weight < 0)
        self.price = price

    def subtotal(self):
        return self.weight * self.price

    @property
    def weight(self):
        return self.__weight

    @weight.setter                  # There is also:  @weight.deleter
    def weight(self, value):        # The methods that implement a property all have the name of the public attribute: weight.
        if value > 0:
            self.__weight = value   # The actual value is stored in a private attribute __weight
        else:
            raise ValueError(' Value must be > 0')


# l1 = LineItem_v1("Some Description", -100, 100)     # ValueError:  Value must be > 0

# For the price we can do the same thing, but this would entail some repetition in our code.
# To solve the problem, we will implement a property factory. But before, here some remarks about @property decorator and properties in general:
# 
#   - @property is Although often used as a decorator, the property built-in is actually a class. (In Python, classes and functions are interchangeable )
#   - This is the full signature of the property constructor : property(fget=None, fset=None, fdel=None, doc=None)
#   - Properties Override Instance Attributes (property and attribute with the same name in an instance, the property has precedence)


############## Coding a Property Factory :

def quantity(storage_name):
    def qty_getter(instance):                   # instance refers to the LineItem instance where the attribute will be stored
        return instance.__dict__[storage_name]  # the value is retrieved directly from the instance.__dict__ to bypass the property and avoid an infinite recursion
    
    def qty_setter(instance, value):
        if value > 0:
            instance.__dict__[storage_name] = value # The value is stored directly in the instance.__dict__, again bypassing the property
        else:
            raise ValueError(" Value must > 0")
    
    return property(fget=qty_getter, fset= qty_setter)  # Build a custom property object and return it


class LineItem_v3:
    weight = quantity('weight')
    price = quantity('price')

    def __init__(self, description, weight, price):
        self.description = description
        self.weight = weight
        self.price = price

    def subtotal(self):
        return self.weight * self.price

# l3 = LineItem_v3("...", 100, -90)    # ValueError:  Value must be > 0



############## Handling Attribute Deletion: 

class Blacknight:
    def __init__(self):
        self.phrases = [
        ('an arm', "'Tis but a scratch."),
        ('another arm', "It's just a flesh wound."),
        ('a leg', "I'm invincible!"),
        ('another leg', "All right, we'll call it a draw.")
        ]

    @property
    def member(self):
        print('next member is: ')
        return self.phrases[0][0]
    
    @member.deleter
    def member(self):
        member, text = self.phrases.pop(0)
        print(f'BLACK KNIGHT (loose {member})  -- {text}')

# Test:
def sep():
    print("-"*66)

knight = Blacknight()
print(knight.member)
sep()
del knight.member
sep()
del knight.member
sep()
del knight.member
sep()
del knight.member

# Output:
# ======
# next member is: 
# an arm
# ------------------------------------------------------------------
# BLACK KNIGHT (loose an arm)  -- 'Tis but a scratch.
# ------------------------------------------------------------------
# BLACK KNIGHT (loose another arm)  -- It's just a flesh wound.
# ------------------------------------------------------------------
# BLACK KNIGHT (loose a leg)  -- I'm invincible!
# ------------------------------------------------------------------
# BLACK KNIGHT (loose another leg)  -- All right, we'll call it a draw.
#  
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  



############## Special Attributes that Affect Attribute Handling :
# 
# __dict__ :
#           A mapping that stores the writable attributes of an object or class. An object that has a __dict__ can have arbitrary new attributes set at any
# time. If a class has a __slots__ attribute, then its instances may not have a __dict__
# 
