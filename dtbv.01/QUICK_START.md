# Quick Start Guide - MT5 Signal Generator

## 5-Minute Setup

### Step 1: Install Python Packages (One-Time Setup)
```bash
pip install MetaTrader5 pandas numpy
```

### Step 2: Start MetaTrader 5
1. Open MT5 application
2. Login to your Pepperstone account
3. Verify "Connected" status in bottom-right corner
4. Keep MT5 running

### Step 3: Run the Script
```bash
python mt5_signal_generator.py
```

### Step 4: Interpret the Output

**If you see "BUY SIGNAL":**
1. Read the entire reasoning section
2. Verify the setup on your charts
3. If you agree, manually enter the trade in MT5:
   - Entry: Market order near signal price
   - Stop Loss: EXACTLY as shown
   - Take Profit: EXACTLY as shown

**If you see "NO TRADE":**
- This is NORMAL and GOOD
- Review which conditions failed
- Wait for better conditions
- Do NOT force trades

---

## Example Run Output

### Successful Signal
```
✓ MT5 initialized successfully
✓ Connected to account: 12345678
  Server: Pepperstone-Demo
  Balance: 10000.0 USD
✓ Symbol EURUSD validated
  Spread: 4 points
  Digits: 5

✓ Configuration loaded
  Symbol: EURUSD
  Timeframe: M5
  EMA: 20/50
  RSI: 14
  Risk:Reward: 1:2.0
  News Filter: ENABLED

✓ Retrieved 200 bars of data
✓ Indicators calculated

================================================================================
MT5 MANUAL TRADING SIGNAL
================================================================================
SIGNAL:          BUY
ENTRY:           1.10500
STOP LOSS:       1.10420
TAKE PROFIT:     1.10660
RISK (pips):     8.0
...
[Full signal details printed here]
```

### No Trade Example
```
SIGNAL:          NO TRADE
FAILED CONDITIONS:
  ✗ RSI out of range (72.4 not in 50-70)
  ✗ Price below VWAP (Price=1.10400, VWAP=1.10450)
```

**Interpretation**: Market is overbought and lacking institutional support. WAIT.

---

## Daily Trading Workflow

### Morning Routine (Before Market Open)
1. Check Forex Factory calendar: https://www.forexfactory.com/calendar
2. Note high-impact USD/EUR news for the day
3. Plan trading hours around news (avoid trading 30 min before/after)

### During Trading Hours
1. Run script when ready to scan for setups
2. Review signal carefully
3. If BUY signal:
   - Cross-reference with your charts
   - Check for nearby support/resistance
   - Verify no news in next 30 minutes
   - If all looks good, execute manually
4. If NO TRADE:
   - Review failed conditions
   - Wait 30 minutes (cooldown)
   - Run again

### After Trading
1. Review `mt5_signals.csv` log file
2. Update your trading journal
3. Calculate daily P&L
4. Note lessons learned

---

## Configuration Quick Reference

**Location**: Open `mt5_signal_generator.py` and find the `TradingConfig` class (near top).

### Common Adjustments

**1. Change Trading Pair:**
```python
SYMBOL = "GBPUSD"  # or "USDJPY", "XAUUSD", etc.
```

**2. Make More Conservative (fewer signals):**
```python
RSI_LOWER = 55  # Was 50
RSI_UPPER = 65  # Was 70
MIN_ATR_MULTIPLIER = 0.00015  # Was 0.0001
RISK_REWARD_RATIO = 3.0  # Was 2.0
```

**3. Make Less Conservative (more signals):**
```python
RSI_LOWER = 45  # Was 50
RSI_UPPER = 75  # Was 70
MIN_ATR_MULTIPLIER = 0.00008  # Was 0.0001
```

**4. Disable News Filter (trade during news - RISKY):**
```python
ENABLE_NEWS_FILTER = False  # Was True
```

**5. Adjust Cooldown:**
```python
COOLDOWN_MINUTES = 15  # Was 30 (more frequent signals)
COOLDOWN_MINUTES = 60  # Was 30 (less frequent signals)
```

---

