"""
MT5 Manual Trading Signal Generator
====================================
A conservative, rule-based system for generating manual trading signals.
NO AUTOMATED TRADING - SIGNALS ONLY.

Author: Senior Quantitative Trader
License: For educational and personal use only
Disclaimer: Not financial advice. User assumes all trading risk.
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import csv
import os
import sys
from typing import Optional, Dict, Tuple


# ============================================================================
# USER CONFIGURATION SECTION - SAFE TO MODIFY
# ============================================================================

class TradingConfig:
    """
    Centralized configuration for all trading parameters.
    Modify these values to customize the signal generator behavior.
    """
    
    # Market settings
    SYMBOL = "EURUSD"
    TIMEFRAME = mt5.TIMEFRAME_M5  # M1, M5, M15, M30, H1, H4, D1
    
    # Indicator parameters
    EMA_FAST = 20
    EMA_SLOW = 50
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    VWAP_PERIOD = 100  # Lookback bars for VWAP calculation
    
    # Filter thresholds
    RSI_LOWER = 50  # Minimum RSI for long entries
    RSI_UPPER = 70  # Maximum RSI for long entries (avoid overbought)
    MIN_ATR_MULTIPLIER = 0.0001  # Minimum ATR to trade (avoid low volatility)
    
    # Risk management
    RISK_REWARD_RATIO = 2.0  # Take profit will be 2x stop loss distance
    ATR_STOP_MULTIPLIER = 1.0  # Stop loss = Entry - (ATR * multiplier)
    
    # Session filters (UTC times)
    LONDON_START = time(7, 0)
    LONDON_END = time(16, 0)
    NY_START = time(12, 0)
    NY_END = time(21, 0)
    
    # Signal management
    COOLDOWN_MINUTES = 30  # Minimum minutes between signals
    MAX_SPREAD_PIPS = 2.0  # Reject signals if spread exceeds this
    
    # Data requirements
    MIN_BARS_REQUIRED = 200  # Minimum historical bars needed
    
    # Logging
    LOG_FILE = "mt5_signals.csv"
    ENABLE_NEWS_FILTER = True  # Manual toggle - set False to override


# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

class Indicators:
    """
    Pure mathematical indicator calculations.
    All methods are static and deterministic.
    """
    
    @staticmethod
    def ema(data: np.ndarray, period: int) -> np.ndarray:
        """
        Exponential Moving Average.
        
        Args:
            data: Price array (typically close prices)
            period: EMA period
            
        Returns:
            EMA values as numpy array
        """
        ema = np.zeros_like(data)
        multiplier = 2.0 / (period + 1)
        
        # Initialize with SMA
        ema[period - 1] = np.mean(data[:period])
        
        # Calculate EMA
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
        
        return ema
    
    @staticmethod
    def rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Relative Strength Index.
        
        Args:
            data: Price array (typically close prices)
            period: RSI period
            
        Returns:
            RSI values (0-100) as numpy array
        """
        deltas = np.diff(data)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.zeros(len(data))
        avg_loss = np.zeros(len(data))
        
        # Initial averages
        avg_gain[period] = np.mean(gains[:period])
        avg_loss[period] = np.mean(losses[:period])
        
        # Smooth averages
        for i in range(period + 1, len(data)):
            avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gains[i - 1]) / period
            avg_loss[i] = (avg_loss[i - 1] * (period - 1) + losses[i - 1]) / period
        
        rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Average True Range.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
            
        Returns:
            ATR values as numpy array
        """
        tr = np.zeros(len(close))
        
        for i in range(1, len(close)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )
        
        atr = np.zeros_like(tr)
        atr[period] = np.mean(tr[1:period + 1])
        
        for i in range(period + 1, len(tr)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
        
        return atr
    
    @staticmethod
    def vwap(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
             volume: np.ndarray, period: int) -> np.ndarray:
        """
        Volume Weighted Average Price (rolling).
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data
            period: Lookback period
            
        Returns:
            VWAP values as numpy array
        """
        typical_price = (high + low + close) / 3
        vwap = np.zeros(len(close))
        
        for i in range(period - 1, len(close)):
            start_idx = max(0, i - period + 1)
            tp_slice = typical_price[start_idx:i + 1]
            vol_slice = volume[start_idx:i + 1]
            
            vwap[i] = np.sum(tp_slice * vol_slice) / np.sum(vol_slice) if np.sum(vol_slice) > 0 else close[i]
        
        return vwap


# ============================================================================
# MARKET STRUCTURE ANALYSIS
# ============================================================================

class MarketStructure:
    """
    Price action and swing analysis for higher-quality entries.
    """
    
    @staticmethod
    def find_swing_low(high: np.ndarray, low: np.ndarray, lookback: int = 20) -> Optional[float]:
        """
        Find the most recent higher low for stop loss placement.
        
        Args:
            high: High prices
            low: Low prices
            lookback: Number of bars to analyze
            
        Returns:
            Price of most recent swing low, or None if not found
        """
        if len(low) < lookback + 5:
            return None
        
        recent_lows = low[-lookback:]
        
        # Find local minima (swing lows)
        swings = []
        for i in range(2, len(recent_lows) - 2):
            if (recent_lows[i] < recent_lows[i - 1] and 
                recent_lows[i] < recent_lows[i - 2] and
                recent_lows[i] < recent_lows[i + 1] and
                recent_lows[i] < recent_lows[i + 2]):
                swings.append(recent_lows[i])
        
        if len(swings) >= 2:
            # Check if we have a higher low pattern
            if swings[-1] > swings[-2]:
                return swings[-1]
        
        return None
    
    @staticmethod
    def is_uptrend(ema_fast: float, ema_slow: float, price: float) -> bool:
        """
        Verify uptrend conditions.
        
        Args:
            ema_fast: Fast EMA value
            ema_slow: Slow EMA value
            price: Current price
            
        Returns:
            True if in uptrend
        """
        return ema_fast > ema_slow and price > ema_fast and price > ema_slow


# ============================================================================
# SESSION AND TIME FILTERS
# ============================================================================

class SessionFilter:
    """
    Trading session validation to trade only during high-liquidity periods.
    """
    
    @staticmethod
    def is_trading_session(dt: datetime, config: TradingConfig) -> Tuple[bool, str]:
        """
        Check if current time is within allowed trading sessions.
        
        Args:
            dt: Current datetime (UTC)
            config: Trading configuration
            
        Returns:
            (is_valid, session_name) tuple
        """
        current_time = dt.time()
        
        # London session
        if config.LONDON_START <= current_time <= config.LONDON_END:
            return True, "LONDON"
        
        # New York session
        if config.NY_START <= current_time <= config.NY_END:
            return True, "NEW_YORK"
        
        # Overlap (most liquid)
        if (config.LONDON_START <= current_time <= config.LONDON_END and
            config.NY_START <= current_time <= config.NY_END):
            return True, "LONDON_NY_OVERLAP"
        
        return False, "CLOSED"


# ============================================================================
# SIGNAL GENERATION ENGINE
# ============================================================================

class SignalGenerator:
    """
    Core signal generation logic with comprehensive validation.
    """
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.last_signal_time = None
        self.last_signal_bar = None
        
    def get_market_data(self) -> Optional[pd.DataFrame]:
        """
        Fetch market data from MT5 with validation.
        
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            rates = mt5.copy_rates_from_pos(
                self.config.SYMBOL,
                self.config.TIMEFRAME,
                0,
                self.config.MIN_BARS_REQUIRED
            )
            
            if rates is None or len(rates) < self.config.MIN_BARS_REQUIRED:
                print(f"❌ ERROR: Insufficient data. Got {len(rates) if rates is not None else 0} bars, need {self.config.MIN_BARS_REQUIRED}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            return df
            
        except Exception as e:
            print(f"❌ ERROR fetching market data: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate all required technical indicators.
        
        Args:
            df: Market data DataFrame
            
        Returns:
            Dictionary of indicator values
        """
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['tick_volume'].values
        
        ema_fast = Indicators.ema(close, self.config.EMA_FAST)
        ema_slow = Indicators.ema(close, self.config.EMA_SLOW)
        rsi = Indicators.rsi(close, self.config.RSI_PERIOD)
        atr = Indicators.atr(high, low, close, self.config.ATR_PERIOD)
        vwap = Indicators.vwap(high, low, close, volume, self.config.VWAP_PERIOD)
        
        return {
            'ema_fast': ema_fast[-1],
            'ema_slow': ema_slow[-1],
            'rsi': rsi[-1],
            'atr': atr[-1],
            'vwap': vwap[-1],
            'price': close[-1],
            'high': high,
            'low': low,
            'time': df['time'].iloc[-1]
        }
    
    def check_cooldown(self, current_time: datetime) -> bool:
        """
        Prevent signal spam by enforcing cooldown period.
        
        Args:
            current_time: Current bar timestamp
            
        Returns:
            True if cooldown satisfied
        """
        if self.last_signal_time is None:
            return True
        
        time_diff = (current_time - self.last_signal_time).total_seconds() / 60
        return time_diff >= self.config.COOLDOWN_MINUTES
    
    def check_spread(self) -> Tuple[bool, float]:
        """
        Validate current spread is acceptable.
        
        Returns:
            (is_valid, spread_pips) tuple
        """
        tick = mt5.symbol_info_tick(self.config.SYMBOL)
        if tick is None:
            return False, 999.0
        
        point = mt5.symbol_info(self.config.SYMBOL).point
        spread_pips = (tick.ask - tick.bid) / point / 10
        
        return spread_pips <= self.config.MAX_SPREAD_PIPS, spread_pips
    
    def evaluate_signal(self, indicators: Dict) -> Dict:
        """
        Main signal evaluation logic - ALL CONDITIONS MUST PASS.
        
        Args:
            indicators: Dictionary of indicator values
            
        Returns:
            Signal dictionary with all details
        """
        signal = {
            'symbol': self.config.SYMBOL,
            'timestamp': indicators['time'],
            'signal': 'NO TRADE',
            'entry': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'risk_pips': 0.0,
            'reasoning': [],
            'failed_conditions': []
        }
        
        # CONDITION 1: Cooldown
        if not self.check_cooldown(indicators['time']):
            signal['failed_conditions'].append(f"Cooldown active ({self.config.COOLDOWN_MINUTES}m)")
            return signal
        
        # CONDITION 2: Spread check
        spread_ok, spread_pips = self.check_spread()
        if not spread_ok:
            signal['failed_conditions'].append(f"Spread too wide ({spread_pips:.1f} pips > {self.config.MAX_SPREAD_PIPS})")
            return signal
        
        # CONDITION 3: Session filter
        in_session, session_name = SessionFilter.is_trading_session(
            indicators['time'].to_pydatetime(),
            self.config
        )
        if not in_session:
            signal['failed_conditions'].append(f"Outside trading hours (current: {session_name})")
            return signal
        
        signal['session'] = session_name
        
        # CONDITION 4: News filter (manual override available)
        if self.config.ENABLE_NEWS_FILTER:
            # User must manually disable if trading during news
            signal['reasoning'].append("News filter: ENABLED (manual override required for news trading)")
        
        # CONDITION 5: Trend filter
        trend_valid = MarketStructure.is_uptrend(
            indicators['ema_fast'],
            indicators['ema_slow'],
            indicators['price']
        )
        if not trend_valid:
            signal['failed_conditions'].append(
                f"No uptrend (EMA{self.config.EMA_FAST}={indicators['ema_fast']:.5f}, "
                f"EMA{self.config.EMA_SLOW}={indicators['ema_slow']:.5f}, Price={indicators['price']:.5f})"
            )
            return signal
        
        # CONDITION 6: RSI filter
        rsi_valid = self.config.RSI_LOWER < indicators['rsi'] < self.config.RSI_UPPER
        if not rsi_valid:
            signal['failed_conditions'].append(
                f"RSI out of range ({indicators['rsi']:.1f} not in {self.config.RSI_LOWER}-{self.config.RSI_UPPER})"
            )
            return signal
        
        # CONDITION 7: VWAP filter
        vwap_valid = indicators['price'] > indicators['vwap']
        if not vwap_valid:
            signal['failed_conditions'].append(
                f"Price below VWAP (Price={indicators['price']:.5f}, VWAP={indicators['vwap']:.5f})"
            )
            return signal
        
        # CONDITION 8: Volatility filter
        atr_valid = indicators['atr'] > self.config.MIN_ATR_MULTIPLIER
        if not atr_valid:
            signal['failed_conditions'].append(
                f"ATR too low ({indicators['atr']:.5f} < {self.config.MIN_ATR_MULTIPLIER})"
            )
            return signal
        
        # CONDITION 9: Market structure (higher low)
        swing_low = MarketStructure.find_swing_low(indicators['high'], indicators['low'])
        if swing_low is None:
            signal['failed_conditions'].append("No valid higher low pattern detected")
            return signal
        
        # ALL CONDITIONS PASSED - GENERATE SIGNAL
        entry_price = indicators['price']
        
        # Calculate stop loss (most conservative of swing low or ATR)
        atr_stop = entry_price - (indicators['atr'] * self.config.ATR_STOP_MULTIPLIER)
        stop_loss = max(swing_low, atr_stop)  # Use safer (higher) stop
        
        # Calculate take profit based on risk:reward
        risk_distance = entry_price - stop_loss
        take_profit = entry_price + (risk_distance * self.config.RISK_REWARD_RATIO)
        
        # Convert to pips
        point = mt5.symbol_info(self.config.SYMBOL).point
        risk_pips = risk_distance / point / 10
        
        # Update signal
        signal['signal'] = 'BUY'
        signal['entry'] = entry_price
        signal['stop_loss'] = stop_loss
        signal['take_profit'] = take_profit
        signal['risk_pips'] = risk_pips
        signal['reasoning'] = [
            f"Uptrend confirmed (EMA{self.config.EMA_FAST} > EMA{self.config.EMA_SLOW}, price above both)",
            f"RSI healthy at {indicators['rsi']:.1f} (momentum without overbought)",
            f"Price above VWAP (institutional support)",
            f"ATR shows sufficient volatility ({indicators['atr']:.5f})",
            f"Higher low pattern confirmed at {swing_low:.5f}",
            f"Trading during {session_name} session (high liquidity)",
            f"Spread acceptable at {spread_pips:.1f} pips",
            f"Risk:Reward = 1:{self.config.RISK_REWARD_RATIO}"
        ]
        
        # Update tracking
        self.last_signal_time = indicators['time'].to_pydatetime()
        
        return signal


# ============================================================================
# SIGNAL OUTPUT AND LOGGING
# ============================================================================

class SignalLogger:
    """
    Professional signal output formatting and CSV logging.
    """
    
    @staticmethod
    def print_signal(signal: Dict, indicators: Dict):
        """
        Print formatted signal to console.
        
        Args:
            signal: Signal dictionary
            indicators: Indicator values
        """
        print("\n" + "=" * 80)
        print("MT5 MANUAL TRADING SIGNAL")
        print("=" * 80)
        print(f"SYMBOL:          {signal['symbol']}")
        print(f"TIMEFRAME:       M5")
        print(f"TIMESTAMP:       {signal['timestamp']}")
        print(f"SESSION:         {signal.get('session', 'N/A')}")
        print("-" * 80)
        print(f"SIGNAL:          {signal['signal']}")
        print(f"ENTRY:           {signal['entry']:.5f}")
        print(f"STOP LOSS:       {signal['stop_loss']:.5f}")
        print(f"TAKE PROFIT:     {signal['take_profit']:.5f}")
        print(f"RISK (pips):     {signal['risk_pips']:.1f}")
        print("-" * 80)
        print("TREND STATUS:    ", end="")
        if signal['signal'] == 'BUY':
            print("UPTREND CONFIRMED")
        else:
            print("NO VALID TREND")
        print("-" * 80)
        print("INDICATOR VALUES:")
        print(f"  EMA 20:        {indicators.get('ema_fast', 0):.5f}")
        print(f"  EMA 50:        {indicators.get('ema_slow', 0):.5f}")
        print(f"  RSI:           {indicators.get('rsi', 0):.1f}")
        print(f"  ATR:           {indicators.get('atr', 0):.5f}")
        print(f"  VWAP:          {indicators.get('vwap', 0):.5f}")
        print(f"  Current Price: {indicators.get('price', 0):.5f}")
        print("-" * 80)
        
        if signal['signal'] == 'NO TRADE':
            print("FAILED CONDITIONS:")
            for condition in signal['failed_conditions']:
                print(f"  ✗ {condition}")
        else:
            print("REASONING:")
            for reason in signal['reasoning']:
                print(f"  ✓ {reason}")
        
        print("=" * 80)
        print("\n⚠️  DISCLAIMER: This is NOT a buy/sell recommendation.")
        print("    Execute trades at your own discretion and risk.")
        print("=" * 80 + "\n")
    
    @staticmethod
    def log_to_csv(signal: Dict, config: TradingConfig):
        """
        Append signal to CSV log file for journaling.
        
        Args:
            signal: Signal dictionary
            config: Trading configuration
        """
        file_exists = os.path.isfile(config.LOG_FILE)
        
        try:
            with open(config.LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                
                if not file_exists:
                    # Write header
                    writer.writerow([
                        'Timestamp', 'Symbol', 'Signal', 'Entry', 'StopLoss',
                        'TakeProfit', 'RiskPips', 'Session', 'Reasoning'
                    ])
                
                # Write signal
                reasoning = '; '.join(signal['reasoning']) if signal['reasoning'] else 'N/A'
                writer.writerow([
                    signal['timestamp'],
                    signal['symbol'],
                    signal['signal'],
                    signal['entry'],
                    signal['stop_loss'],
                    signal['take_profit'],
                    signal['risk_pips'],
                    signal.get('session', 'N/A'),
                    reasoning
                ])
                
            print(f"✓ Signal logged to {config.LOG_FILE}")
            
        except Exception as e:
            print(f"❌ ERROR logging to CSV: {e}")


# ============================================================================
# MT5 CONNECTION MANAGER
# ============================================================================

class MT5Connection:
    """
    Robust MT5 connection handling with graceful error recovery.
    """
    
    @staticmethod
    def initialize() -> bool:
        """
        Initialize MT5 connection with validation.
        
        Returns:
            True if successful
        """
        if not mt5.initialize():
            print("❌ ERROR: MT5 initialization failed")
            print(f"   Error code: {mt5.last_error()}")
            return False
        
        print("✓ MT5 initialized successfully")
        
        # Verify connection
        account_info = mt5.account_info()
        if account_info is None:
            print("❌ ERROR: Not connected to trading account")
            return False
        
        print(f"✓ Connected to account: {account_info.login}")
        print(f"  Server: {account_info.server}")
        print(f"  Balance: {account_info.balance} {account_info.currency}")
        
        return True
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Validate symbol exists and is tradable.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if valid
        """
        symbol_info = mt5.symbol_info(symbol)
        
        if symbol_info is None:
            print(f"❌ ERROR: Symbol {symbol} not found")
            return False
        
        if not symbol_info.visible:
            print(f"⚠️  WARNING: {symbol} not visible, attempting to enable...")
            if not mt5.symbol_select(symbol, True):
                print(f"❌ ERROR: Could not enable {symbol}")
                return False
        
        print(f"✓ Symbol {symbol} validated")
        print(f"  Spread: {symbol_info.spread} points")
        print(f"  Digits: {symbol_info.digits}")
        
        return True
    
    @staticmethod
    def shutdown():
        """Gracefully shutdown MT5 connection."""
        mt5.shutdown()
        print("✓ MT5 connection closed")


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main application entry point.
    """
    print("\n" + "=" * 80)
    print("MT5 MANUAL TRADING SIGNAL GENERATOR")
    print("=" * 80)
    print("⚠️  SAFETY NOTICE:")
    print("   - This program generates SIGNALS ONLY")
    print("   - NO automated trading will occur")
    print("   - User must execute trades manually")
    print("   - Not financial advice - for educational use only")
    print("=" * 80 + "\n")
    
    # Initialize configuration
    config = TradingConfig()
    
    # Initialize MT5
    if not MT5Connection.initialize():
        sys.exit(1)
    
    # Validate symbol
    if not MT5Connection.validate_symbol(config.SYMBOL):
        MT5Connection.shutdown()
        sys.exit(1)
    
    print(f"\n✓ Configuration loaded")
    print(f"  Symbol: {config.SYMBOL}")
    print(f"  Timeframe: M5")
    print(f"  EMA: {config.EMA_FAST}/{config.EMA_SLOW}")
    print(f"  RSI: {config.RSI_PERIOD}")
    print(f"  Risk:Reward: 1:{config.RISK_REWARD_RATIO}")
    print(f"  News Filter: {'ENABLED' if config.ENABLE_NEWS_FILTER else 'DISABLED'}")
    
    # Initialize signal generator
    generator = SignalGenerator(config)
    
    try:
        print("\n" + "=" * 80)
        print("GENERATING SIGNAL...")
        print("=" * 80 + "\n")
        
        # Fetch market data
        df = generator.get_market_data()
        if df is None:
            raise Exception("Failed to retrieve market data")
        
        print(f"✓ Retrieved {len(df)} bars of data")
        
        # Calculate indicators
        indicators = generator.calculate_indicators(df)
        print("✓ Indicators calculated")
        
        # Evaluate signal
        signal = generator.evaluate_signal(indicators)
        
        # Output signal
        SignalLogger.print_signal(signal, indicators)
        
        # Log to CSV (only if valid signal or for record keeping)
        if signal['signal'] == 'BUY':
            SignalLogger.log_to_csv(signal, config)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Signal generation interrupted by user")
    
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always cleanup
        MT5Connection.shutdown()
        print("\n✓ Program terminated safely\n")


if __name__ == "__main__":
    main()
