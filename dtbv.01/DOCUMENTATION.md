# MT5 Manual Trading Signal Generator - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Indicator Explanations](#indicator-explanations)
4. [Strategy Logic](#strategy-logic)
5. [Configuration Guide](#configuration-guide)
6. [Usage Instructions](#usage-instructions)
7. [Output Interpretation](#output-interpretation)
8. [Safety Features](#safety-features)
9. [Limitations & Disclaimers](#limitations--disclaimers)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This is a **conservative, rule-based signal generator** for manual day trading. It does NOT execute trades automatically. Instead, it analyzes market conditions and outputs signals that YOU must evaluate and execute manually.

### Key Principles
- **Safety First**: Multiple validation layers prevent false signals
- **No Automation**: Signals only - you maintain full control
- **Deterministic**: Same market conditions = same signal
- **Conservative**: When in doubt, outputs NO TRADE
- **Transparent**: Every decision is logged and explained

---

## Installation & Setup

### Prerequisites

1. **MetaTrader 5**
   - Download from: https://www.metatrader5.com/
   - Install and login to your Pepperstone account
   - Ensure MT5 is running before starting the script

2. **Python 3.10+**
   - Download from: https://www.python.org/
   - During installation, check "Add Python to PATH"

3. **Required Python Package**
   ```bash
   pip install MetaTrader5
   pip install pandas
   pip install numpy
   ```

### Installation Steps

1. **Save the Script**
   - Save `mt5_signal_generator.py` to a folder (e.g., `C:\Trading\`)

2. **Verify MT5 is Running**
   - Open MT5
   - Login to your Pepperstone account
   - Keep MT5 open while running the script

3. **Test the Installation**
   ```bash
   python mt5_signal_generator.py
   ```

4. **Expected First Run**
   - Script should connect to MT5
   - Display account information
   - Generate a signal (likely NO TRADE on first run)
   - Create `mt5_signals.csv` log file

---

## Indicator Explanations

### 1. Exponential Moving Average (EMA)

**What it is:**
A trend-following indicator that gives more weight to recent prices.

**How it's used:**
- **EMA 20 (Fast)**: Reacts quickly to price changes
- **EMA 50 (Slow)**: Shows longer-term trend direction
- **Signal**: Price and EMA 20 must be above EMA 50 for uptrend confirmation

**Why it matters:**
EMAs help filter out noise and identify the dominant trend direction. Trading with the trend significantly improves probability of success.

**Mathematical formula:**
```
EMA(t) = Price(t) × α + EMA(t-1) × (1 - α)
where α = 2 / (period + 1)
```

### 2. Relative Strength Index (RSI)

**What it is:**
A momentum oscillator measuring the speed and magnitude of price movements.

**How it's used:**
- Range: 0-100
- **For longs**: Must be between 50-70
- Below 50: Weak momentum
- Above 70: Overbought (risk of reversal)

**Why it matters:**
RSI ensures we enter with momentum on our side, but not when the market is overextended (which leads to pullbacks).

**Mathematical formula:**
```
RS = Average Gain / Average Loss (over 14 periods)
RSI = 100 - (100 / (1 + RS))
```

### 3. Average True Range (ATR)

**What it is:**
A volatility indicator measuring the average range of price movement.

**How it's used:**
- **Volatility filter**: ATR must exceed minimum threshold
- **Stop loss calculation**: Stop = Entry - (ATR × 1.0)
- High ATR = trending market (good for trading)
- Low ATR = choppy/ranging market (avoid)

**Why it matters:**
Low volatility markets generate many false signals and small profits. ATR ensures we only trade when there's sufficient movement to justify the risk.

**Mathematical formula:**
```
True Range = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
ATR = Moving Average of True Range over 14 periods
```

### 4. Volume Weighted Average Price (VWAP)

**What it is:**
The average price weighted by volume - essentially where institutions are positioned.

**How it's used:**
- Price must be above VWAP for long signals
- VWAP acts as dynamic support/resistance
- Below VWAP = bearish pressure
- Above VWAP = bullish pressure

**Why it matters:**
Institutional traders (banks, hedge funds) use VWAP for execution. Trading above VWAP means we're aligned with institutional flow.

**Mathematical formula:**
```
VWAP = Σ(Typical Price × Volume) / Σ(Volume)
where Typical Price = (High + Low + Close) / 3
```

### 5. Market Structure (Swing Analysis)

**What it is:**
Analysis of recent swing highs and lows to identify trend structure.

**How it's used:**
- Identifies the most recent "higher low" in an uptrend
- Used for intelligent stop loss placement
- Confirms trend continuation vs. reversal

**Why it matters:**
Placing stops below recent structure reduces the chance of getting stopped out by normal market noise while still protecting capital.

---

## Strategy Logic

### Multi-Layer Validation System

The signal generator uses a **fail-safe approach**: ALL conditions must pass, or the signal is rejected.

```
┌─────────────────────────────────────┐
│  CONDITION 1: Cooldown Timer        │ ← Prevents signal spam
├─────────────────────────────────────┤
│  CONDITION 2: Spread Check          │ ← Ensures low transaction costs
├─────────────────────────────────────┤
│  CONDITION 3: Session Filter        │ ← Only trade high-liquidity hours
├─────────────────────────────────────┤
│  CONDITION 4: News Filter           │ ← Manual override for news events
├─────────────────────────────────────┤
│  CONDITION 5: Trend Alignment       │ ← EMA 20 > EMA 50, Price > both
├─────────────────────────────────────┤
│  CONDITION 6: RSI Range             │ ← 50 < RSI < 70 (momentum without overbought)
├─────────────────────────────────────┤
│  CONDITION 7: VWAP Confirmation     │ ← Price > VWAP (institutional support)
├─────────────────────────────────────┤
│  CONDITION 8: Volatility Check      │ ← ATR > minimum (avoid chop)
├─────────────────────────────────────┤
│  CONDITION 9: Market Structure      │ ← Higher low pattern confirmed
└─────────────────────────────────────┘
          ↓ ALL CONDITIONS MET
    ┌──────────────────┐
    │  BUY SIGNAL      │
    │  + Entry Price   │
    │  + Stop Loss     │
    │  + Take Profit   │
    └──────────────────┘
```

### Risk Management Calculation

**Entry**: Current market price

**Stop Loss**: Conservative choice between:
- Most recent swing low (structural support)
- Entry - (ATR × 1.0) (volatility-based)
→ Whichever is SAFER (higher price for longs)

**Take Profit**: Entry + (Risk × 2.0)
- Fixed 1:2 Risk:Reward ratio
- If you risk 10 pips, target 20 pips profit

**Example Calculation:**
```
Current Price: 1.10500
ATR: 0.00080 (8 pips)
Swing Low: 1.10420

Stop Loss = max(1.10420, 1.10500 - 0.00080) = 1.10420 (swing low is safer)
Risk = 1.10500 - 1.10420 = 0.00080 (8 pips)
Take Profit = 1.10500 + (0.00080 × 2) = 1.10660 (16 pips)
Risk:Reward = 1:2
```

---

## Configuration Guide

### User-Modifiable Parameters

All configuration is in the `TradingConfig` class at the top of the script. Here's what you can safely modify:

#### Market Settings

```python
SYMBOL = "EURUSD"  # Trading pair (must be available in MT5)
TIMEFRAME = mt5.TIMEFRAME_M5  # Chart timeframe
```

**Available timeframes:**
- `mt5.TIMEFRAME_M1` - 1 minute
- `mt5.TIMEFRAME_M5` - 5 minutes (recommended for day trading)
- `mt5.TIMEFRAME_M15` - 15 minutes
- `mt5.TIMEFRAME_M30` - 30 minutes
- `mt5.TIMEFRAME_H1` - 1 hour
- `mt5.TIMEFRAME_H4` - 4 hours
- `mt5.TIMEFRAME_D1` - Daily

**Caution**: Lower timeframes (M1) generate more signals but with more noise. Higher timeframes (H4, D1) are more reliable but slower.

#### Indicator Periods

```python
EMA_FAST = 20  # Fast EMA period (8-21 typical range)
EMA_SLOW = 50  # Slow EMA period (50-200 typical range)
RSI_PERIOD = 14  # RSI calculation period (standard)
ATR_PERIOD = 14  # ATR calculation period (standard)
VWAP_PERIOD = 100  # Lookback for rolling VWAP
```

**Guidelines:**
- Shorter EMAs = more signals, more whipsaws
- Longer EMAs = fewer signals, more reliable
- Standard RSI/ATR is 14 periods (don't change unless you have good reason)

#### Filter Thresholds

```python
RSI_LOWER = 50  # Minimum RSI for long entries
RSI_UPPER = 70  # Maximum RSI (avoid overbought)
MIN_ATR_MULTIPLIER = 0.0001  # Minimum volatility to trade
```

**To make MORE conservative** (fewer signals, higher quality):
- Increase `RSI_LOWER` to 55
- Decrease `RSI_UPPER` to 65
- Increase `MIN_ATR_MULTIPLIER` to 0.00015

**To make LESS conservative** (more signals, accept more risk):
- Decrease `RSI_LOWER` to 45
- Increase `RSI_UPPER` to 75
- Decrease `MIN_ATR_MULTIPLIER` to 0.00008

#### Risk Management

```python
RISK_REWARD_RATIO = 2.0  # Take profit = 2x stop distance
ATR_STOP_MULTIPLIER = 1.0  # Stop loss buffer
```

**Common ratios:**
- Conservative: 3.0 (risk 10 pips to make 30)
- Balanced: 2.0 (risk 10 pips to make 20)
- Aggressive: 1.5 (risk 10 pips to make 15)

**Stop multiplier:**
- Tight: 0.8 (risk more whipsaws)
- Standard: 1.0
- Wide: 1.5 (fewer whipsaws, larger losses)

#### Session Filters (UTC Times)

```python
LONDON_START = time(7, 0)   # 7:00 AM UTC
LONDON_END = time(16, 0)    # 4:00 PM UTC
NY_START = time(12, 0)      # 12:00 PM UTC (Noon)
NY_END = time(21, 0)        # 9:00 PM UTC
```

**Notes:**
- These are in UTC time (match to your MT5 server time)
- London/NY overlap (12:00-16:00 UTC) is most liquid
- Asian session typically has lower volatility (not enabled by default)

#### Signal Management

```python
COOLDOWN_MINUTES = 30  # Minimum time between signals
MAX_SPREAD_PIPS = 2.0  # Reject if spread too wide
```

**Cooldown:**
- Higher value = fewer signals (less spam)
- Lower value = more signals (might repeat on same setup)

**Max spread:**
- Pepperstone EURUSD typical spread: 0.1-0.6 pips
- 2.0 pips is very conservative (protects against news spikes)

#### News Filter

```python
ENABLE_NEWS_FILTER = True  # Manual toggle
```

**Important:**
- Set to `True`: Program reminds you about news filter
- Set to `False`: Override news filter (trade during news)
- **Always check economic calendar before trading**

---

## Usage Instructions

### Basic Workflow

1. **Check Economic Calendar**
   - Visit https://www.forexfactory.com/calendar
   - Note any high-impact USD or EUR news in the next hour
   - Avoid trading 30 minutes before and after major news

2. **Start MT5**
   - Login to your Pepperstone account
   - Ensure EURUSD chart is visible
   - Keep MT5 running

3. **Run the Script**
   ```bash
   python mt5_signal_generator.py
   ```

4. **Review the Signal**
   - Read the entire output carefully
   - If "BUY SIGNAL": evaluate the reasoning
   - If "NO TRADE": review failed conditions

5. **Manual Decision**
   - This is YOUR decision point
   - Consider:
     * Do you agree with the analysis?
     * Is there news coming up?
     * What's your risk tolerance today?
     * Do you have other open positions?

6. **If You Decide to Trade:**
   - Open MT5
   - Place order manually:
     * Entry: As close to signal price as possible
     * Stop Loss: EXACTLY as shown in signal
     * Take Profit: EXACTLY as shown in signal
   - Document your trade in a journal

7. **Monitor the Trade**
   - The script does NOT manage your trade
   - You must monitor and close manually
   - Consider trailing stops if profitable

### Running on a Schedule

**Option 1: Manual (Recommended for Beginners)**
- Run the script when you're ready to trade
- Review each signal carefully
- Full control and learning opportunity

**Option 2: Scheduled Task (Advanced)**
- Set up a Windows Task Scheduler or cron job
- Run every 5 minutes during trading hours
- Review signal log file periodically
- Still requires manual trade execution

**Windows Task Scheduler Example:**
```
Program: python.exe
Arguments: C:\Trading\mt5_signal_generator.py
Start in: C:\Trading\
Trigger: Repeat every 5 minutes from 7:00 AM to 9:00 PM
```

---

## Output Interpretation

### Example Signal Output

```
================================================================================
MT5 MANUAL TRADING SIGNAL
================================================================================
SYMBOL:          EURUSD
TIMEFRAME:       M5
TIMESTAMP:       2026-01-31 14:35:00
SESSION:         LONDON_NY_OVERLAP
--------------------------------------------------------------------------------
SIGNAL:          BUY
ENTRY:           1.10500
STOP LOSS:       1.10420
TAKE PROFIT:     1.10660
RISK (pips):     8.0
--------------------------------------------------------------------------------
TREND STATUS:    UPTREND CONFIRMED
--------------------------------------------------------------------------------
INDICATOR VALUES:
  EMA 20:        1.10480
  EMA 50:        1.10420
  RSI:           58.3
  ATR:           0.00082
  VWAP:          1.10450
  Current Price: 1.10500
--------------------------------------------------------------------------------
REASONING:
  ✓ Uptrend confirmed (EMA20 > EMA50, price above both)
  ✓ RSI healthy at 58.3 (momentum without overbought)
  ✓ Price above VWAP (institutional support)
  ✓ ATR shows sufficient volatility (0.00082)
  ✓ Higher low pattern confirmed at 1.10420
  ✓ Trading during LONDON_NY_OVERLAP session (high liquidity)
  ✓ Spread acceptable at 0.4 pips
  ✓ Risk:Reward = 1:2
================================================================================

⚠️  DISCLAIMER: This is NOT a buy/sell recommendation.
    Execute trades at your own discretion and risk.
================================================================================
```

### What Each Section Means

**Header Information:**
- **SYMBOL/TIMEFRAME**: What market and chart period
- **TIMESTAMP**: When this signal was generated
- **SESSION**: Which trading session (affects liquidity)

**Signal Details:**
- **SIGNAL**: BUY or NO TRADE
- **ENTRY**: Price to enter (use market order or limit near this price)
- **STOP LOSS**: Where to place your stop (non-negotiable - must use this)
- **TAKE PROFIT**: Where to take profit (can adjust based on price action)
- **RISK (pips)**: How many pips you're risking

**Trend Status:**
- Confirms overall market direction
- "UPTREND CONFIRMED" = all trend filters passed

**Indicator Values:**
- Current snapshot of all indicators
- Use this to verify the signal makes sense
- Compare to your own charts

**Reasoning:**
- Explains WHY the signal was generated
- Each line represents a condition that passed
- Read this carefully - it's your quality check

### NO TRADE Example

```
SIGNAL:          NO TRADE
ENTRY:           0.00000
STOP LOSS:       0.00000
TAKE PROFIT:     0.00000
RISK (pips):     0.0
--------------------------------------------------------------------------------
FAILED CONDITIONS:
  ✗ RSI out of range (72.4 not in 50-70)
  ✗ ATR too low (0.00005 < 0.0001)
```

**Interpretation:**
- Market is overbought (RSI > 70)
- Volatility is too low (choppy conditions)
- **Action**: Wait for better conditions, do NOT force a trade

---

## Safety Features

### 1. No Automated Trading
- Script physically cannot place trades
- MT5 API trading functions are NOT used
- You maintain 100% control

### 2. Graceful Error Handling
- If MT5 disconnects → safe error message
- If data is missing → NO TRADE with explanation
- If spread spikes → signal rejected
- If any unexpected error → program stops safely

### 3. Cooldown Timer
- Prevents signal spam
- 30-minute default gap between signals
- Avoids emotional rapid-fire entries

### 4. Spread Protection
- Monitors real-time bid/ask spread
- Rejects signals if spread > 2.0 pips
- Protects you from poor execution during volatility spikes

### 5. Data Validation
- Requires minimum 200 bars of history
- Checks for complete candles
- Ensures all indicators can be calculated
- No extrapolation or guessing

### 6. Session Filtering
- Only signals during high-liquidity sessions
- London: 7:00-16:00 UTC
- New York: 12:00-21:00 UTC
- Avoids thin markets (reduced slippage risk)

### 7. Comprehensive Logging
- Every signal saved to `mt5_signals.csv`
- Timestamp, entry, stops, reasoning all recorded
- Enables performance tracking and backtesting

### 8. Conservative Default Settings
- Tight RSI range (50-70)
- Higher low pattern required
- 1:2 minimum risk:reward
- Multiple confirmation filters
- **Philosophy**: Miss signals rather than take bad ones

---

## Limitations & Disclaimers

### What This Program IS

✓ A **signal generation tool** based on technical analysis  
✓ A **learning aid** for understanding rule-based trading  
✓ A **journaling system** for tracking potential setups  
✓ A **time-saver** for scanning market conditions  

### What This Program IS NOT

✗ **Not a guaranteed profit system** - no such thing exists  
✗ **Not financial advice** - you are responsible for your decisions  
✗ **Not a replacement for education** - learn before you trade  
✗ **Not foolproof** - markets are unpredictable  
✗ **Not a "set and forget" solution** - requires active monitoring  

### Technical Limitations

1. **Historical Data Only**
   - Indicators use past prices
   - Cannot predict future with certainty
   - Lag is inherent in moving averages

2. **No Fundamental Analysis**
   - Ignores economic data
   - Doesn't account for central bank actions
   - No sentiment analysis

3. **Single Asset Focus**
   - Analyzes one symbol at a time
   - No correlation analysis across pairs
   - No portfolio-level risk management

4. **Intraday Only**
   - Designed for day trading (M5 timeframe)
   - Not optimized for scalping or swing trading
   - Signals expire quickly

5. **Market Condition Dependent**
   - Works best in trending markets
   - Struggles in choppy/ranging conditions
   - News events can invalidate signals instantly

### Risk Warnings

⚠️ **Trading Forex carries substantial risk of capital loss**

- Leverage magnifies both gains AND losses
- You can lose more than your initial deposit
- Past performance does not guarantee future results
- This script has NOT been backtested on years of data
- No optimization or forward testing has been performed

⚠️ **Only trade with money you can afford to lose**

⚠️ **Start with a demo account** until you're consistently profitable

⚠️ **Never risk more than 1-2% of your account per trade**

### Legal Disclaimer

This software is provided "AS IS" without warranty of any kind. The developer assumes no liability for:
- Trading losses
- Software errors or bugs
- Data accuracy issues
- MT5 connection problems
- Any direct or indirect damages

**You are solely responsible for your trading decisions.**

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "MT5 initialization failed"

**Cause**: MT5 not running or not logged in

**Solution**:
1. Open MetaTrader 5
2. Login to your Pepperstone account
3. Wait for "Connected" in bottom right
4. Run script again

---

#### 2. "Symbol EURUSD not found"

**Cause**: Symbol not enabled in Market Watch

**Solution**:
1. In MT5, press Ctrl+U (Market Watch)
2. Right-click → "Show All"
3. Find EURUSD and right-click → "Show"
4. Run script again

---

#### 3. "Insufficient data. Got 50 bars, need 200"

**Cause**: Not enough historical data loaded

**Solution**:
1. In MT5, open an EURUSD M5 chart
2. Scroll back to load more history
3. Wait 10 seconds for data to sync
4. Run script again

---

#### 4. "Spread too wide (5.2 pips > 2.0)"

**Cause**: Market volatility or news event

**Solution**:
- Check economic calendar for news releases
- Wait 30 minutes after news
- This is a safety feature working correctly
- If spread is consistently high, check your broker connection

---

#### 5. Script runs but always says "NO TRADE"

**Cause**: Market conditions don't meet all criteria (NORMAL)

**Solution**:
- Review "FAILED CONDITIONS" in output
- This is the script working as designed
- Don't force trades - wait for proper setups
- Consider running during London/NY overlap for more activity
- **Conservative is good** - quality over quantity

---

#### 6. "Error fetching market data"

**Cause**: MT5 connection interrupted

**Solution**:
1. Check MT5 is still connected (green bar in bottom right)
2. Check internet connection
3. Restart MT5 if necessary
4. Run script again

---

#### 7. CSV file not created

**Cause**: Permission issue or incorrect path

**Solution**:
1. Run script from a folder where you have write permissions
2. Don't run from Program Files (restricted)
3. Try running as Administrator (Windows)
4. Check `LOG_FILE` path in config

---

#### 8. Signals not matching my MT5 charts

**Possible causes**:
1. **Different indicator settings** - Verify EMA periods match
2. **Server time difference** - Script uses MT5 server time
3. **Data sync delay** - Wait a few seconds after candle close
4. **Bid vs Ask prices** - Script uses close price from MT5 data

**Solution**:
- Use the same indicator periods on your chart
- Compare indicator values (printed in output)
- Remember: Close price may differ slightly from current bid/ask

---

### Getting Help

If you encounter issues not covered here:

1. **Check the output carefully** - error messages are descriptive
2. **Verify MT5 connection** - most issues stem from MT5 connectivity
3. **Review configuration** - ensure settings are valid
4. **Check CSV log** - previous signals may provide clues
5. **Test with demo account first** - isolate software vs. account issues

---

## Best Practices for Use

### Before Trading

1. ✅ Test on demo account for at least 1 week
2. ✅ Verify you understand each indicator
3. ✅ Practice manual trade entry in MT5
4. ✅ Set up a trading journal
5. ✅ Define your maximum daily loss limit
6. ✅ Check economic calendar

### During Trading

1. ✅ Run script only when you can monitor trades
2. ✅ Never enter a trade blindly - verify the signal makes sense
3. ✅ Place stops EXACTLY as calculated (no "wider for safety")
4. ✅ Use proper position sizing (1-2% risk per trade)
5. ✅ Keep a trading log (CSV provides this)
6. ✅ Respect the cooldown - don't overtrade

### After Trading

1. ✅ Review your trades in the CSV log
2. ✅ Calculate win rate and average R:R
3. ✅ Identify patterns in failed trades
4. ✅ Adjust configuration if needed (conservatively)
5. ✅ Take breaks after losses (avoid revenge trading)
6. ✅ Celebrate discipline, not just profits

---

## Final Thoughts

This signal generator is a **tool**, not a magic solution. Like a hammer doesn't make you a carpenter, this script doesn't make you a profitable trader.

**The real work is:**
- Understanding WHY signals are generated
- Developing patience to wait for quality setups
- Managing emotions when trades go against you
- Continuous learning and improvement
- Discipline to follow your rules

**Use this script to:**
- Save time scanning markets
- Learn rule-based decision making
- Build a database of setups
- Develop consistency

**Remember:**
- The best traders take FEWER trades, not more
- NO TRADE is a valid (and often smart) decision
- Consistency beats occasional big wins
- Risk management is more important than entry signals

---

## Version History

- **v1.0** (2026-01-31): Initial release
  - Multi-indicator signal generation
  - Conservative default settings
  - Comprehensive safety features
  - CSV logging
  - Full documentation

---

## License & Usage

This script is provided for educational purposes only.

You may:
- Use on personal demo/live accounts
- Modify configuration parameters
- Study and learn from the code

You may not:
- Sell or redistribute this code
- Claim it as your own work
- Remove safety features
- Use for automated trading without understanding the risks

---

## Support & Feedback

This is a learning tool. Invest time in understanding it rather than expecting instant profits.

**Good luck, trade safely, and never risk what you can't afford to lose.**

---

*Disclaimer: This documentation is for educational purposes only and does not constitute financial advice. Trading carries risk.*
