# Portfolio Rebalancing Backtester

A Python project comparing buy-and-hold with monthly and quarterly equal-weight portfolio rebalancing.

The script downloads adjusted historical prices for AAPL, MSFT, NVDA, AMZN, JPM, and KO. Each strategy starts with $10,000 equally allocated across the stocks. It prints final portfolio values and total returns, then plots all three strategies.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python portfolio-rebalancing-backtester.py
```

An internet connection is required to download prices. Edit the stocks, dates, and initial investment near the top of the script to change the experiment.

## How it works

- Buy-and-hold keeps the initial units fixed.
- Monthly and quarterly strategies restore equal dollar allocations at the close of the first available trading day of each new period.
- A built-in check verifies that the daily simulation matches buy-and-hold when rebalancing is disabled.

## Assumptions and limitations

Fractional units are allowed. Adjusted prices account for splits and dividends, so holdings represent synthetic adjusted-price units. Trading costs, taxes, and slippage are excluded. Dates with missing prices for any stock are dropped.

The default period starts on January 1, 2020 and ends before January 1, 2026. Returns are cumulative, not annualised. This is a historical case study of a fixed selection of stocks, not evidence that the selection could have been made in advance.

## Next steps

Add trading costs, maximum drawdown, and a summary comparison table.
