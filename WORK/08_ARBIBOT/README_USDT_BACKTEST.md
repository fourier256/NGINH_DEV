# KRW-USDT HFT 백테스트 실행 가이드

`usdt_hft_backtest.py`는 다음을 결합한 1분봉 전략을 백테스트합니다.

- USDT 자체 모멘텀/역추세: Bollinger z-score, RSI, ATR
- BTC 간접 영향: KRW-BTC 수익률 기반 스프레드 z-score
- 거래량 레짐: USDT 볼륨 비율(현재/60분 평균)
- 김치프리미엄 proxy: `KRW-BTC / (BTC-USDT * KRW-USDT)`
- 부분 그리드 매수/분할 익절
- 체결 규칙(요청사항 반영)
  - 매수: 신호 캔들의 `open` 가격 지정가, 해당 캔들의 `low < open`이면 체결
  - 매도: 신호 캔들의 `open` 가격 지정가, 해당 캔들의 `high > open`이면 체결
  - 슬리피지 0, 메이커 인센티브 +0.01%

## 입력 파일 형식
CSV 헤더:

```csv
timestamp,open,high,low,close,volume
```

- `timestamp`: ISO8601(예: `2026-04-07T00:01:00+00:00`) 또는 epoch seconds
- 1분봉 기준
- 파일 3개 권장
  - `usdt_1m.csv` (KRW-USDT)
  - `btc_krw_1m.csv` (KRW-BTC)
  - `btc_usdt_1m.csv` (BTC-USDT, optional)

## 실행 예시

```bash
python WORK/08_ARBIBOT/usdt_hft_backtest.py \
  --usdt data/usdt_1m.csv \
  --btc-krw data/btc_krw_1m.csv \
  --btc-usdt data/btc_usdt_1m.csv \
  --seed 1000000000 \
  --out WORK/08_ARBIBOT/monthly_returns.csv
```

실행 결과:
- 콘솔: 최종 자산, 누적 수익률, MDD, 트레이드 수
- CSV: 월별 수익률
