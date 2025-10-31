
# Deucalion

Author - *Max Beinlich* for **Prometheus Capital**, **University of Amsterdam**

Modular quantitative trading and testing framework for Prometheus Capital.

-----

## Overview

This framework is modular framework designed for testing and executing quantitative trading strategies. To effectively test and compare strategies we require a standardized and reliable system, which at the same time allows for a high degree of customizability. To achieve this, we construct a modular system built on three separate layers, each extendable to accommodate unique use-cases.

From the bottom up:
1. Layer 1 - The **Client layer** implements data interaction procedures via request and callback methods. 
2. Layer 2 - The **Engine layer** maintains state, config and facilitates broker interactions via Client instance.
3. Layer 3 - The **Strategy layer** implements the users trading strategy and supporting callback methods.

##### Client Layer 

The Client layer refers to all classes related to data injections. In the future we will build upon this layer to implement API interfaces for any relevant data sources (e.g. QuiverQuant, IBKR, Alpaca, etc.). Currently, we construct a Simulator client as a means to generate synthetic data to use for testing. 

The following classes are part of the client layer to facilitate data injection: 
- Client - superclass for implementing clients
- Simulator - subclass of Client, simulates market data with request structure

##### Engine Layer

The Engine layer covers all classes handling state maintenance. The primary class here is the Engine which keeps an updates instance of the current portfolio and facilitates broker interaction either as simulation or once implemented by leveraging a broker specific client instance. Furthermore, the Engine generates an event record to track state change over time and which will then be used to evaluate strategy performance.

The following classes are part of the engine layer to handle state maintenance:
- Engine - superclass for implementing engines
- BacktestEngine - subclass of Engine, handles portfolio state and order execution for backtesting.
- Portfolio - dataclass representative of a single portfolio of active positions
- Position - dataclass representative of a single asset position
- PortfolioEvent - dataclass used to capture any portfolio updates (trade, stock splits, option expiry, etc.)

##### Strategy Layer

The Strategy layer is used by a Deucalion user to implement trading strategies, through interaction via an engine instance and client callbacks.

*This class still needs to be implemented.*


-----

## System Design

The three now established layers enable an end user to leverage the framework to implement fully unique and modular strategies - something that a lot of backtesting and execution frameworks struggle with for sake of standardization.

The following design is proposed for interaction between the layers:

1. While initializing a Strategy, the user creates a Client instance for the desired API and passes to an initialization the appropriate Engine.
2. Using the engine client, the strategy subscribes to relevant callback methods.
3. The strategy generates orders which are passed to the Engine.

A small snippet of pseudo-code gives a better imagine of the proposed design:

```python
class Strategy:
	
	def __init__(self, ...):
		ibkr = IBKRClient(...)
		
		ibkr.subscribe("tick", self.on_tick)
		self.engine = IBKREngine(ibkr, config, ...)
		
	def on_tick(self, tick):
		rsi = self.compute_rsi(tick)
		if rsi > 80:
			self.engine.submit_order(Order("SELL"))
		elif rsi < 20:
			self.engine.submit_order(Order("BUY"))

	def compute_rsi(self, tick):
		...
		
```


-----

## Backtesting and Simulation

For the MVP version of Deucalion we focus on backtesting functionality as proof of concept. This will be achieved by building relevant classes within the three system design layers to imitate live data injection. Functionality is split in two relevant classes: the Simulator and BacktestingEngine.

The **Simulator** is a client subclass used to simulate historical data by adhering to a state simulated clock. A Simulator instance takes a **SimulatedClock** instance and a timestamp indexed dataset as a pandas data frame. As we progress the simulated clock in the desired interval, simulators will emit the most recent datapoint from their dataset via callback function. We can instantiate separate simulators for different datasets using the same simulated clock.

The **BacktestingEngine** is an Engine subclass implementing standard functionality, however also simulating broker order execution according to specified config (In the future, we may consider a local LOB instance utilizing L2 data).   