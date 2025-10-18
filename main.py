
from deucalion import Portfolio
from deucalion import Position


def main():
    aapl = Position("AAPL", 10, 1000)
    tsla = Position("TSLA", 20, 1000)

    portfolio = Portfolio(1000, set([aapl, tsla]))

    print(portfolio["AAPL"])


if __name__ == "__main__":
    main()