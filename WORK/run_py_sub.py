import time
import json
import joblib
import logging
import numpy as np
import pandas as pd
import pyupbit
from binance.client import Client
from datetime import datetime, timedelta, timezone
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# ------------------------------------------
# 설정 (Configuration)
# ------------------------------------------
# API 키 설정 (환경 변수나 별도 설정 파일에서 가져오시오)
UPBIT_ACCESS_KEY = "YOUR_UPBIT_ACCESS_KEY"
UPBIT_SECRET_KEY = "YOUR_UPBIT_SECRET_KEY"
BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_SECRET_KEY = "YOUR_BINANCE_SECRET_KEY"

# 모델 및 경로 설정
MODEL_PATH = "./FIT_OUT_DIR"  # 모델이 저장된 폴더
MODEL_FILE = "model_h5.joblib"  # 예: 5분 예측 모델 로드 (사용하려는 horizon에 맞게 변경)

# 기본 파라미터 (백테스트 최적화 결과를 반영)
INITIAL_CAPITAL = 1_000_000_000.0  # 초기 자본 (실제 잔고 조회로 대체 필요)
MAKER_REBATE = 0.0001
MAX_ALLOC = 1.0      # 최대 할당 비중 (백테스트 best config)
THR_BP = 5.0         # 임계값 (백테스트 best config)
GRID_MULT = 1.2      # 그리드 배율 (백테스트 best config)
WINDOW_SIZE = 3000   # 데이터 윈도우 크기 (여유 있게 3000개)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname] %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------------------
# 피처 계산 함수 (백테스트 코드와 동일해야 함)
# ------------------------------------------
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

def calculate_features(df, usdkrw_rate):
    """백테스트의 build_df 로직을 현재 데이터프레임에 적용"""
    # 복사본 생성 및 정렬
    df = df.copy().sort_index()
    
    # USD/KRW 매핑 (단순화를 위해 현재 환율 하나를 전체 기간에 적용하거나, 
    # 실전에서는 daily 데이터를 merge 해야 함. 여기서는 최신 환율 하나를 사용하는 것으로 단순화)
    df['usdkrw'] = usdkrw_rate

    # 지표 계산
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
    
    # 시간 변수
    df['hsin'] = np.sin(2*np.pi*df.index.hour/24).astype('float32')
    df['hcos'] = np.cos(2*np.pi*df.index.hour/24).astype('float32')
    
    return df

# ------------------------------------------
# 데이터 매니저 클래스
# ------------------------------------------
class DataManager:
    def __init__(self, upbit_access, upbit_secret, binance_api, binance_secret):
        self.upbit = pyupbit.Upbit(upbit_access, upbit_secret)
        self.binance = Client(binance_api, binance_secret)
        
        # 캐시 데이터프레임 초기화
        self.df = pd.DataFrame()
        self.last_timestamp = None
        
        # 초기 데이터 로드
        self._initialize_data()

    def _initialize_data(self):
        """프로그램 시작 시 과거 데이터 WINDOW_SIZE 만큼 로드"""
        logger.info("Initializing historical data...")
        
        # 1. Upbit USDT/KRW (u)
        # pyupbit는 최대 200개까지 리턴하므로 루프 돌아야 함
        u_dfs = []
        for i in range(WINDOW_SIZE // 200):
            # count=200, to 파라미터 등을 이용해 과거 데이터 가져오기 (간략화를 위해 get_ohlcv 사용)
            # 실제로는 to 파라미터를 이용해 시간을 거슬러 올라가며 수집 필요
            # 여기서는 가장 최근 200개만 예시로 가져옴 (실전에서는 루프 구현 필수)
            # 편의상 최근 200개만 가져오는 것으로 가정하고 작성 (1440개 필요시 로직 추가 필요)
            # TODO: 과거 데이터 3000개 가져오는 로직 구현
            pass 
        
        # 간소화를 위해 최근 200개만 가져오는 것으로 가정 (실전에서는 WINDOW_SIZE 채워야 함)
        # 실제로는 pyupbit.get_ohlcv(ticker="KRW-USDT", interval="minute1", count=200)
        
        # 예시용 더미 데이터 생성 (실제 API 호출로 대체하세요)
        # 과거 데이터 로드 로직은 길어지므로 "업데이트" 로직에 집중합니다.
        logger.warning("초기 데이터 로드 로직 구현 필요 (DataManager._initialize_data)")

    def update_data(self):
        """매 분 신규 데이터를 가져와 기존 DF에 병합"""
        now = datetime.now(timezone.utc)
        
        # 1. Upbit Data
        # 최근 1분봉 1개 가져오기 (완성된 캔들)
        u_new = pyupbit.get_ohlcv(ticker="KRW-USDT", interval="minute1", count=1)
        b_new = pyupbit.get_ohlcv(ticker="KRW-BTC", interval="minute1", count=1)
        
        # 2. Binance Data
        # python-binance는 ms 단위 timestamp 사용
        # 가장 최근 완성된 1분봉 가져오기 (현재 시간 - 1분)
        start_str = str(int((now - timedelta(minutes=1)).timestamp() * 1000))
        g_klines = self.binance.get_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, startTime=start_str, limit=1)
        
        if not g_klines:
            logger.warning("Binance data fetch failed")
            return False

        # 데이터 파싱 및 DataFrame 생성
        try:
            ts = u_new.index[0].to_pydatetime().replace(tzinfo=timezone.utc)
            
            new_row = {
                # Upbit USDT
                'u_open': u_new['open'].iloc[0], 'u_high': u_new['high'].iloc[0], 
                'u_low': u_new['low'].iloc[0], 'u_close': u_new['close'].iloc[0],
                'u_tp': u_new['value'].iloc[0], 'u_tv': u_new['volume'].iloc[0],
                # Upbit BTC
                'b_open': b_new['open'].iloc[0], 'b_high': b_new['high'].iloc[0],
                'b_low': b_new['low'].iloc[0], 'b_close': b_new['close'].iloc[0],
                'b_tp': b_new['value'].iloc[0], 'b_tv': b_new['volume'].iloc[0],
                # Binance BTC
                'g_open': float(g_klines[0][1]), 'g_high': float(g_klines[0][2]),
                'g_low': float(g_klines[0][3]), 'g_close': float(g_klines[0][4]),
                'g_tv': float(g_klines[0][5]), 'g_tp': float(g_klines[0][7]) # Quote asset volume
            }
            
            # 데이터프레임에 추가
            new_df = pd.DataFrame([new_row], index=[ts])
            
            if self.df.empty:
                self.df = new_df
            else:
                # 기존 데이터에 append
                self.df = pd.concat([self.df, new_df])
                
                # 윈도우 사이즈 유지 (오래된 데이터 삭제)
                if len(self.df) > WINDOW_SIZE:
                    self.df = self.df.iloc[-WINDOW_SIZE:]
            
            self.last_timestamp = ts
            return True

        except Exception as e:
            logger.error(f"Data parsing error: {e}")
            return False

