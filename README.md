# MT5 Manual Trading Signal Generator

A conservative, rule-based signal generator for discretionary forex day traders. This tool analyzes market conditions and outputs manual trading signals - it does not execute trades automatically.

## Important Disclaimer

**This software generates trading signals only. It does NOT place trades automatically.**

Trading forex carries substantial risk of capital loss. This software is provided for educational purposes only and is not financial advice. You are solely responsible for your trading decisions and their outcomes.

Always start with a demo account and never risk money you cannot afford to lose.

## What This Does

This program connects to MetaTrader 5, analyzes the current market using multiple technical indicators, and outputs a trading signal if all conditions are met. If any condition fails, it outputs "NO TRADE" with an explanation of which filters were not satisfied.

The signal includes entry price, stop loss, take profit, and detailed reasoning based on the current market structure.

## Features

- Multi-indicator analysis (EMA, RSI, ATR, VWAP, swing structure)
- Conservative validation requiring all conditions to pass
- Session filtering (London and New York hours only)
- Automatic spread checking
- Signal cooldown to prevent overtrading
- CSV logging for trade journaling
- Comprehensive error handling
- No automated trade execution

## Requirements

- Python 3.10 or higher
- MetaTrader 5 terminal installed and running
- Active connection to a Pepperstone account (or other MT5 broker)

## Installation

Install the required Python packages:

```bash
pip install MetaTrader5 pandas numpy
```

## Quick Start

1. Make sure MetaTrader 5 is open and logged in to your account
2. Run the script:

```bash
python mt5_signal_generator.py
```

3. Review the signal output
4. If you receive a BUY signal, evaluate it carefully before manually entering the trade
5. If you receive NO TRADE, review which conditions were not met

The script will create a file called `mt5_signals.csv` to log all signals for your review.

## How It Works

The signal generator uses a strict validation process where ALL of the following conditions must be satisfied:

1. **Cooldown Timer** - Minimum time between signals to prevent spam
2. **Spread Check** - Bid-ask spread must be below maximum threshold
3. **Session Filter** - Only generates signals during London or New York sessions
4. **Trend Alignment** - EMA 20 must be above EMA 50, price above both
5. **Momentum Check** - RSI must be between 50 and 70
6. **Institutional Support** - Price must be above VWAP
7. **Volatility Filter** - ATR must exceed minimum threshold
8. **Market Structure** - Recent price action must show a higher low pattern

If any single condition fails, the signal is rejected and the reason is displayed.

## Risk Management

The program calculates risk management levels automatically:

- **Entry**: Current market price
- **Stop Loss**: The safer of (1) most recent swing low or (2) entry minus one ATR
- **Take Profit**: Entry plus twice the risk distance (1:2 risk-reward ratio)

You should verify these levels make sense before entering any trade.

## Configuration

All configurable parameters are in the `TradingConfig` class near the top of the script. You can modify:

- Trading symbol (default: EURUSD)
- Timeframe (default: M5)
- Indicator periods (EMA, RSI, ATR)
- Filter thresholds (RSI range, minimum ATR)
- Risk-reward ratio
- Session times
- Cooldown period
- Maximum spread

See `DOCUMENTATION.md` for detailed explanations of each parameter.

See `SAMPLE_CONFIGURATIONS.md` for pre-built configurations for different trading styles.

## Understanding the Output

When you run the script, you'll see a formatted signal that includes:

- Symbol and timeframe
- Current session (London, NY, or overlap)
- Signal type (BUY or NO TRADE)
- Entry, stop loss, and take profit levels
- Risk in pips
- Trend status
- Current indicator values
- Detailed reasoning for the signal

If the signal is NO TRADE, you'll see a list of which conditions were not satisfied.

## Documentation

- `README.md` - This file, general overview
- `QUICK_START.md` - Get started in 5 minutes
- `DOCUMENTATION.md` - Complete technical documentation
- `SAMPLE_CONFIGURATIONS.md` - Example configurations for different trading styles

Read these files in order if you're new to the tool.

## Safety Features

This program includes multiple safety features:

- Cannot place trades (no MT5 trading API functions are used)
- Validates data completeness before calculations
- Checks spread before generating signals
- Enforces cooldown period between signals
- Only trades during high-liquidity sessions
- Gracefully handles MT5 disconnections
- Logs all activity for review

## Limitations

This tool:

- Uses only historical price data (indicators inherently lag)
- Does not account for fundamental analysis or news events
- Analyzes one symbol at a time
- Is designed for intraday trading on M5 timeframe (though configurable)
- Works best in trending markets, struggles in choppy conditions
- Has not been backtested on years of historical data

## Common Issues

**"MT5 initialization failed"**
Make sure MetaTrader 5 is open and you're logged in to your account.

**"Symbol not found"**
Enable the symbol in MT5's Market Watch (View > Market Watch, then right-click > Show All).

**Always getting "NO TRADE"**
This is normal and expected. The system is conservative by design. Most market conditions do not offer good risk-reward setups.

**"Insufficient data"**
Open a chart for the symbol in MT5 and scroll back to load more historical data.

See `DOCUMENTATION.md` for more troubleshooting help.

## Best Practices

- Always test on a demo account first (minimum 2 weeks)
- Check an economic calendar before trading
- Never risk more than 1-2% of your account per trade
- Keep a trading journal (the CSV log helps with this)
- Don't force trades - wait for proper setups
- Understand each indicator before trading live
- Set a maximum daily loss limit and stick to it

## Performance Expectations

Be realistic about what this tool can do:

- Most signals will be NO TRADE (this is intentional)
- Win rates typically range from 40-60% depending on configuration
- The tool helps with discipline, not magic predictions
- Consistent small profits over time, not huge one-off wins
- Your execution and discipline matter as much as the signals

## Contributing

This is an educational project. The core philosophy (safety, transparency, conservative approach) will be maintained in any modifications.

## Version History

**Version 1.0** (January 31, 2026)
- Initial release
- Multi-indicator signal generation
- Conservative default settings
- Comprehensive documentation
- CSV logging

## License

This software is provided for educational purposes only. See LICENSE file for terms.

You may use this for personal trading (demo or live accounts) and modify it for your own use. You may not sell, redistribute, or remove safety features.

## Final Notes

This signal generator is a tool for learning and developing disciplined trading habits. It will not make you rich overnight, but it can help you understand technical analysis, practice patience, and build a systematic approach to trading.

The real edge in trading comes from emotional control, discipline, risk management, and continuous learning. This tool assists with discipline and analysis, but the rest is up to you.

Trade safely and responsibly.
