import os
import numpy as np
import pandas as pd

from dotenv import load_dotenv

from quantvn.vn.data.utils import client
from quantvn.vn.data import get_derivatives_hist
from quantvn.vn.metrics import (
    Backtest_Derivates,
    Metrics
)

def gen_position(df: pd.DataFrame) -> pd.DataFrame:


    # =========================
    # PARAMS (Alpha2004 & Strategy)
    # =========================
    decay_window = 8
    norm_window = 50
    vol_ma_window = 36
    
    buy_threshold = 0.75
    sell_threshold = -0.75
    trend_window = 100
    
    # =========================
    # PARAMS (Dynamic Exit - Tối ưu)
    # =========================
    atr_period = 14
    atr_multiplier = 1.8   # SIẾT CHẶT: Giảm từ 2.5 xuống 1.8 để giảm Drawdown
    cooldown_period = 5    # Nghỉ 5 nến sau khi đóng lệnh
    
    eps = 1e-5

    # =========================
    # PREPARE DATA SERIES
    # =========================
    close = df["Close"].astype(float)
    open_price = df["Open"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)

    if "Volume" in df.columns:
        volume = df["Volume"].astype(float)
    elif "volume" in df.columns:
        volume = df["volume"].astype(float)
    else:
        df["signal"] = 0
        df["position"] = 0
        return df

    # TÍNH TOÁN ATR (Cho Dynamic Exit)
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    
    atr = tr.rolling(window=atr_period, min_periods=1).mean()

    # =========================
    # ALPHA 2004 LOGIC
    # =========================
    body = close - open_price
    hl_range = high - low + eps
    alpha_raw = body / hl_range

    vol_ma = volume.rolling(window=vol_ma_window, min_periods=1).mean() + eps
    vol_ratio = volume / vol_ma
    vol_ratio_capped = vol_ratio.clip(upper=2.5)
    momentum_scaled = alpha_raw * vol_ratio_capped

    weights = np.arange(1, decay_window + 1)
    wma_func = lambda x: np.dot(x, weights) / weights.sum()
    
    alpha_decay = momentum_scaled.rolling(window=decay_window, min_periods=decay_window).apply(wma_func, raw=True)

    sma_decay = alpha_decay.rolling(window=norm_window, min_periods=1).mean()
    std_decay = alpha_decay.rolling(window=norm_window, min_periods=1).std(ddof=0) + eps

    raw_z_score = (alpha_decay - sma_decay) / std_decay
    score_series = np.tanh(raw_z_score)

    # =========================
    # STRATEGY TREND FILTER
    # =========================
    trend_ma_series = close.rolling(window=trend_window, min_periods=1).mean()

    # =========================
    # STATE MACHINE (EXECUTION)
    # =========================
    signal = 0
    signals = []
    positions = []
    
    # Biến quản lý trạng thái Dynamic Exit
    trail_stop = np.nan
    cooldown_counter = 0

    for i in range(len(df)):
        score = score_series.iat[i]
        trend_ma = trend_ma_series.iat[i]
        current_close = close.iat[i]
        current_atr = atr.iat[i]

        new_signal = signal

        if pd.isna(score) or pd.isna(trend_ma) or pd.isna(current_atr):
            signals.append(0)
            positions.append(0)
            continue

        if cooldown_counter > 0:
            cooldown_counter -= 1

        is_uptrend = current_close > trend_ma
        is_downtrend = current_close < trend_ma

        # LOGIC VÀO LỆNH
        if signal == 0:
            if cooldown_counter == 0:
                if score > buy_threshold and is_uptrend:
                    new_signal = 1
                    # Đặt mức Stop Loss ban đầu khi vừa vào lệnh
                    trail_stop = current_close - (atr_multiplier * current_atr)
                elif score < sell_threshold and is_downtrend:
                    new_signal = -1
                    trail_stop = current_close + (atr_multiplier * current_atr)
        
        # LOGIC RA LỆNH ĐỘNG (TRAILING STOP)
        else:
            exit_triggered = False
            
            if signal == 1: # Đang Long
                # Kéo Trailing Stop LÊN nếu giá tăng (không bao giờ kéo xuống)
                trail_stop = max(trail_stop, current_close - (atr_multiplier * current_atr))
                
                # Thoát nếu giá đâm xuyên xuống dưới Trailing Stop
                if current_close < trail_stop:
                    exit_triggered = True
                    
            elif signal == -1: # Đang Short 
                # Kéo Trailing Stop XUỐNG nếu giá giảm
                trail_stop = min(trail_stop, current_close + (atr_multiplier * current_atr))
                
                # Thoát nếu giá đâm ngược lên trên Trailing Stop
                if current_close > trail_stop:
                    exit_triggered = True

            # Xử lý đóng lệnh
            if exit_triggered:
                new_signal = 0
                trail_stop = np.nan
                cooldown_counter = cooldown_period

        signal = new_signal
        signals.append(signal)
        positions.append(signal)

    df["signal"] = signals
    df["position"] = positions
    
    # Debug
    df["alpha_score"] = score_series
    df["trend_ma"] = trend_ma_series

    return df
