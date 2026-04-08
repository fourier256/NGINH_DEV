import time
import requests
import pandas as pd
import zipfile
from pathlib import Path
from datetime import datetime, timedelta

# =========================
# 경로 설정
# =========================
BASE = Path(__file__).parent
CACHE = BASE / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()

# =========================
# 업비트 1분봉 수집
# =========================
def fetch_upbit(market, start, end):
    url = "https://api.upbit.com/v1/candles/minutes/1"
    dfs = []
    to = end

    while True:
        params = {
            "market": market,
            "count": 200,
            "to": to.strftime("%Y-%m-%dT%H:%M:%S")
        }
        res = SESSION.get(url, params=params)
        data = res.json()

        if not data:
            break

        df = pd.DataFrame(data)
        df['date_time_utc'] = pd.to_datetime(df['candle_date_time_utc'])
        dfs.append(df)

        oldest = df['date_time_utc'].min()
        if oldest <= start:
            break

        to = oldest - timedelta(minutes=1)
        time.sleep(0.11)  # rate limit 대응

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    df = df[(df['date_time_utc'] >= start) & (df['date_time_utc'] <= end)]
    return df.sort_values('date_time_utc')


# =========================
# 업비트 저장 (헤더 문제 해결 버전)
# =========================
def save_upbit_zip(df, market):
    if df.empty:
        return

    df = df[['date_time_utc', 'opening_price', 'high_price', 'low_price', 'trade_price',
             'candle_acc_trade_price', 'candle_acc_trade_volume']]

    df.columns = ['date_time_utc', 'open', 'high', 'low', 'close',
                  'acc_trade_price', 'acc_trade_volume']

    df['month'] = df['date_time_utc'].dt.strftime("%Y-%m")

    for m, g in df.groupby('month'):
        path = CACHE / f"{market}_candle-1m_{m}.zip"

        # 🔥 핵심: 기존 파일 삭제 → append 방지
        if path.exists():
            path.unlink()

        csv_name = f"{market}_{m}.csv"

        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                csv_name,
                g.drop(columns='month').to_csv(index=False, header=True)
            )


# =========================
# 바이낸스 1분봉 수집
# =========================
def fetch_binance(symbol, start, end):
    url = "https://api.binance.com/api/v3/klines"
    dfs = []

    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    while start_ms < end_ms:
        params = {
            "symbol": symbol,
            "interval": "1m",
            "startTime": start_ms,
            "limit": 1000
        }

        res = SESSION.get(url, params=params)
        data = res.json()

        if not data:
            break

        df = pd.DataFrame(data)
        dfs.append(df)

        start_ms = int(df.iloc[-1, 0]) + 1
        time.sleep(0.1)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


# =========================
# 바이낸스 저장 (헤더 문제 해결)
# =========================
def save_binance_zip(df):
    if df.empty:
        return

    df = df[[0,1,2,3,4,5,7]]
    df.columns = ['ts','open','high','low','close','volume','quote_volume']

    df['dt'] = pd.to_datetime(df['ts'], unit='ms')
    df['month'] = df['dt'].dt.strftime("%Y-%m")

    for m, g in df.groupby('month'):
        path = CACHE / f"BTCUSDT-1m-{m}.zip"

        # 🔥 기존 파일 삭제
        if path.exists():
            path.unlink()

        csv_name = f"BTCUSDT_{m}.csv"

        with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                csv_name,
                g.drop(columns='month').to_csv(index=False, header=True)
            )


# =========================
# 메인 실행
# =========================
def main():
    start = datetime(2025, 4, 1)
    end = datetime(2026, 3, 31, 23, 59)

    print("📥 Upbit KRW-USDT")
    u = fetch_upbit("KRW-USDT", start, end)
    save_upbit_zip(u, "KRW-USDT")

    print("📥 Upbit KRW-BTC")
    b = fetch_upbit("KRW-BTC", start, end)
    save_upbit_zip(b, "KRW-BTC")

    print("📥 Binance BTCUSDT")
    g = fetch_binance("BTCUSDT", start, end)
    save_binance_zip(g)

    print("✅ DONE")


if __name__ == "__main__":
    main()
