# Sample Configurations for Different Trading Styles

This file shows example configurations for different trader profiles.
Copy the relevant configuration into the `TradingConfig` class in `mt5_signal_generator.py`.

---

## 1. Ultra-Conservative (Beginner Friendly)

**Profile**: New trader, wants highest quality signals only, willing to miss opportunities

```python
class TradingConfig:
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_M15  # Higher timeframe = less noise
    
    # Indicator parameters
    EMA_FAST = 20
    EMA_SLOW = 100  # Wider separation = stronger trend required
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 100
    
    # Filter thresholds (VERY TIGHT)
    RSI_LOWER = 55  # Higher = stronger momentum required
    RSI_UPPER = 65  # Lower = avoid overbought
    MIN_ATR_MULTIPLIER = 0.00015  # Higher = more volatile markets only
    
    # Risk management (CONSERVATIVE)
    RISK_REWARD_RATIO = 3.0  # Only trade if 3x reward potential
    ATR_STOP_MULTIPLIER = 1.5  # Wider stops = fewer whipsaws
    
    # Session filters (OVERLAP ONLY)
    LONDON_START = time(12, 0)  # Only trade London/NY overlap
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(16, 0)
    
    # Signal management
    COOLDOWN_MINUTES = 60  # One signal per hour max
    MAX_SPREAD_PIPS = 1.5  # Tight spread requirement
    
    # Data requirements
    MIN_BARS_REQUIRED = 250
    
    # Logging
    LOG_FILE = "mt5_signals_conservative.csv"
    ENABLE_NEWS_FILTER = True
```

**Expected Behavior**: Very few signals (1-2 per day max), but high win rate

---

## 2. Balanced (Recommended Default)

**Profile**: Intermediate trader, balance between signal frequency and quality

```python
class TradingConfig:
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_M5
    
    # Indicator parameters
    EMA_FAST = 20
    EMA_SLOW = 50
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 100
    
    # Filter thresholds (BALANCED)
    RSI_LOWER = 50
    RSI_UPPER = 70
    MIN_ATR_MULTIPLIER = 0.0001
    
    # Risk management (BALANCED)
    RISK_REWARD_RATIO = 2.0
    ATR_STOP_MULTIPLIER = 1.0
    
    # Session filters (LONDON + NY)
    LONDON_START = time(7, 0)
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(21, 0)
    
    # Signal management
    COOLDOWN_MINUTES = 30
    MAX_SPREAD_PIPS = 2.0
    
    # Data requirements
    MIN_BARS_REQUIRED = 200
    
    # Logging
    LOG_FILE = "mt5_signals.csv"
    ENABLE_NEWS_FILTER = True
```

**Expected Behavior**: 3-5 signals per day, balanced win rate

---

## 3. Aggressive (Experienced Traders Only)

**Profile**: Experienced trader, wants more opportunities, can handle more losing trades

```python
class TradingConfig:
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_M5
    
    # Indicator parameters
    EMA_FAST = 12  # Faster EMAs = more responsive
    EMA_SLOW = 26
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 100
    
    # Filter thresholds (LOOSER)
    RSI_LOWER = 45  # Lower = accept earlier entries
    RSI_UPPER = 75  # Higher = willing to chase
    MIN_ATR_MULTIPLIER = 0.00008  # Lower = trade in calmer markets too
    
    # Risk management (AGGRESSIVE)
    RISK_REWARD_RATIO = 1.5  # Lower target = higher win rate
    ATR_STOP_MULTIPLIER = 0.8  # Tighter stops = accept more whipsaws
    
    # Session filters (EXTENDED HOURS)
    LONDON_START = time(6, 0)  # Earlier start
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(22, 0)  # Later end
    
    # Signal management
    COOLDOWN_MINUTES = 15  # More frequent signals
    MAX_SPREAD_PIPS = 2.5  # Willing to accept wider spreads
    
    # Data requirements
    MIN_BARS_REQUIRED = 150
    
    # Logging
    LOG_FILE = "mt5_signals_aggressive.csv"
    ENABLE_NEWS_FILTER = False  # Trade through news (RISKY!)
```

**Expected Behavior**: 8-12 signals per day, lower win rate but more activity

⚠️ **WARNING**: This configuration increases risk significantly. Only use if you have:
- 6+ months profitable trading experience
- Strong emotional control
- Sufficient capital to handle drawdowns

