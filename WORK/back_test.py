import json, zipfile, gc
from pathlib import Path

import numpy as np
import math
import pandas as pd
import requests
from sklearn.linear_model import Ridge
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

START = pd.Timestamp('2025-04-01 00:00:00', tz='UTC')
END = pd.Timestamp('2026-03-31 23:59:00', tz='UTC')
INITIAL_CAPITAL = 1_000_000_000.0
MAKER_REBATE = 0.0001
#CACHE = Path('/home/user/usdt_hft_cache')
#OUTDIR = Path('/mnt/user-data/outputs/usdt_hft_backtest')

CACHE = Path.home() / "usdt_hft_cache"
#CACHE = Path('./usdt_hft_cache')
OUTDIR = Path('./usdt_hft_backtest')

OUTDIR.mkdir(parents=True, exist_ok=True)
IDX = pd.date_range(START, END, freq='min', tz='UTC')
SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})


def load_upbit(market: str, prefix: str) -> pd.DataFrame:
    dfs = []
    for fp in sorted(CACHE.glob(f'{market}_candle-1m_*.zip')):
        with zipfile.ZipFile(fp) as zf:
            df = pd.read_csv(
                zf.open(zf.namelist()[0]),
                dtype={
                    'open': 'float32', 'high': 'float32', 'low': 'float32', 'close': 'float32',
                    'acc_trade_price': 'float32', 'acc_trade_volume': 'float32'
                }
            )
        df['ts'] = pd.to_datetime(df['date_time_utc'], utc=True)
        df = df[['ts', 'open', 'high', 'low', 'close', 'acc_trade_price', 'acc_trade_volume']]
        df.columns = ['ts', f'{prefix}_open', f'{prefix}_high', f'{prefix}_low', f'{prefix}_close', f'{prefix}_tp', f'{prefix}_tv']
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True).drop_duplicates('ts').set_index('ts').sort_index().reindex(IDX)
    oc, oo, oh, ol, otp, otv = [f'{prefix}_{x}' for x in ['close', 'open', 'high', 'low', 'tp', 'tv']]
    df[oc] = df[oc].ffill().astype('float32')
    df[oo] = df[oo].fillna(df[oc]).astype('float32')
    df[oh] = df[oh].fillna(df[[oo, oc]].max(axis=1)).astype('float32')
    df[ol] = df[ol].fillna(df[[oo, oc]].min(axis=1)).astype('float32')
    df[otp] = df[otp].fillna(0).astype('float32')
    df[otv] = df[otv].fillna(0).astype('float32')
    return df

def load_binance() -> pd.DataFrame:
    frames = []

    for fp in sorted(CACHE.glob('BTCUSDT-1m-*.zip')):
        with zipfile.ZipFile(fp) as zf:
            df = pd.read_csv(
                zf.open(zf.namelist()[0])  # ✅ header 있음
            )

        # 🔥 혹시 모를 중복 헤더 제거
        df = df[df['open'] != 'open']

        # 타입 변환
        for c in ['open','high','low','close','volume','quote_volume']:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        df['ts'] = pd.to_datetime(df['ts'], unit='ms', utc=True)

        df = df[['ts','open','high','low','close','volume','quote_volume']]
        df.columns = ['ts','g_open','g_high','g_low','g_close','g_tv','g_tp']

        frames.append(df)

    df = pd.concat(frames, ignore_index=True)\
           .drop_duplicates('ts')\
           .set_index('ts')\
           .sort_index()\
           .reindex(IDX)

    # 기존 후처리 그대로
    df['g_close'] = df['g_close'].ffill().astype('float32')
    df['g_open'] = df['g_open'].fillna(df['g_close']).astype('float32')
    df['g_high'] = df['g_high'].fillna(df[['g_open','g_close']].max(axis=1)).astype('float32')
    df['g_low'] = df['g_low'].fillna(df[['g_open','g_close']].min(axis=1)).astype('float32')
    df['g_tp'] = df['g_tp'].fillna(0).astype('float32')
    df['g_tv'] = df['g_tv'].fillna(0).astype('float32')

    return df

