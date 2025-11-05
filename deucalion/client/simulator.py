
import datetime as dt
import pandas as pd


from deucalion.client.client import Client


class SimulatedClock:
    """
    Manages time passed in the backtest simulation.
    
    This class provides a simulated clock that advances at specified intervals
    and notifies subscribers when time advances. Subscribers can register
    callbacks to be called on each tick.
    
    credit: askarsher - trading_algo_1.0
    
    Attributes:
        current_time: The current simulated time as a datetime object.
        tick_interval: The time interval between ticks as a timedelta.
        subscribers: List of callable functions to be called on each tick.
    
    Example:
        >>> clock = SimulatedClock(dt.datetime(2024, 1, 1), 60)
        >>> clock.subscribe(my_callback_function)
        >>> clock.advance()  # Calls my_callback_function with current time
    """

    def __init__(self, start_date: dt.datetime, tick_interval_seconds: int):
        """
        Initialize the simulated clock.
        
        Args:
            start_date: The starting datetime for the simulation.
            tick_interval_seconds: The number of seconds between each tick.
        """
        self.current_time = start_date
        self.tick_interval = dt.timedelta(seconds=tick_interval_seconds)
        self.subscribers = []

    def get_timestamp(self) -> float:
        """Returns the current simulated time as a Unix timestamp."""
        return self.current_time.timestamp()

    def advance(self):
        """
        Moves the clock forward by one tick interval and notifies all subscribers.
        
        After advancing the clock, all registered subscribers are called with
        the current time as an argument.
        """
        self.current_time += self.tick_interval
        # Notify all subscribers of the tick
        for callback in self.subscribers:
            callback(self.current_time)

    def subscribe(self, callback):
        """
        Register a callback function to be called on each clock tick.
        
        Args:
            callback: A callable function that accepts a datetime argument.
                     The function will be called with the current time whenever
                     advance() is called.
        """
        if callback not in self.subscribers:
            self.subscribers.append(callback)



class Simulator(Client):
    """
    Simulator client used for backtesting.
    
    This class simulates market data by emitting historical data points
    at each clock tick. It ensures zero look-ahead bias by only providing
    data up to and including the current simulated time.
    
    The Simulator subscribes to a SimulatedClock and processes time-indexed
    data (pandas DataFrame) to emit price data as the simulation progresses.
    
    Attributes:
        clock: The SimulatedClock instance that controls time progression.
        data: A pandas DataFrame with datetime index containing price data.
              Columns should represent contract_id (ticker symbols).
        current_data: DataFrame containing only data up to current time.
        subscribers: Dictionary mapping event types to lists of callbacks.
    
    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({'AAPL': [100, 101, 102]}, 
        ...                      index=pd.date_range('2024-01-01', periods=3))
        >>> clock = SimulatedClock(dt.datetime(2024, 1, 1), 86400)
        >>> simulator = Simulator(clock, data)
        >>> simulator.subscribe('tick', my_strategy.on_tick)
    """

    def __init__(self, clock: SimulatedClock, data: pd.DataFrame):
        """
        Initialize the Simulator.
        
        Args:
            clock: A SimulatedClock instance that controls time progression.
            data: A pandas DataFrame with datetime index. Columns should be
                  contract_id (ticker symbols), values should be prices.
                  The index must be datetime-like and sorted.
        
        Raises:
            ValueError: If data is empty or index is not datetime-like.
        """
        super().__init__()
        
        if data.empty:
            raise ValueError("Data DataFrame cannot be empty")
        
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data DataFrame must have a DatetimeIndex")
        
        # Ensure data is sorted by time
        self.data = data.sort_index()
        self.clock = clock
        self.subscribers = {}  # Dictionary: event_type -> list of callbacks
        
        # Initialize current_data with data up to start_date
        self.current_data = self.data.loc[self.data.index <= self.clock.current_time]
        
        # Subscribe to clock ticks
        self.clock.subscribe(self._on_tick)

    def _on_tick(self, current_time: dt.datetime):
        """
        Internal callback method called when the clock advances.
        
        This method filters the data to include only points up to and including
        the current time, then notifies subscribers of new data.
        
        Args:
            current_time: The current simulated time from the clock.
        """
        # Filter data to include only points up to current time (no look-ahead)
        mask = self.data.index <= current_time
        self.current_data = self.data.loc[mask]
        
        # Notify subscribers of the tick event
        if 'tick' in self.subscribers:
            for callback in self.subscribers['tick']:
                callback(current_time)

    def subscribe(self, event_type: str, callback):
        """
        Subscribe to simulator events.
        
        Args:
            event_type: Type of event to subscribe to (e.g., 'tick').
            callback: Callable function to be called when the event occurs.
                     For 'tick' events, the callback receives the current datetime.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)

    def get_price(self, contract_id: str) -> float:
        """
        Get the current price for a given contract.
        
        Returns the most recent available price for the contract_id,
        based on the current simulated time. Only returns data that
        has been "emitted" up to the current time (no look-ahead bias).
        
        Args:
            contract_id: The ticker symbol or contract identifier.
        
        Returns:
            The most recent price for the contract as a float.
        
        Raises:
            KeyError: If contract_id is not found in the data.
            ValueError: If no data is available up to the current time.
        """
        if contract_id not in self.data.columns:
            raise KeyError(f"Contract '{contract_id}' not found in data")
        
        if self.current_data.empty:
            raise ValueError("No data available for current time")
        
        # Get the latest available price for this contract
        if contract_id in self.current_data.columns:
            # Get the last non-null value
            series = self.current_data[contract_id].dropna()
            if series.empty:
                raise ValueError(f"No price data available for '{contract_id}' at current time")
            return float(series.iloc[-1])
        else:
            raise KeyError(f"Contract '{contract_id}' not found in current data")
    