#########################################################################################
##############  Chapter 10: Design Patterns with First-Class Functions
#########################################################################################

############## Strategy Pattern :  
from abc import ABC, abstractmethod
from typing import Callable, Optional
from decimal import Decimal

############## the strategy pattern : The classic apporach: 

class Order:  # The context that uses the Promotions: 
    promotion: Optional['Promotion'] = None

# Abstract class Promotion with the abstract method discount() ! 
class Promotion(ABC):
    @abstractmethod
    def discount(self, order: Order) -> Decimal:
        """Returns discounts as a positive dollar amount"""

# Concrete classes : FidelityPromo - BulkItemPromo - LargerOrderPromo
class FidelityPromo(Promotion):
    def discount(self, order: Order) -> Decimal:
        print("discount from FidelityPromo ")

class BulkItemPromo(Promotion):
    def discount(self, order: Order) -> Decimal:
        print("discount from BulkItemPromo ")

class LargerOrderPromo(Promotion):
    def discount(self, order: Order) -> Decimal:
        print("discount from LargerOrderPromo ")

# 
# With Python: It's possible to refactor the strategy pattern and simplify the code !
# 

############## the strategy pattern : The Pythonic apporach:

# concrete classes are just simple functions !
def fidelity_promo(order: Order):
    print("discount from FidelityPromo ")

def bulkItem_promo(order: Order):
    print("discount from BulkItemPromo ")

def largerOrder_promo(order: Order):
    print("discount from LargerOrderPromo ")

class Order:
    # This type hint says: promotion may be None,
    # or it may be a callable that takes an Order argument and returns a Decimal.
    # It replaces the use of abstract class
    promotion : Optional[Callable[['Order'], Decimal]] = None

# 
# If we want to add a new strategy (new function) to compute the best promotion for a given order
# we need to track the different promotions possibles.
# One way is by using a decorator :
#

Promotion = Callable[[Order], Decimal]

promos: list[Promotion] = []    # Here, will save the different (strategies) functions used to calculate a promo 

def best_promo(order: Order):
    max(promo(order) for promo in promos)

def promotion(promo: Promotion) -> Promotion:
    promos.append(promo)
    return promo

@promotion
def fidelity(order: Order):
    pass

@promotion
def bulk_item(order: Order):
    pass

@promotion
def large_order(order: Order):
    pass

