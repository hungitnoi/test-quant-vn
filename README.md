# QuantVN Entry Test - Alpha2004 Derivative Strategy

## 1. Strategy Overview
Chiến lược giao dịch phái sinh (VN30F1M) kết hợp tín hiệu Alpha dựa trên hành vi giá (Price Action) và khối lượng (Volume) đột biến, đi kèm với bộ lọc xu hướng (Trend Filter) và cơ chế quản lý rủi ro động (Dynamic Exit).

* **Alpha Signal:** Tính toán dựa trên tỷ lệ `(Close - Open) / (High - Low)` kết hợp với `Volume Ratio`.
* **Trend Filter:** Sử dụng Moving Average (MA100) để xác nhận xu hướng.
* **Risk Management:** Sử dụng Trailing Stop động dựa trên chỉ báo ATR (Average True Range) với hệ số 1.8 để siết chặt Maximum Drawdown.

## 2. Performance Metrics (Backtest Results)
* **Sharpe Ratio:** 2.377
* **Max Drawdown:** -12.58%
* **Win Rate:** 38.90%
* **Profit Factor:** 1.657

## 3. How to Run
```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Tạo file .env và thêm API Key
echo "QUANTVN_API_KEY=your_api_key_here" > .env

# Test API đã connect được chưa
python TEST_API.py

# Chạy chiến lược
python strategy.py