---

## 4. Scalper (High Frequency, NOT RECOMMENDED FOR BEGINNERS)

**Profile**: Very active trader, willing to take many small profits/losses

```python
class TradingConfig:
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_M1  # 1-minute chart
    
    # Indicator parameters (FAST)
    EMA_FAST = 8
    EMA_SLOW = 21
    RSI_PERIOD = 9
    ATR_PERIOD = 10
    VWAP_PERIOD = 50
    
    # Filter thresholds (MINIMAL FILTERING)
    RSI_LOWER = 45
    RSI_UPPER = 75
    MIN_ATR_MULTIPLIER = 0.00005
    
    # Risk management (TIGHT TARGETS)
    RISK_REWARD_RATIO = 1.2  # Quick 1.2:1 trades
    ATR_STOP_MULTIPLIER = 0.5  # Very tight stops
    
    # Session filters (OVERLAP ONLY - most liquid)
    LONDON_START = time(12, 0)
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(16, 0)
    
    # Signal management (RAPID FIRE)
    COOLDOWN_MINUTES = 5  # Signal every 5 minutes possible
    MAX_SPREAD_PIPS = 1.0  # Must be tight spread
    
    # Data requirements
    MIN_BARS_REQUIRED = 100
    
    # Logging
    LOG_FILE = "mt5_signals_scalping.csv"
    ENABLE_NEWS_FILTER = True  # Still avoid news
```

**Expected Behavior**: 20-30 signals per session, very active trading

⚠️ **WARNING**: Scalping requires:
- Advanced experience
- Excellent discipline
- Fast execution skills
- Understanding of transaction costs (spreads/commissions)
- Full-time focus during trading hours
- **NOT suitable for beginners**

---

## 5. Swing Trader (Higher Timeframe, Position Holding)

**Profile**: Patient trader, willing to hold positions hours/days, focuses on major trends

```python
class TradingConfig:
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_H1  # 1-hour chart
    
    # Indicator parameters (SLOWER)
    EMA_FAST = 50
    EMA_SLOW = 200
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 200
    
    # Filter thresholds (STRICT TREND)
    RSI_LOWER = 52
    RSI_UPPER = 68
    MIN_ATR_MULTIPLIER = 0.0002  # Higher timeframe needs more volatility
    
    # Risk management (WIDE TARGETS)
    RISK_REWARD_RATIO = 4.0  # Looking for big moves
    ATR_STOP_MULTIPLIER = 2.0  # Wide stops for larger swings
    
    # Session filters (ALL DAY - swing trading doesn't need tight session)
    LONDON_START = time(0, 0)
    LONDON_END = time(23, 59)
    NY_START = time(0, 0)
    NY_END = time(23, 59)
    
    # Signal management (PATIENT)
    COOLDOWN_MINUTES = 240  # One signal every 4 hours max
    MAX_SPREAD_PIPS = 3.0  # Less sensitive to spread on larger moves
    
    # Data requirements
    MIN_BARS_REQUIRED = 300
    
    # Logging
    LOG_FILE = "mt5_signals_swing.csv"
    ENABLE_NEWS_FILTER = True
```

**Expected Behavior**: 1-3 signals per week, larger position hold times

---

## 6. Multi-Pair Scanner (Advanced - Requires Code Modification)

**Profile**: Want to scan multiple pairs for best setup

**Note**: This requires modifying the main script to loop through symbols.

```python
class TradingConfig:
    # Market settings (will be overridden in loop)
    SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
    TIMEFRAME = mt5.TIMEFRAME_M5
    
    # Indicator parameters
    EMA_FAST = 20
    EMA_SLOW = 50
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 100
    
    # Filter thresholds (STRICT - only want BEST setups across all pairs)
    RSI_LOWER = 52
    RSI_UPPER = 68
    MIN_ATR_MULTIPLIER = 0.0001
    
    # Risk management
    RISK_REWARD_RATIO = 2.5
    ATR_STOP_MULTIPLIER = 1.0
    
    # Session filters
    LONDON_START = time(7, 0)
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(21, 0)
    
    # Signal management
    COOLDOWN_MINUTES = 30
    MAX_SPREAD_PIPS = 2.0
    
    # Data requirements
    MIN_BARS_REQUIRED = 200
    
    # Logging
    LOG_FILE = "mt5_signals_multi.csv"
    ENABLE_NEWS_FILTER = True
```

