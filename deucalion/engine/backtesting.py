
from deucalion.client.simulator import Simulator

from deucalion.portfolio import Portfolio
from deucalion.order import Order
from deucalion.trade import Trade

from collections import deque


class BacktestEngine(Engine):
    """
    Engine subclass for backtesting. Simulated order execution and portfolio updating.

    Essentially implements a broker interface for submitting/updating orders and 
    runs order execution in response to 


    Specification:

        - _approve_order: 
    """ 

    def __init__(self, portfolio: Portfolio, client: Simulator, config: dict = None):
        super().__init__(portfolio, config)
        self.client = client

    
    def _approve_order(self, order: Order) -> bool:
        # TODO Add error handling
        if order.direction == "BUY":
            price = self.client.get_price(order.contract_id)
            if price * order.qty >= self.portfolio.buying_power:
                # Order value exceeds buying power
                return False
        elif order.direction == "SELL":
            # TODO implement shorting functionality
            if self.portfolio[order.contract_id].size < order.qty:
                # Order quantity exceeds existing position
                return False
        else:
            raise ValueError(f"Unknown order direction '{order.direction}'")
        return True
    
    
    def _fill_order(self, order: Order) -> Trade:


    def submit_order(self, order: Order):
        if self._approve_order(order):
            self.active_orders.append(order)
    

    