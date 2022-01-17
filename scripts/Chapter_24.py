#########################################################################################
##############  Chapter 24: Attribute Descriptors                                       #
#########################################################################################


############## Simple example: A descriptor that returns a constant :

class Ten:      # This is Descriptor Class ( A class implementing the descriptor protocol: __get__ and/or __set___ and/or __delete__)
    def __get__(self, obj, objtype=None):
        return 10

class A:
    x = 5                       # Regular class attribute
    y = Ten()                   # Descriptor instance

a = A()
print(a.x)      # 5
print(a.y)      # 10

############## Descriptor Example: Attribute Validation: 

class Quantity:
    def __init__(self, storage_name):
        self.storage_name = storage_name
    
    def __set__(self, instance, value): # self refers to current instance (of Quantity - like normal), and instance refers to the instance of the managed class (instances of LineItem).
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            msg = f'{self.storage_name} must be > 0'
            raise ValueError(msg)

    def __get__(self, instance, owner):         # The owner argument is a reference to the managed class (LineItem class in this example).
        return instance.__dict__[self.storage_name]


class LineItem:
    weight = Quantity("weight")         # The first descriptor instance will manage the weight attribute
    price = Quantity("price")           # The second descriptor instance will manage the weight attribute

    def __init__(self, description , weight , price) -> None:
        self.description = description
        self.weight = weight            # Here __set__ of the descriptor will be used !
        self.price = price

    def subtotal(self):
        return self.weight * self.price

# Test:
"""
LineItem("descirptioh", -100, 90)   # ValueError: weight must be > 0
LineItem("descirptioh", 100, -90)   # ValueError: price must be > 0

"""

##############  It would be better if the LineItem class could be declared like this :
# 
#   class LineItem:
#        weight = Quantity()
#        price = Quantity()
# 
# Without explicty writing:  weight = Quantity("weight").
# 
# 
# 
# For This we will implement : __set_name__ special method 

class Quantity_v1:
    def __set_name__(self, owner, name):
        self.storage_name = name

    def __set__(self, instance, value):
        if value > 0:
            instance.__dict__[self.storage_name] = value
        else:
            msg = f'{self.storage_name} must be > 0'
            raise ValueError(msg)
    
    # no __get__ needed

class LineItem_v1:
    weight = Quantity_v1()         
    price = Quantity_v1()         

    def __init__(self, description , weight , price) -> None:
        self.description = description
        self.weight = weight           
        self.price = price

    def subtotal(self):
        return self.weight * self.price

LineItem_v1('des ...', -100, 88)        # ValueError: weight must be > 0

