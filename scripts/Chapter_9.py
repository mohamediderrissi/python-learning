####################################################
##############  Chapter 9: Decorators and Closures
####################################################

############## Decorator : @decorator <==> func  = decorator(func)

# @decorator
# def target():
#     print("running target ()")
# 
#  is equals to :
# 
# target = decorator(decorator)
# 

############## Decorators executes at import time !
# Which means that python evaluates the decorators when you import the module that contains them, and not until the runtime !


############## Vriable Scope Rules: 
# a variable assigned in a function is considred a local variable. (even if there is a global var with same name !)
# b = 0
# def f():
#     print(b)
#     b=1       # local variable
# f()       # UnboundLocalError: local variable 'b' referenced before assignment

# to explicitly, tell the interpreter that 'b' here is refering to global var b ! we use 'global'

# def f():
#     global b
#     print(b)  # No error !
#     b=1   # global var b will be assigned to 1

############## Closures : thoses are functions that contains variables that are neither local nor global !

# Closures are functions with a state !

def outer_function():
    number_of_calls = [0]
    def inner_function():
        number_of_calls[0] += 1 # number_of_calls is used here ! but it's not a local variable nor a global var !
        print(f'inner function is invoked {number_of_calls[0]} !')
    return inner_function

inner_function = outer_function()
inner_function()    # inner function is invoked 1 !
inner_function()    # inner function is invoked 2 !
inner_function()    # inner function is invoked 3 !

# In the previous exmaple, we use a list with 1 element, instaed of a direct variable !
# This is because, we can not just do number_of_calls+=1 !
# number_of_calls will be considered a local variable of the inner_function.
# There is a way to solve the problem, using 'nonlocal' key word :

def outer_function():
    number_of_calls = 0
    def inner_function():
        nonlocal number_of_calls    # nonlocal keyword !
        number_of_calls += 1 # number_of_calls is used here ! but it's not a local variable nor a global var !
        print(f'inner function is invoked {number_of_calls[0]} !')
    return inner_function


# Closure are used to implement decorators !

############## Stacked decorators are possibles !

def alpha(func):
    return func

def beta(func):
    return func

@alpha
@beta
def test_stacked_decorator():   # which <=> to : test_stacked_decorator = alpha(beta(test_stacked_decorator))
    pass

############## Parameterized Decorators :
# The idea is to create a Parameterized Decorators, is to create a function that returns a decorator as following:

def decorator_with_parm(active=False):
    def outer_func(func):
        if (active):
            pass
        # ...
        return func
    return outer_func

@decorator_with_parm(active=True)   # decorator_with_parm should be invoked with () parenthesis !
def f1():
    pass

############## Parameterized Decorators with class :
# It's possible to implement a decorator with parms using a class based apporach :

class class_decorator:
    def __init__(self, parm_of_decorator=None):
        self.parm = parm_of_decorator 

    def __call__(self, func):
        def some_decoration_for_func(args):
            print("some_decoration_for_func: --- starting decorating --- ")
            if(self.parm):
                print(f"recieved parameter: {self.parm} ")
            result = func(args)
            print("some_decoration_for_func: --- ending decorating --- ")
            return result
        return some_decoration_for_func

@class_decorator('some value')
def increment(param):
    return param+1

print(increment(2))
# Output :
# some_decoration_for_func: --- starting decorating ---
# recieved parameter: some value
# some_decoration_for_func: --- ending decorating ---