# ------------------------------------------
# 메인 로직
# ------------------------------------------
def main():
    # 1. 객체 초기화
    logger.info("System initializing...")
    
    # 모델 로드
    try:
        model = joblib.load(f"{MODEL_PATH}/{MODEL_FILE}")
        logger.info(f"Model loaded: {MODEL_FILE}")
    except Exception as e:
        logger.error(f"Model load failed: {e}")
        return

    # 데이터 매니저 초기화 (실제 API 키 필요)
    # dm = DataManager(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY, BINANCE_API_KEY, BINANCE_SECRET_KEY)
    # Upbit 실행 객체
    # upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)
    
    # 테스트용 Dummy Data Manager (API 키 없이 돌릴 때)
    class DummyDataManager:
        def __init__(self):
            self.df = pd.DataFrame() # 테스트용 빈 DF
        def update_data(self):
            # 테스트용 데이터 생성 로직
            now = datetime.now(timezone.utc)
            self.df.loc[now, 'u_open'] = 1350.0 # 예시값
            return True
            
    dm = DummyDataManager()
    
    logger.info("Starting main loop...")
    
    FEATURES = ['ur1','ur3','ur5','ur15','ur60','uema15','uema60','rsi7','rsi14','ubz20','ubz60','uvz60','gvz60','bvz60','atr14','br5','br15','br60','gr5','gr15','gr60','div5','div15','gap','gz60','gz240','gm15','kimchi','kz1440','km60','fr5','fr15','wick','range','hsin','hcos']

    while True:
        # 매 분 00초에 실행 (간단한 동기화)
        now = datetime.now()
        if now.second == 0:
            logger.info("--- New Minute Start ---")
            
            # 1. 데이터 업데이트
            if dm.update_data():
                # 2. 환율 업데이트 (여기서는 고정값 사용, 실전은 API 호출 권장)
                current_usdkrw = 1350.0 
                
                # 3. 피처 계산
                df_features = calculate_features(dm.df, current_usdkrw)
                
                # 가장 최신 데이터(마지막 행) 가져오기
                if len(df_features) > 0:
                    latest = df_features.iloc[[-1]]
                    
                    # 피처 결측치 확인 (학습시 사용된 피처만 추출)
                    X_live = latest[FEATURES]
                    
                    # 4. 예측
                    pred_return = model.predict(X_live)[0]
                    logger.info(f"Predicted Return: {pred_return:.6f}")
                    
                    # 5. 타겟 포지션 계산 (백테스트 simulate 로직 활용)
                    # 여기서는 간단히 예측값이 양수면 매수, 음수면 매도 하는 로직 예시
                    # 실제로는 백테스트의 target 계산 로직(div, grid 등)을 그대로 구현해야 함
                    
                    # 백테스트 로직 일부 발췌 적용
                    th = THR_BP / 10000.0
                    pred_score = max(min(pred_return / max(th, 1e-8), 2.0), -2.0)
                    
                    # 간단한 리밸런싱 로직 예시
                    # target_alloc = 0.0 ~ 1.0
                    target_alloc = max(pred_score * 0.5, 0.0) # 단순화된 로직
                    
                    logger.info(f"Target Allocation: {target_alloc:.2f}")
                    
                    # 6. 주문 실행 (실전 코드)
                    # cur_krw = upbit.get_balance("KRW")
                    # cur_usdt = upbit.get_balance("KRW-USDT")
                    # cur_price = pyupbit.get_orderbook(ticker="KRW-USDT")['orderbook_units'][0]['ask_price']
                    
                    # target_usdt_qty = (cur_krw + cur_usdt * cur_price) * target_alloc / cur_price
                    # current_usdt_qty = cur_usdt
                    
                    # if target_usdt_qty > current_usdt_qty * 1.01:
                    #     # 매수
                    #     upbit.buy_market_order("KRW-USDT", (target_usdt_qty - current_usdt_qty) * cur_price)
                    # elif target_usdt_qty < current_usdt_qty * 0.99:
                    #     # 매도
                    #     upbit.sell_market_order("KRW-USDT", current_usdt_qty - target_usdt_qty)

            # 다음 분까지 대기 (CPU 점유율 방지)
            time.sleep(1)
        else:
            time.sleep(0.5)

if __name__ == "__main__":
    main()
