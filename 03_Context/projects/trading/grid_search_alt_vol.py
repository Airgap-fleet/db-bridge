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

def atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period, min_periods=period).mean()
    return atr

def yang_zhang(df, period=14):
    # Using the Yang-Zhang volatility estimator
    # Requires open, high, low, close
    o = df['Open']
    h = df['High']
    l = df['Low']
    c = df['Close']
    # Calculate the overnight volatility
    vo = np.log(o / c.shift())
    # Calculate the open-to-close volatility
    vc = np.log(c / o)
    # Calculate the Rogers-Satchell volatility
    rs = np.log(h / l) * np.log(h / c) + np.log(l / o) * np.log(l / c)
    # Window sizes
    window = period
    # Calculate the various volatilities
    vo2 = vo.rolling(window, min_periods=window).var()
    vc2 = vc.rolling(window, min_periods=window).var()
    rs2 = rs.rolling(window, min_periods=window).mean()
    # Yang-Zhang volatility
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    yz2 = vo2 + k * vc2 + (1 - k) * rs2
    yz = np.sqrt(yz2)
    return yz

def run_one(price, sma_len, vol_len, leverage_cap, vol_target=None, vol_method='std'):
    # Calculate returns
    returns = price.pct_change().fillna(0)
    # Calculate SMA signal
    sma = price.rolling(sma_len, min_periods=sma_len).mean()
    signal = (price > sma.shift(1)).astype(float).fillna(0)
    # Calculate volatility based on method
    if vol_method == 'std':
        vol = returns.rolling(vol_len, min_periods=vol_len).std().shift(1)
    elif vol_method == 'atr':
        # We need high, low, close for ATR - we don't have them in price DataFrame (only close/adj close)
        # For simplicity, we'll approximate ATR using price alone (not accurate) or skip.
        # Since we don't have OHLC data, we'll fallback to std for this test.
        vol = returns.rolling(vol_len, min_periods=vol_len).std().shift(1)
    elif vol_method == 'ewma':
        vol = returns.ewm(span=vol_len).std().shift(1)
    elif vol_method == 'yang_zhang':
        # We don't have OHLC, so fallback to std
        vol = returns.rolling(vol_len, min_periods=vol_len).std().shift(1)
    else:
        vol = returns.rolling(vol_len, min_periods=vol_len).std().shift(1)
    # Inverse volatility
    inv_vol = 1.0 / vol.replace(0, np.nan)
    inv_vol = inv_vol.fillna(0)
    # Raw weights
    raw = signal * inv_vol
    weight_sum = raw.sum(axis=1).replace(0, np.nan)
    weights = raw.div(weight_sum, axis=0).fillna(0)
    # Volatility target scaling
    if vol_target is not None:
        target_daily = vol_target / np.sqrt(252)
        # Portfolio volatility based on weights and covariance (simplified: assume uncorrelated)
        port_vol = np.sqrt((weights**2 * vol**2).sum(axis=1))
        scale = np.where(~np.isnan(port_vol) & (port_vol != 0), target_daily / port_vol, 0.0)
        weights = weights.multiply(scale, axis=0)
    # Leverage cap
    abs_sum = np.abs(weights).sum(axis=1)
    scale_leverage = np.where(abs_sum > leverage_cap, leverage_cap / abs_sum, 1.0)
    weights = weights.multiply(scale_leverage, axis=0)
    # Gross returns
    gross = (weights * returns).sum(axis=1)
    # Turnover and cost
    prev = weights.shift(1).fillna(0)
    turnover = (weights - prev).abs().sum(axis=1)
    cost = turnover * COST_PER_TURN
    net = gross - cost
    if len(net) == 0:
        return None
    # Performance metrics
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
        'VOL_METHOD': vol_method,
        'CAGR': float(cagr),
        'VOL_ANN': float(vol_ann),
        'SHARPE': float(sharpe),
        'MAXDD': max_dd,
        'TURNOVER': ann_turnover
    }

def main():
    price = load_data()
    # Focused grid around the best from previous run: SMA~20, VOL~80, LEV~2.5, TARGET~0.06
    sma_list = [15, 18, 20, 22, 25]
    vol_list = [60, 70, 80, 90, 100]
    lev_list = [2.0, 2.25, 2.5, 2.75, 3.0]
    vol_target_list = [0.04, 0.05, 0.06, 0.07, 0.08]
    vol_methods = ['std', 'ewma']  # We'll test std and ewma; atr and yang_zhang need OHLC
    results = []
    start = time.time()
    for s, v, l, t, m in itertools.product(sma_list, vol_list, lev_list, vol_target_list, vol_methods):
        if time.time() - start > MAX_RUNTIME_SEC:
            break
        res = run_one(price, s, v, l, t, m)
        if res is None:
            continue
        results.append(res)
    out_dir = r'C:\The Force\03_Context\projects\trading\grid_search'
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(out_dir, f'run_alt_vol_{timestamp}.json')
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
    print(f'Finished. Best Sharpe {best["SHARPE"]:.3f} (SMA={best["SMA"]}, VOL={best["VOL"]}, LEV={best["LEV"]}, TARGET={best["VOL_TARGET"]}, METHOD={best["VOL_METHOD"]})')
    print(f'Results saved to {out_path}')

if __name__ == '__main__':
    main()