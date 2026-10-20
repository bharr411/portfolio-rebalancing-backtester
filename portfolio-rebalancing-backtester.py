import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#Import Dependencies

# Backtest Settings
stockList = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'JPM', 'KO']
stocks = [stock for stock in stockList]
start_date = "2020-01-01"
end_date = "2026-01-01"
initialInvestment = 10_000

#Load adjusted prices to account for stock splits and dividends.
prices = yf.download(
    stocks,
    start=start_date,
    end=end_date,
    auto_adjust=True
)["Close"]

#Use chronological dates with prices available for every stock.
prices = prices.sort_index().dropna()

if prices.empty:
    raise ValueError("No complete price data was loaded.")


# Flag the first available trading day of each new month and quarter.
monthly_periods=prices.index.to_period("M")
quarterly_period = prices.index.to_period("Q")


# Leave the first day False: the initial allocation is handled separately.
monthly_rebalance = np.zeros(len(prices), dtype=bool)
quarterly_rebalance = np.zeros(len(prices), dtype=bool)
monthly_rebalance[1:] = monthly_periods[1:] != monthly_periods[:-1]
quarterly_rebalance[1:] = quarterly_period[1:] != quarterly_period[:-1]

#Start with equal dollar allocations, allowing fractional units
#This assumes no trading costs.
allocationPerStock = initialInvestment / len(prices.columns)
starting_prices = prices.iloc[0]
unitsHeld = allocationPerStock / starting_prices

#Keep units fixed throughout the buy-and-hold backtest.
holdings_values = prices.mul(unitsHeld, axis="columns")
portfolio_values = holdings_values.sum(axis=1)

def backtest_rebalancing(prices, rebalance_flags, initial_investment):
    """Simulate equal-weight rebalancing with fractional units and no costs."""
    number_of_stocks = len(prices.columns)
    units_held = (initial_investment / number_of_stocks) / prices.iloc[0]
    daily_values = []

    for day in range(len(prices)):
        current_prices = prices.iloc[day]
        portfolio_value = (units_held * current_prices).sum()

        if rebalance_flags[day]:
            # Trade at the scheduled day's close using the current value.
            target_allocation = portfolio_value / number_of_stocks
            target_units = target_allocation / current_prices
            units_to_trade = target_units - units_held
            units_held = units_held + units_to_trade

        # Without costs, trades change the allocation but not total value.
        daily_values.append(portfolio_value)

    return pd.Series(daily_values, index=prices.index)


monthly_values = backtest_rebalancing(
    prices, monthly_rebalance, initialInvestment
)
quarterly_values = backtest_rebalancing(
    prices, quarterly_rebalance, initialInvestment
)

# Verify the daily loop against the independently calculated baseline.
no_rebalance_flags = np.zeros(len(prices), dtype=bool)
baseline_check = backtest_rebalancing(
    prices, no_rebalance_flags, initialInvestment
)
np.testing.assert_allclose(
    baseline_check.to_numpy(), portfolio_values.to_numpy()
)

strategy_values = {
    "Buy and hold": portfolio_values,
    "Monthly rebalancing": monthly_values,
    "Quarterly rebalancing": quarterly_values,
}

# Report cumulative returns over the same period for each strategy.
print(f"Initial investment: ${initialInvestment:,.2f}")
print("Assumptions: fractional units, trades at close, no trading costs.")
for name, values in strategy_values.items():
    final_value = values.iloc[-1]
    total_return = (final_value / initialInvestment - 1) * 100
    print(f"\n{name}")
    print(f"Final portfolio value: ${final_value:,.2f}")
    print(f"Total return: {total_return:,.2f}%")


# Compare all three strategies with the initial investment.
plt.figure(figsize=(12, 6))
for name, values in strategy_values.items():
    plt.plot(values, label=name)
plt.axhline(
    initialInvestment,
    color="black",
    linestyle="--",
    label="Initial investment"
)

plt.title("Portfolio Strategy Comparison")
plt.xlabel("Date")
plt.ylabel("Portfolio value ($)")
plt.legend()
plt.tight_layout()
plt.show()
