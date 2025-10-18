
from dataclasses import dataclass

@dataclass
class Order:
    """
    Implements an open order for trade.

    
    """

    contract_id: str
    direction: str
    qty: int
    order_type: str
    

    def __init__(self, contract_id: str, direction: str, qty: int, 
                 order_type: str="MARKET", params: dict = None):
        
        self.contract_id = contract_id
        self.direction = direction
        self.qty = qty
        self.order_type = order_type
        self.params = params

    