**Code modification needed**:
```python
# In main() function, replace single symbol with loop:
for symbol in config.SYMBOLS:
    config.SYMBOL = symbol
    # ... rest of signal generation logic
```

---

## How to Use These Configurations

1. **Choose a profile** that matches your experience level
2. **Open** `mt5_signal_generator.py`
3. **Find** the `TradingConfig` class (near the top)
4. **Replace** the entire class with your chosen configuration
5. **Save** the file
6. **Test on demo** for at least 1 week
7. **Review results** in CSV log
8. **Adjust** if needed

---

## Configuration Safety Guidelines

✅ **DO:**
- Start with conservative settings
- Test on demo first
- Make small adjustments
- Track results for at least 1 week before changing
- Document why you changed settings

❌ **DON'T:**
- Jump straight to aggressive settings
- Change multiple parameters at once (can't tell what helped/hurt)
- Modify filters after a losing trade (emotional reaction)
- Disable all safety features
- Trade live while "experimenting"

---

## Performance Metrics to Track

For any configuration, track these metrics:

1. **Signal Frequency**: How many signals per day?
2. **Win Rate**: What % of signals (if traded) would profit?
3. **Average R:R**: What's the actual risk:reward achieved?
4. **Best Session**: Which session produces best signals?
5. **Failed Conditions**: Which filters reject most signals?

**Example tracking:**
```
Week 1 (Conservative Config):
- Signals: 8 total (1.6 per day)
- Would-be wins: 6 (75% win rate)
- Avg R:R: 1:2.8 (better than 1:3 target)
- Best session: London/NY Overlap
- Most common rejection: RSI out of range

Conclusion: Config is working well, keep it.
```

---

## When to Modify Your Configuration

**Good reasons to adjust:**
- After 2+ weeks of tracking, clear pattern emerges
- Win rate consistently >70% → can loosen filters slightly
- Win rate consistently <40% → tighten filters
- Too few signals (<1 per day) → slightly loosen filters
- Too many signals (>10 per day) → tighten filters
- Specific session performs much better → adjust session times

**Bad reasons to adjust:**
- Had a losing trade today
- Want more "action"
- Someone else's settings look better
- Impatient for signals

---

## Advanced: Creating Your Own Configuration

If you want to create a custom configuration:

1. **Start with balanced default**
2. **Change ONE parameter at a time**
3. **Test for minimum 20 signals**
4. **Document the change and results**
5. **Keep or revert based on data**
6. **Repeat**

**Example iteration:**
```
Week 1: Default config → 45% win rate
Week 2: RSI_LOWER 50→55 → 55% win rate (improvement, keep)
Week 3: RSI_UPPER 70→65 → 62% win rate (improvement, keep)
Week 4: RISK_REWARD 2.0→2.5 → 58% win rate (slight drop, but acceptable)
Week 5: Final config locked in, 60% win rate stable
```

---

## Pair-Specific Adjustments

Different currency pairs have different characteristics:

**EURUSD (Default)**:
- Good: Most liquid, tight spreads, predictable
- Settings: Default configuration works well

**GBPUSD (Volatile)**:
- Good: Large moves, clear trends
- Adjust: Increase MIN_ATR_MULTIPLIER to 0.00015 (more volatile)
- Adjust: Increase ATR_STOP_MULTIPLIER to 1.5 (wider stops)

**USDJPY (Fast-moving)**:
- Good: Strong trends, fast moves
- Adjust: Faster EMAs (15/35)
- Adjust: Tighter risk:reward (1.5:1) due to quick moves

**AUDUSD (Commodity-linked)**:
- Good: Correlates with gold/commodities
- Adjust: Trade during Asian/London overlap
- Adjust: Watch commodity news closely

**XAUUSD (Gold - Very Volatile)**:
- Good: Big moves, trending
- Adjust: MIN_ATR_MULTIPLIER to 0.50 (much larger swings)
- Adjust: ATR_STOP_MULTIPLIER to 2.0 (need wide stops)
- Adjust: Risk:reward to 3.0+ (go for big moves)

**Always test pair-specific configs on demo first!**

---

*Remember: Configuration is personal. What works for one trader may not work for another. Trust the process, track results, adjust slowly.*
