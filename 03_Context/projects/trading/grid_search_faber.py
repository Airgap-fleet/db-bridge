import yfinance as yf
import pandas as pd
import numpy as np
import os, json, datetime, itertools, time, sys

# ----- CONFIG -----
START_DATE = '2003-01-01'
RAW_ASSETS = [
    'SPY','IVV','VOO','VTI','IEFA','VXUS','EFA','EEM','IEUR','IEEM',
    'AGG','BND','TLT','IEI','SHY','LQD','HYG','JNK',
    'GLD','SLV','USO','UNG','DBB','DBC','VNQ','VNQI',
    'XLF','XLK','XLE','XLV','XLI','XLY','XLP','XLB','XLU','XLC',
    'UUP','UDN','EWT','EWZ','EWJ','EWG','EWU','EWC','EWA','EEMS',
    'IEUS','SCZ','FEZ','IEV'
]
BAD = {'IEEM','XLP','EWG','EFA'}
ASSETS = [a for a in RAW_ASSETS if a not in BAD]
COST_PER_TURN = 0.0005  # 5 bps
MAX_RUNTIME_SEC = 30 * 60  # 30 minutes
# ------------------

def load_data():
    price = pd.DataFrame()
    for sym in ASSETS:
        try:
            df = yf.download(sym, start=START_DATE, progress=False)
            if df.empty:
                continue
            col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            price[sym] = df[col]
        except Exception:
            pass
    price = price.ffill().dropna()
    return price

def run_one(price, sma_len, vol_len, leverage_cap, vol_target=None):
    returns = price.pct_change().fillna(0)
    sma = price.rolling(sma_len, min_periods=sma_len).mean()
    signal = (price > sma.shift(1)).astype(float).fillna(0)
    vol = returns.rolling(vol_len, min_periods=vol_len).std().shift(1)
    inv_vol = 1.0 / vol.replace(0, np.nan)
    inv_vol = inv_vol.fillna(0)
    raw = signal * inv_vol
    weight_sum = raw.sum(axis=1).replace(0, np.nan)
    weights = raw.div(weight_sum, axis=0).fillna(0)
    if vol_target is not None:
        target_daily = vol_target / np.sqrt(252)
        port_vol = np.sqrt((weights**2 * vol**2).sum(axis=1))
        # avoid division by zero
        scale = np.where(~np.isnan(port_vol) & (port_vol != 0), target_daily / port_vol, 0.0)
        # scale is a Series aligned with index
        weights = weights.multiply(scale, axis=0)
    abs_sum = np.abs(weights).sum(axis=1)
    scale_leverage = np.where(abs_sum > leverage_cap, leverage_cap / abs_sum, 1.0)
    weights = weights.multiply(scale_leverage, axis=0)
    gross = (weights * returns).sum(axis=1)
    prev = weights.shift(1).fillna(0)
    turnover = (weights - prev).abs().sum(axis=1)
    cost = turnover * COST_PER_TURN
    net = gross - cost
    if len(net) == 0:
        return None
    total = (1 + net).prod() - 1
    years = (net.index[-1] - net.index[0]).days / 365.25
    cagr = (1 + total) ** (1 / years) - 1 if years > 0 else 0.0
    vol_ann = np.sqrt(252) * np.std(net)
    sharpe = cagr / vol_ann if vol_ann != 0 else -np.inf
    cum = (1 + net).cumprod()
    dd = (cum - cum.cummax()) / cum.cummax()
    max_dd = float(dd.min())
    ann_turnover = float(np.mean(turnover) * 252)
    return {
        'SMA': int(sma_len),
        'VOL': int(vol_len),
        'LEV': float(leverage_cap),
        'VOL_TARGET': None if vol_target is None else float(vol_target),
        'CAGR': float(cagr),
        'VOL_ANN': float(vol_ann),
        'SHARPE': float(sharpe),
        'MAXDD': max_dd,
        'TURNOVER': ann_turnover
    }

def main():
    price = load_data()
    sma_list = [30,40,50,60,70]
    vol_list = [60,75,90,105,120]
    lev_list = [1.0,1.2,1.5,1.8,2.0]
    vol_target_list = [0.05,0.10,0.15]
    results = []
    start = time.time()
    for s, v, l, t in itertools.product(sma_list, vol_list, lev_list, vol_target_list):
        if time.time() - start > MAX_RUNTIME_SEC:
            break
        res = run_one(price, s, v, l, t)
        if res is None:
            continue
        results.append(res)
    out_dir = r'C:\The Force\03_Context\projects\trading\grid_search'
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(out_dir, f'run_{timestamp}.json')
    if results:
        best = max(results, key=lambda x: x['SHARPE'])
        summary = {
            'generated_at': datetime.datetime.now().isoformat(),
            'total_combinations_tested': len(results),
            'best': best
        }
        payload = {'results': results, 'summary': summary}
    else:
        payload = {'results': [], 'summary': {}}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    print(f'Finished. Best Sharpe {best["SHARPE"]:.3f} (SMA={best["SMA"]}, VOL={best["VOL"]}, LEV={best["LEV"]}, TARGET={best["VOL_TARGET"]})')
    print(f'Results saved to {out_path}')

if __name__ == '__main__':
    main()