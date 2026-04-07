#!/usr/bin/env python3
"""
KRW-USDT 1분봉 기술적 지표 + 그리드 기반 백테스트.

입력 CSV (헤더 필수):
- usdt_1m.csv: timestamp,open,high,low,close,volume
- btc_krw_1m.csv: timestamp,open,high,low,close,volume
- (옵션) btc_usdt_1m.csv: timestamp,open,high,low,close,volume

timestamp는 ISO8601(UTC 권장) 또는 epoch seconds.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import deque, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


MAKER_REBATE = 0.0001  # +0.01%


@dataclass
class Candle:
    ts: datetime
    o: float
    h: float
    l: float
    c: float
    v: float


class RollingWindow:
    def __init__(self, n: int):
        self.n = n
        self.q = deque()
        self.s = 0.0
        self.s2 = 0.0

    def push(self, x: float) -> None:
        self.q.append(x)
        self.s += x
        self.s2 += x * x
        if len(self.q) > self.n:
            y = self.q.popleft()
            self.s -= y
            self.s2 -= y * y

    def mean(self) -> float:
        if not self.q:
            return 0.0
        return self.s / len(self.q)

    def std(self) -> float:
        m = self.mean()
        v = self.s2 / max(1, len(self.q)) - m * m
        return math.sqrt(max(0.0, v))

    def full(self) -> bool:
        return len(self.q) >= self.n


def parse_ts(raw: str) -> datetime:
    raw = raw.strip()
    if raw.isdigit():
        return datetime.fromtimestamp(int(raw), tz=timezone.utc)
    raw = raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_csv(path: Path) -> Dict[datetime, Candle]:
    out: Dict[datetime, Candle] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ts = parse_ts(row["timestamp"])
            out[ts] = Candle(
                ts=ts,
                o=float(row["open"]),
                h=float(row["high"]),
                l=float(row["low"]),
                c=float(row["close"]),
                v=float(row["volume"]),
            )
    return out


def month_key(ts: datetime) -> str:
    return f"{ts.year:04d}-{ts.month:02d}"


def backtest(
    usdt: Dict[datetime, Candle],
    btc_krw: Dict[datetime, Candle],
    btc_usdt: Optional[Dict[datetime, Candle]],
    seed_krw: float,
) -> Tuple[List[Tuple[str, float]], Dict[str, float]]:
    common_ts = sorted(set(usdt.keys()) & set(btc_krw.keys()))
    if btc_usdt:
        common_ts = [t for t in common_ts if t in btc_usdt]

    if not common_ts:
        raise ValueError("세 데이터셋의 공통 timestamp가 없습니다.")

    close_win = RollingWindow(60)
    vol_win = RollingWindow(60)
    ret_spread_win = RollingWindow(180)
    atr_win = RollingWindow(14)

    prev_usdt_close = None
    prev_btc_close = None
    avg_gain = 0.0
    avg_loss = 0.0

    cash = seed_krw
    qty = 0.0
    avg_cost = 0.0
    layers = 0
    max_layers = 5
    base_order_krw = seed_krw * 0.08

    peak_eq = seed_krw
    max_dd = 0.0
    trades = 0

    month_equity_close: Dict[str, float] = {}

    for ts in common_ts:
        u = usdt[ts]
        b = btc_krw[ts]
        bu = btc_usdt[ts] if btc_usdt else None

        close_win.push(u.c)
        vol_win.push(u.v)

        usdt_ret = 0.0 if prev_usdt_close is None else (u.c / prev_usdt_close - 1.0)
        btc_ret = 0.0 if prev_btc_close is None else (b.c / prev_btc_close - 1.0)

        spread = usdt_ret - 0.55 * btc_ret
        ret_spread_win.push(spread)

        if prev_usdt_close is None:
            tr = u.h - u.l
        else:
            tr = max(u.h - u.l, abs(u.h - prev_usdt_close), abs(u.l - prev_usdt_close))
        atr_win.push(tr)

        # RSI(14) Wilder
        ch = 0.0 if prev_usdt_close is None else (u.c - prev_usdt_close)
        gain = max(0.0, ch)
        loss = max(0.0, -ch)
        if avg_gain == 0.0 and avg_loss == 0.0:
            avg_gain = gain
            avg_loss = loss
        else:
            avg_gain = (avg_gain * 13 + gain) / 14
            avg_loss = (avg_loss * 13 + loss) / 14
        rs = avg_gain / avg_loss if avg_loss > 1e-12 else 10.0
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # feature engineering
        boll_z = 0.0
        if close_win.full() and close_win.std() > 1e-12:
            boll_z = (u.c - close_win.mean()) / close_win.std()

        vol_ratio = u.v / max(1e-12, vol_win.mean()) if vol_win.full() else 1.0
        spread_z = 0.0
        if ret_spread_win.full() and ret_spread_win.std() > 1e-12:
            spread_z = (spread - ret_spread_win.mean()) / ret_spread_win.std()

        atr_n = atr_win.mean() / max(1e-12, u.c)

        kimchi = 0.0
        if bu is not None and bu.c > 0 and u.c > 0:
            implied_krw_btc = bu.c * u.c
            kimchi = b.c / implied_krw_btc - 1.0

        # composite signal (mean-reversion + liquidity + premium)
        score = 0.0
        score += -1.25 * boll_z
        score += -0.75 * spread_z
        score += 0.65 * ((50.0 - rsi) / 50.0)
        score += 0.2 * max(0.0, min(3.0, vol_ratio - 1.0))
        score += -1.1 * kimchi

        buy_threshold = 1.25
        sell_threshold = -0.55

        buy_price = u.o
        sell_price = u.o

        # dynamic grid spacing: 변동성 높을수록 간격 확대
        grid_gap = max(0.00035, min(0.0022, atr_n * 1.25))

        # buy rule
        can_add_grid = qty > 0 and layers < max_layers and u.o < avg_cost * (1.0 - grid_gap * layers)
        do_buy = (score > buy_threshold and layers < max_layers) or can_add_grid

        if do_buy and (u.l < buy_price):  # 엄격히 미만
            order_krw = base_order_krw * (1.0 + 0.35 * layers)
            order_krw = min(order_krw, cash)
            if order_krw > 1000:
                buy_qty = order_krw / buy_price
                new_notional = qty * avg_cost + buy_qty * buy_price
                qty += buy_qty
                avg_cost = new_notional / max(1e-12, qty)
                cash -= order_krw
                cash += order_krw * MAKER_REBATE
                layers += 1
                trades += 1

        # sell rule (signal or take-profit or risk-off)
        tp_hit = qty > 0 and u.o > avg_cost * (1.0 + grid_gap * 1.2)
        risk_off = qty > 0 and (score < sell_threshold or kimchi > 0.025)

        if qty > 0 and (tp_hit or risk_off) and (u.h > sell_price):  # 엄격히 초과
            sell_qty = qty * (0.35 if not (score < -1.2 or kimchi > 0.04) else 0.7)
            proceeds = sell_qty * sell_price
            qty -= sell_qty
            cash += proceeds
            cash += proceeds * MAKER_REBATE
            if qty < 1e-12:
                qty = 0.0
                avg_cost = 0.0
                layers = 0
            else:
                layers = max(1, layers - 1)
            trades += 1

        eq = cash + qty * u.c
        peak_eq = max(peak_eq, eq)
        dd = (peak_eq - eq) / peak_eq if peak_eq > 0 else 0.0
        max_dd = max(max_dd, dd)

        month_equity_close[month_key(ts)] = eq

        prev_usdt_close = u.c
        prev_btc_close = b.c

    months = sorted(month_equity_close.keys())
    monthly_returns: List[Tuple[str, float]] = []
    prev = seed_krw
    for m in months:
        cur = month_equity_close[m]
        r = (cur / prev - 1.0) * 100.0
        monthly_returns.append((m, r))
        prev = cur

    final_eq = prev
    summary = {
        "final_equity": final_eq,
        "total_return_pct": (final_eq / seed_krw - 1.0) * 100.0,
        "max_drawdown_pct": max_dd * 100.0,
        "trades": float(trades),
    }
    return monthly_returns, summary


def save_monthly(path: Path, monthly: List[Tuple[str, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["month", "return_pct"])
        for m, r in monthly:
            w.writerow([m, f"{r:.4f}"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--usdt", required=True, help="KRW-USDT 1m CSV")
    ap.add_argument("--btc-krw", required=True, help="KRW-BTC 1m CSV")
    ap.add_argument("--btc-usdt", default=None, help="BTC-USDT 1m CSV (optional, 김프 proxy)")
    ap.add_argument("--seed", type=float, default=1_000_000_000.0)
    ap.add_argument("--out", default="monthly_returns.csv")
    args = ap.parse_args()

    usdt = load_csv(Path(args.usdt))
    btc_krw = load_csv(Path(args.btc_krw))
    btc_usdt = load_csv(Path(args.btc_usdt)) if args.btc_usdt else None

    monthly, summary = backtest(usdt, btc_krw, btc_usdt, args.seed)
    save_monthly(Path(args.out), monthly)

    print("=== BACKTEST SUMMARY ===")
    print(f"months={len(monthly)}")
    for k, v in summary.items():
        if "pct" in k:
            print(f"{k}: {v:.4f}%")
        elif k == "trades":
            print(f"{k}: {int(v)}")
        else:
            print(f"{k}: {v:,.0f}")
    print(f"monthly csv saved to: {args.out}")


if __name__ == "__main__":
    main()