def load_binance_old() -> pd.DataFrame:
    frames = []
    for fp in sorted(CACHE.glob('BTCUSDT-1m-*.zip')):
        with zipfile.ZipFile(fp) as zf:
            df = pd.read_csv(
                zf.open(zf.namelist()[0]), header=None, usecols=[0,1,2,3,4,5,7],
                dtype={1:'float32',2:'float32',3:'float32',4:'float32',5:'float32',7:'float32'}
            )
        df.columns = ['ts', 'g_open', 'g_high', 'g_low', 'g_close', 'g_tv', 'g_tp']
        df['ts'] = pd.to_datetime(df['ts'], utc=True, unit='us')
        frames.append(df)
    df = pd.concat(frames, ignore_index=True).drop_duplicates('ts').set_index('ts').sort_index().reindex(IDX)
    df['g_close'] = df['g_close'].ffill().astype('float32')
    df['g_open'] = df['g_open'].fillna(df['g_close']).astype('float32')
    df['g_high'] = df['g_high'].fillna(df[['g_open','g_close']].max(axis=1)).astype('float32')
    df['g_low'] = df['g_low'].fillna(df[['g_open','g_close']].min(axis=1)).astype('float32')
    df['g_tp'] = df['g_tp'].fillna(0).astype('float32')
    df['g_tv'] = df['g_tv'].fillna(0).astype('float32')
    return df


def load_usdkrw() -> pd.Series:
    data = SESSION.get('https://api.frankfurter.app/2025-04-01..2026-03-31?from=USD&to=KRW', timeout=60).json()['rates']
    s = pd.Series({pd.Timestamp(k, tz='UTC'): v['KRW'] for k, v in data.items()}, dtype='float32').sort_index()
    daily = pd.date_range(START.floor('D'), END.floor('D'), freq='D', tz='UTC')
    s = s.reindex(daily).ffill().bfill().reindex(IDX.floor('D')).astype('float32')
    s.index = IDX
    return s


def rsi(s, n):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    down = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    rs = up / down.replace(0, np.nan)
    return (100 - 100/(1+rs)).astype('float32')


def zscore(s, n):
    m = s.rolling(n).mean()
    st = s.rolling(n).std()
    return ((s - m) / st.replace(0, np.nan)).astype('float32')


def build_df():
    u = load_upbit('KRW-USDT', 'u')
    b = load_upbit('KRW-BTC', 'b')
    g = load_binance()
    usd = load_usdkrw()
    df = pd.concat([u, b, g], axis=1)
    del u, b, g
    gc.collect()
    df['usdkrw'] = usd.values

    df['fair'] = (df['b_close'] / df['g_close']).astype('float32')
    df['gap'] = (df['u_close'] / df['fair'] - 1).astype('float32')
    df['kimchi'] = (df['b_close'] / (df['g_close'] * df['usdkrw']) - 1).astype('float32')

    prev = df['u_close'].shift(1)
    tr = pd.concat([
        (df['u_high'] - df['u_low']).abs(),
        (df['u_high'] - prev).abs(),
        (df['u_low'] - prev).abs(),
    ], axis=1).max(axis=1)
    df['atr14'] = (tr.rolling(14).mean() / df['u_close']).astype('float32')

    for n in [1,3,5,15,60]:
        df[f'ur{n}'] = df['u_close'].pct_change(n).astype('float32')
    df['uema15'] = (df['u_close']/df['u_close'].ewm(span=15, adjust=False).mean()-1).astype('float32')
    df['uema60'] = (df['u_close']/df['u_close'].ewm(span=60, adjust=False).mean()-1).astype('float32')
    df['rsi7'] = (rsi(df['u_close'],7)/100).astype('float32')
    df['rsi14'] = (rsi(df['u_close'],14)/100).astype('float32')
    df['ubz20'] = zscore(df['u_close'],20)
    df['ubz60'] = zscore(df['u_close'],60)
    df['uvz60'] = zscore(np.log1p(df['u_tp']),60)
    df['gvz60'] = zscore(np.log1p(df['g_tp']),60)
    df['bvz60'] = zscore(np.log1p(df['b_tp']),60)

    for n in [5,15,60]:
        df[f'br{n}'] = df['b_close'].pct_change(n).astype('float32')
        df[f'gr{n}'] = df['g_close'].pct_change(n).astype('float32')
        df[f'div{n}'] = (df[f'br{n}'] - df[f'gr{n}']).astype('float32')
    df['gz60'] = zscore(df['gap'],60)
    df['gz240'] = zscore(df['gap'],240)
    df['gm15'] = df['gap'].diff(15).astype('float32')
    df['kz1440'] = zscore(df['kimchi'],1440)
    df['km60'] = df['kimchi'].diff(60).astype('float32')
    df['fr5'] = df['fair'].pct_change(5).astype('float32')
    df['fr15'] = df['fair'].pct_change(15).astype('float32')

    upper = df['u_high'] - pd.concat([df['u_open'], df['u_close']], axis=1).max(axis=1)
    lower = pd.concat([df['u_open'], df['u_close']], axis=1).min(axis=1) - df['u_low']
    df['wick'] = ((upper - lower)/df['u_close']).astype('float32')
    df['range'] = ((df['u_high'] - df['u_low'])/df['u_open']).astype('float32')
    df['hsin'] = np.sin(2*np.pi*IDX.hour/24).astype('float32')
    df['hcos'] = np.cos(2*np.pi*IDX.hour/24).astype('float32')
    return df


