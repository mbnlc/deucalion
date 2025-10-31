
import datetime as dt
import pandas as pd


from deucalion.client.client import Client


class SimulatedClock:
    """
    Manages time passed in the backtest simulation

    credit: askarsher - trading_algo_1.0
    """

    def __init__(self, start_date, tick_interval_seconds):
        self.current_time = start_date
        self.tick_interval = dt.timedelta(seconds=tick_interval_seconds)

    def get_timestamp(self):
        """Returns the current simulated time as a Unix timestamp."""
        return self.current_time.timestamp()

    def advance(self):
        """Moves the clock forward by one tick interval."""
        self.current_time += self.tick_interval

    def subscribe(self, callable):
        pass



class Simulator(Client):
    """
    Simulator client used for backtesting.

    """

    def __init__(self, clock: SimulatedClock, data: pd.DataFrame):
        super().__init__()
        
    