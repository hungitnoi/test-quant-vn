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

### Bước 1: Clone dự án về máy
```bash
git clone https://github.com/hungitnoi/test-quant-vn.git
cd test-quant-vn

```

### Bước 2: Khởi tạo và kích hoạt môi trường ảo (Virtual Environment)

Việc sử dụng môi trường ảo giúp tránh xung đột thư viện với hệ thống gốc.

**Đối với Windows:**

```bash
python -m venv .venv
.\.venv\Scripts\activate

```

*(Nếu PowerShell báo lỗi execution policy, hãy mở Command Prompt (cmd) để chạy, hoặc dùng lệnh: `Set-ExecutionPolicy Unrestricted -Scope Process`)*

**Đối với macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate

```

### Bước 3: Cài đặt thư viện phụ thuộc

Đảm bảo bạn đang ở trong môi trường ảo, sau đó chạy:

```bash
pip install -r requirements.txt

```

### Bước 4: Thiết lập biến môi trường (API Key)

Dự án yêu cầu API Key của QuantVN để lấy dữ liệu.

1. Tạo một file mới có tên chính xác là `.env` tại thư mục gốc của dự án.
2. Mở file bằng Text Editor (VS Code, Notepad, v.v.) và nhập vào nội dung sau:

```env
QUANTVN_API_KEY=your_actual_api_key_here

```

> **⚠️ Lưu ý quan trọng cho người dùng Windows:** Vui lòng tạo file thủ công. **KHÔNG** sử dụng lệnh `echo ... > .env` trong PowerShell vì PowerShell mặc định lưu file dưới chuẩn UTF-16, sẽ gây lỗi `UnicodeDecodeError` khi Python (yêu cầu UTF-8) đọc file.

### Bước 5: Chạy chiến lược và xem kết quả Backtest

```bash
python strategy.py

```