FEATURES = ['ur1','ur3','ur5','ur15','ur60','uema15','uema60','rsi7','rsi14','ubz20','ubz60','uvz60','gvz60','bvz60','atr14','br5','br15','br60','gr5','gr15','gr60','div5','div15','gap','gz60','gz240','gm15','kimchi','kz1440','km60','fr5','fr15','wick','range','hsin','hcos']


class Cfg:
    def __init__(self, horizon, thr_bp, grid_mult, max_alloc):
        self.horizon = horizon
        self.thr_bp = thr_bp
        self.grid_mult = grid_mult
        self.max_alloc = max_alloc


CONFIGS = [Cfg(h,t,g,m) for h in (5,10,15) for t in (3.0,5.0,7.0) for g in (0.8,1.2) for m in (0.7,1.0)]


def fit_preds(df):
    preds = {}
    for h in sorted({c.horizon for c in CONFIGS}):
        y = (df['u_close'].shift(-h) / df['u_open'] - 1).astype('float32')
        valid = df[FEATURES].notna().all(axis=1) & y.notna()
        pipe = Pipeline([('imp', SimpleImputer(strategy='median')), ('sc', StandardScaler()), ('ridge', Ridge(alpha=6.0))])
        pipe.fit(df.loc[valid, FEATURES], y.loc[valid])
        preds[h] = pd.Series(pipe.predict(df[FEATURES]).astype('float32'), index=df.index)
    return preds


def simulate(df, pred, cfg):
    op = df['u_open'].to_numpy(np.float32)
    hi = df['u_high'].to_numpy(np.float32)
    lo = df['u_low'].to_numpy(np.float32)
    cl = df['u_close'].to_numpy(np.float32)
    gz = df['gz60'].fillna(0).to_numpy(np.float32)
    gzL = df['gz240'].fillna(0).to_numpy(np.float32)
    kz = df['kz1440'].fillna(0).to_numpy(np.float32)
    br = df['br15'].fillna(0).to_numpy(np.float32)
    gr = df['gr15'].fillna(0).to_numpy(np.float32)
    atr = df['atr14'].fillna(np.float32(df['atr14'].median())).to_numpy(np.float32)
    pv = pred.fillna(0).to_numpy(np.float32)

    krw = np.float64(INITIAL_CAPITAL)
    qty = np.float64(0.0)
    eq = np.empty(len(df), dtype=np.float64)
    trades = 0
    turnover = np.float64(0.0)
    weights = np.array([0.55,0.30,0.15], dtype=np.float64)
    th = cfg.thr_bp / 10000.0

    for i in range(len(df)):
        equity = krw + qty * np.float64(op[i])
        alloc = 0.0 if equity <= 0 else (qty * np.float64(op[i])) / equity
        pred_score = max(min(float(pv[i]) / max(th, 1e-8), 2.0), -2.0)
        btc_risk = -float(gr[i]) - float(br[i])
        meanrev = max(-float(gz[i]), 0.0) * 0.28 + max(-float(gzL[i]),0.0) * 0.18
        riskoff = max(btc_risk,0.0) * 11.0 + max(-float(kz[i]),0.0) * 0.10
        sellp = max(float(gz[i]),0.0) * 0.36 + max(float(kz[i]),0.0) * 0.09 + max(-btc_risk,0.0) * 7.0
        target = cfg.max_alloc * max(pred_score * 0.58 + meanrev + riskoff - sellp, 0.0)
        target = min(target, cfg.max_alloc)
        if gz[i] > 1.8: target *= 0.35
        if gzL[i] > 2.1: target *= 0.18
        if atr[i] > 0.0025: target *= 0.55
        diff = target - alloc
        grid = max(0.00025, float(atr[i]) * cfg.grid_mult)

        if diff > 0.015 and krw > 10000:
            desired = min(diff * equity, krw)
            for lv in range(3):
                limit = math.floor(np.float64(op[i]) * (1 - grid * (0.35 + 0.75 * lv)))
                #if lo[i] <= limit:
                if lo[i] < limit:
                    notional = min(desired * weights[lv], krw)
                    if notional <= 0: continue
                    buy_qty = notional / limit
                    krw -= notional * (1 - MAKER_REBATE)
                    qty += buy_qty
                    turnover += notional
                    trades += 1
        elif diff < -0.015 and qty * np.float64(op[i]) > 10000:
            desired = min((-diff) * equity, qty * np.float64(op[i]))
            for lv in range(3):
                limit = math.ceil(np.float64(op[i]) * (1 + grid * (0.35 + 0.75 * lv)))
                #if hi[i] >= limit:
                if hi[i] > limit:
                    notional = min(desired * weights[lv], qty * limit)
                    if notional <= 0: continue
                    sell_qty = notional / limit
                    krw += notional * (1 + MAKER_REBATE)
                    qty -= sell_qty
                    turnover += notional
                    trades += 1
        eq[i] = krw + qty * np.float64(cl[i])

    eqs = pd.Series(eq, index=df.index)
    dd = eqs / eqs.cummax() - 1
    mr = eqs.resample('M').last().pct_change().fillna(eqs.resample('M').last().iloc[0] / INITIAL_CAPITAL - 1)
    total = eqs.iloc[-1] / INITIAL_CAPITAL - 1
    maxdd = float(dd.min())
    posm = float((mr > 0).mean())
    score = total - 1.15 * abs(maxdd) + 0.12 * posm
    return {'equity': eqs, 'monthly': mr, 'total': total, 'maxdd': maxdd, 'trades': trades, 'turnover': float(turnover), 'score': score}


