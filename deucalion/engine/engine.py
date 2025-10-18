
from deucalion.client import Client

from deucalion.portfolio import Portfolio
from deucalion.order import Order

from collections import deque

class Engine:
    """
    Base class for trading engine.
    
    This class will implement basic functionality for maintaining a portfolio, 
    executing orders and providing event handling functionality.

    I will derive from this class to implement BacktestingEngine which handles events
    based on historical data.

    Specification:
        - maintain portfolio instance
        - execute orders on portfolio
        - provide portfolio metrics (mkt values, excess liq, etc., unrealized p&l)

        - maintain active orders
        - handle order execution events

        - surface event handlers for data 
        - surface event handlers for orders
        - 

    Engine instance maintains time state.
    """

    def __init__(self, portfolio: Portfolio, client: Client, config: dict = None):
        self.client = client
        self.portfolio = portfolio
        self.active_orders = deque()




class BacktestEngine(Engine):
    """
    Engine subclass for backtesting.


    """

    def __init__(self, portfolio: Portfolio, client: Client, config: dict = None):
        super().__init__(portfolio, config)
        self.client = client

    
    def _approve_order(self, order: Order) -> bool:
        if order.direction == "BUY":
            
        elif order.direction == "SELL":
            pass
        else:
            raise ValueError(f"Unknown order direction '{order.direction}'")

    
    def submit_order(self, order: Order):



        self.active_orders.append(order)
    