## Understanding Your CSV Log

**Location**: `mt5_signals.csv` (created in same folder as script)

**Columns:**
- **Timestamp**: When signal was generated
- **Symbol**: Trading pair
- **Signal**: BUY or NO TRADE
- **Entry**: Suggested entry price
- **StopLoss**: Calculated stop loss
- **TakeProfit**: Calculated take profit
- **RiskPips**: How many pips at risk
- **Session**: London, NY, or Overlap
- **Reasoning**: Why signal was generated

**Use this to:**
- Track which setups you took
- Calculate win rate over time
- Identify best trading sessions
- Learn which indicators matter most

**Example CSV Entry:**
```
Timestamp,Symbol,Signal,Entry,StopLoss,TakeProfit,RiskPips,Session,Reasoning
2026-01-31 14:35:00,EURUSD,BUY,1.10500,1.10420,1.10660,8.0,LONDON_NY_OVERLAP,"Uptrend confirmed; RSI at 58.3; Price above VWAP; ..."
```

---

## Checklist Before First Live Trade

- [ ] Tested on demo account for at least 1 week
- [ ] Understand what each indicator does
- [ ] Can calculate stop loss and take profit manually
- [ ] Know how to place manual orders in MT5
- [ ] Defined maximum daily loss limit (e.g., $100)
- [ ] Position size calculated (risk only 1-2% per trade)
- [ ] Economic calendar checked for today
- [ ] Trading journal prepared
- [ ] Emotional state: calm and patient

**If ANY box is unchecked, continue on demo.**

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| "MT5 initialization failed" | Open MT5, login, verify connected |
| "Symbol not found" | MT5 → Market Watch → right-click → Show All → find EURUSD |
| Always "NO TRADE" | Normal! Market must meet ALL conditions. Be patient. |
| "Insufficient data" | Open EURUSD M5 chart in MT5, scroll back to load history |
| "Spread too wide" | Check for news events. Wait 30 min. Safety feature working. |
| Signals don't match my chart | Verify indicator periods match. Use bid price on chart. |

---

## Important Reminders

⚠️ **This is NOT a get-rich-quick system**
- Most signals will be NO TRADE (this is good)
- Winning trades and losing trades are both normal
- Focus on process, not outcome of individual trades

⚠️ **You are in control**
- Script suggests, YOU decide
- Script calculates, YOU execute
- Script logs, YOU review and learn

⚠️ **Risk management is everything**
- Never risk more than 1-2% per trade
- Use the stop loss - no exceptions
- If you lose your daily limit, STOP trading

⚠️ **News events override everything**
- Check calendar EVERY day
- Avoid trading 30 min before/after high-impact news
- When in doubt, stay out

---

## Next Steps

1. **Week 1-2**: Demo account only
   - Run script daily
   - Track all signals in journal
   - Don't focus on profit, focus on following rules

2. **Week 3-4**: Analysis phase
   - Review your CSV log
   - Calculate win rate
   - Identify best trading sessions
   - Tweak configuration if needed

3. **Week 5+**: Consider live (if profitable on demo)
   - Start with minimum position size
   - Trade only 1-2 setups per day
   - Increase size slowly as consistency improves

---

## Support Resources

- **MT5 Tutorial**: https://www.metatrader5.com/en/terminal/help
- **Forex Factory Calendar**: https://www.forexfactory.com/calendar
- **Pepperstone Support**: https://support.pepperstone.com/

---

## Your Trading Rules (Fill This Out)

**Maximum Daily Loss**: $_______ (stop trading if reached)

**Maximum Trades Per Day**: _______ (prevent overtrading)

**Position Size**: _______ lots (based on account size and risk tolerance)

**Trading Hours**: _______ to _______ (when you're most focused)

**No-Trade Zones**:
- [ ] 30 min before/after high-impact news
- [ ] When emotionally upset
- [ ] When tired or distracted
- [ ] After hitting daily loss limit

**Signature**: _________________ **Date**: _________

**Print this out and keep it visible while trading.**

---

*Good luck, stay disciplined, and remember: protecting capital is job #1.*
