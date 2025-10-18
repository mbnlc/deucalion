
from dataclasses import dataclass

from deucalion.position import Position


class Portfolio:
    """
    Implements a portfolio of positions. 
    
    This object will be continuosly updated by the Engine. Provide handlers for 
    portfolio interaction.

    Specification:
        - maintain cash position
        - maintain dictionary of positions

    Future features:
        - portfolio config functionality (no_shorting, margin_allowed, etc.)
    """

    def __init__(self, cash, positions: set[Position] = set()):
        self.cash = cash
        self.positions = {p.contract_id: p for p in positions}


    def __getitem__(self, id) -> Position:
        """Retrieve position by contract_id"""
        return self.positions[id]
    
    @property
    def contracts(self) -> list[str]:
        return self.positions.keys()

    @property
    def buying_power(self) -> float:
        return self.cash    # TODO Future feature: margin trading
    

@dataclass
class PortfolioEvent:
    """
     
    """

    def __init__(self):
        pass