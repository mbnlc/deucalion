

from dataclasses import dataclass

@dataclass(unsafe_hash=True) # TODO: Implement safe hash function
class Position:
    """
    Implements a single portfolio position.

    Specification:
        - contract: initially just ticker str, later full spec
        - size: number of assets (negative if short),
        - cost basis: initial cost of entering position
    """

    contract_id: str
    size: int = 0
    cost_basis: float = 0

    def __init__(self, contract_id: str, size: int=0, cost_basis: float=0.0):
        self.contract_id = contract_id
        self.size = size
        self.cost_basis = cost_basis

    @property
    def avg_price(self) -> float:
        return self.cost_basis / self.size
    
    # def __hash__(self):
    #     pass

    

    
