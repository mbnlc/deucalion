
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
        subscribers: Dictionary mapping event types to lists of callbacks.
        last_packet: Most recent DataFrame of newly emitted rows (may be None).
    
    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({'AAPL': [100, 101, 102]}, 
        ...                      index=pd.date_range('2024-01-01', periods=3))
        >>> clock = SimulatedClock(dt.datetime(2024, 1, 1), 86400)
        >>> simulator = Simulator(clock, data)
        >>> simulator.subscribe('tick', my_strategy.on_tick)
        >>> # my_strategy.on_tick receives (current_time, packet_df)
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
        self.subscribers: dict[str, list] = {}
        self._last_emitted_time: dt.datetime | None = None
        self._last_packet: pd.DataFrame | None = None

        initial_window = self.data.loc[self.data.index <= self.clock.current_time]
        if not initial_window.empty:
            self._last_emitted_time = initial_window.index[-1]
            self._last_packet = initial_window.copy()

        # Subscribe to clock ticks
        self.clock.subscribe(self._on_tick)

    def _on_tick(self, current_time: dt.datetime):
        """
        Internal callback method called when the clock advances.
        
        This method extracts any newly available rows since the last tick and
        notifies subscribers with the corresponding data packet.
        
        Args:
            current_time: The current simulated time from the clock.
        """
        packet = self._extract_new_data(current_time)
        if packet.empty:
            return

        self._last_emitted_time = packet.index[-1]
        self._last_packet = packet.copy()

        if "tick" in self.subscribers:
            for callback in self.subscribers["tick"]:
                callback(current_time, packet.copy())

    def subscribe(self, event_type: str, callback):
        """
        Subscribe to simulator events.
        
        Args:
            event_type: Type of event to subscribe to (e.g., 'tick').
            callback: Callable function to be called when the event occurs.
                     For 'tick' events, the callback receives the current datetime
                     and a pandas DataFrame containing any newly available rows.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        if callback not in self.subscribers[event_type]:
            self.subscribers[event_type].append(callback)

    def get_data_upto(self, current_time: dt.datetime | None = None) -> pd.DataFrame:
        """
        Return all available data up to the specified time.

        Args:
            current_time: Upper bound for the returned data. If omitted,
                the last emitted timestamp is used.

        Returns:
            DataFrame containing rows up to and including the requested time.

        Raises:
            ValueError: If no data has been emitted and no time is provided.
        """
        if current_time is None:
            if self._last_emitted_time is None:
                raise ValueError("No data has been emitted yet.")
            current_time = self._last_emitted_time

        return self.data.loc[self.data.index <= current_time].copy()

    @property
    def last_packet(self) -> pd.DataFrame | None:
        """Return the most recent data packet emitted by the simulator."""
        if self._last_packet is None:
            return None
        return self._last_packet.copy()

    def _extract_new_data(self, current_time: dt.datetime) -> pd.DataFrame:
        """Internal helper to retrieve newly accessible data."""
        if self._last_emitted_time is None:
            mask = self.data.index <= current_time
        else:
            mask = (self.data.index > self._last_emitted_time) & (
                self.data.index <= current_time
            )
        return self.data.loc[mask]
    