def benchmark(df):
    qty = INITIAL_CAPITAL / float(df['u_open'].iloc[0])
    eq = qty * df['u_close']
    dd = eq / eq.cummax() - 1
    mr = eq.resample('M').last().pct_change().fillna(eq.resample('M').last().iloc[0] / INITIAL_CAPITAL - 1)
    return {'equity': eq, 'monthly': mr, 'total': float(eq.iloc[-1]/INITIAL_CAPITAL - 1), 'maxdd': float(dd.min())}


def main():
    df = build_df()
    preds = fit_preds(df)
    rows = []
    best = None
    for cfg in CONFIGS:
        sim = simulate(df, preds[cfg.horizon], cfg)
        row = {'horizon': cfg.horizon, 'thr_bp': cfg.thr_bp, 'grid_mult': cfg.grid_mult, 'max_alloc': cfg.max_alloc,
               'score': sim['score'], 'total_return': sim['total'], 'max_dd': sim['maxdd'], 'trades': sim['trades'], 'turnover': sim['turnover']}
        rows.append(row)
        if best is None or sim['score'] > best['sim']['score']:
            best = {'cfg': cfg, 'sim': sim, 'row': row}
    search = pd.DataFrame(rows).sort_values('score', ascending=False)
    search.to_csv(OUTDIR / 'config_search_results.csv', index=False)
    bench = benchmark(df)
    monthly = pd.DataFrame({'strategy_return_pct': best['sim']['monthly'].mul(100), 'buy_hold_return_pct': bench['monthly'].mul(100)})
    monthly.index = monthly.index.astype(str)
    monthly.to_csv(OUTDIR / 'monthly_returns.csv')
    summary = {
        'period_start_utc': str(START), 'period_end_utc': str(END),
        'initial_capital_krw': INITIAL_CAPITAL, 'maker_rebate_assumption': MAKER_REBATE,
        'best_config': {'horizon': best['cfg'].horizon, 'thr_bp': best['cfg'].thr_bp, 'grid_mult': best['cfg'].grid_mult, 'max_alloc': best['cfg'].max_alloc},
        'strategy_total_return_pct': best['sim']['total'] * 100,
        'strategy_final_equity_krw': float(best['sim']['equity'].iloc[-1]),
        'strategy_max_drawdown_pct': best['sim']['maxdd'] * 100,
        'strategy_trades': best['sim']['trades'], 'strategy_turnover_krw': best['sim']['turnover'],
        'benchmark_total_return_pct': bench['total'] * 100, 'benchmark_max_drawdown_pct': bench['maxdd'] * 100,
    }
    with open(OUTDIR / 'summary.json', 'w') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False))
    print(monthly.round(3).to_string())

if __name__ == '__main__':
    main()
