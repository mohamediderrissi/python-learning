#######################################################################
##############  Chapter 18: Context Managers and else Blocks
#######################################################################

############## else with try/catch

def code_that_may_throw_exception():
    pass

def code_that_does_not_throw_exception():
    pass

# doing this better ...
try:
    code_that_may_throw_exception()
except OSError:
    pass
else:
    code_that_does_not_throw_exception()    # This code will be exectuted only if no exception is raised !
                                            # Also, Exceptions in the else clause are not handled by the preceding except clauses

# than :
try:
    code_that_may_throw_exception()         # We do not know exatly which function may throw an exception !
    code_that_does_not_throw_exception()
except OSError:
    pass

############## Context Managers and with Blocks

# Width designed to simplify try/finally pattern. 
# 
# Syntax:
# width [The code here is used to create a Context manager Object] as somthing (somthing is bound to the results return by calling __enter__ on the context manager object)
# When control flow exists from wdith, the __exit__ method is invoked on the context manager object (not on what __enter__ returned )

############## Create a Context Manager :
class TestContextManager:

    def __enter__(self):
        # Prepare some context ...
        import sys
        self.original_write = sys.stdout.write
        sys.stdout.write = self.reverse_write
        return "Mohamed"
    
    def reverse_write(self, text):  # reverses the text argument and calls the original implementation
        self.original_write(text[::-1])


    def __exit__(self, exc_type, exc_value, traceback):     # This three params are the same returened by call to sys.exc_info() inside a finally block !
        import sys
        sys.stdout.write = self.original_write
        if exc_type is ZeroDivisionError:
            print("Please Don't divide by zero !")
            return True     # return True tells the interpreter that the exception was handled ! (so it will not propagate)


with TestContextManager() as test:
    print(test)     
    3/0
# demahoM
# Please Don't divide by zero !

############## Simplify the creation of Context manager using @contextlib.contextmanager decorator :
import contextlib

@contextlib.contextmanager
def test_context_manager():
    # Prepare some context ...
    import sys
    original_write = sys.stdout.write
    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write

    yield "Mohamed" # ================ The code until the part, represents the __enter__ method , and the coming is the  __exist__ method

    sys.stdout.write = original_write


with test_context_manager() as test_1:
    print("ABCD")
    print(test_1)
#  Output:
# DCBA
#  demahoM

# update test_context_manager to handle excpetions :

@contextlib.contextmanager
def test_context_manager():
    import sys
    original_write = sys.stdout.write
    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write

    msg = ""    # empty string
    try:
        yield "Mohamed"     # If an exception occured inside the with block, it will be propagate until here
    except ZeroDivisionError:
        msg = "Please Don't divide by zero !"
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)