if __name__ == "__main__":
    # Đọc API key từ .env
    # .env:
    # QUANTVN_API_KEY=your_key_here
    from dotenv import load_dotenv

    load_dotenv()
    # ==========================================================
    # CONNECT API
    # ==========================================================
    load_dotenv()

    client(
        apikey=os.getenv("QUANTVN_API_KEY")
    )

    # ==========================================================
    # LOAD DATA
    # ==========================================================
    df = get_derivatives_hist(
        "VN30F1M",
        "15m"
    )

    # ==========================================================
    # GENERATE SIGNAL
    # ==========================================================
    df = gen_position(df)

    print("\n========== LAST POSITIONS ==========")
    print(df[["Close", "position"]].tail())

    # ==========================================================
    # BACKTEST
    # ==========================================================
    backtest = Backtest_Derivates(
        df,
        pnl_type="after_fees"
    )

    metrics = Metrics(backtest)

    # ==========================================================
    # PNL
    # ==========================================================
    pnl = backtest.PNL()

    print("\n========== PNL SUMMARY ==========")
    print(f"Final PnL            : {pnl.iloc[-1]:,.2f} VND")

    daily_pnl = backtest.daily_PNL()

    print(f"Minimum Capital      : {backtest.estimate_minimum_capital():,.0f} VND")

    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================
    print("\n========== PERFORMANCE REPORT ==========")

    print(f"Sharpe Ratio         : {metrics.sharpe():.3f}")
    print(f"Sortino Ratio        : {metrics.sortino():.3f}")
    print(f"Calmar Ratio         : {metrics.calmar():.3f}")

    print(f"Max Drawdown         : {metrics.max_drawdown()*100:.2f}%")

    print(f"Win Rate             : {metrics.win_rate()*100:.2f}%")

    print(f"Profit Factor        : {metrics.profit_factor():.3f}")

    print(f"Average Return       : {metrics.avg_return()*100:.4f}%")

    print(f"Volatility           : {metrics.volatility()*100:.4f}%")

    print(f"Average Win          : {metrics.avg_win():,.0f} VND")

    print(f"Average Loss         : {metrics.avg_loss():,.0f} VND")

    print(f"Risk of Ruin         : {metrics.risk_of_ruin():.4f}")

    # ==========================================================
    # VALUE AT RISK
    # ==========================================================
    var95 = metrics.value_at_risk(
        confidence_level=0.95
    )

    print(f"VaR (95%)            : {var95:,.0f} VND")

    # ==========================================================
    # DAILY PNL
    # ==========================================================
    print("\n========== LAST DAILY PNL ==========")
    print(daily_pnl.tail())

    # ==========================================================
    # EQUITY CURVE
    # ==========================================================
    backtest.plot_PNL(
        "VN30F1M - Donchian VWAP Strategy"
    )


