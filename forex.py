import os
from matplotlib.finance import candlestick2_ohlc as plt_candle
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import datetime
from oandapyV20 import API
import oandapyV20.endpoints.instruments as oandapy

now = datetime.datetime.now() - datetime.timedelta(hours=9)  # 標準時に合わせる
minutes = 61  # 60分取得
time_min = now - datetime.timedelta(minutes=120)  # 2時間前からデータを取得する
# start = datetime.datetime(year=2018,month=5,day=1)
time_min = time_min.strftime("%Y-%m-%dT%H:%M:00.000000Z")
# OANDA_API ACCESS-TOKEN
access_token = os.environ.get("ACCESS_TOKEN")
api = API(access_token = access_token, environment="practice")
request = oandapy.InstrumentsCandles(instrument = "USD_JPY",
               params = { "alignmentTimezone": "Japan", "from": start, "count": minutes, "granularity": "M1" })
api.request(request)

#filename = "candle.csv"
candle = pd.DataFrame.from_dict(
    [row['mid'] for row in request.response['candles']])
candle['time'] = [row['time'] for row in request.response['candles']]
#candle.to_csv(filename)

#candle = pd.read_csv('candle.csv')
candle = candle

sns.set_style("whitegrid")

#移動平均を求める
small_window = 5  # 5分平均線を求める
big_window = 20  # 　20分平均線求める
sma5 = pd.Series.rolling(candle.c, window=small_window).mean()
sma20 = pd.Series.rolling(candle.c, window=big_window).mean()

candle = candle[big_window:].reset_index(drop=True)
sma5 = sma5[big_window:].reset_index(drop=True)
sma20 = sma20[big_window:].reset_index(drop=True)

#ゴールデンクロス、デッドクロスを見つける
cross = sma5 > sma20
d_sma20 = sma20.shift(1) - sma20
# golden = (cross != cross.shift(1)) & (cross == True)
golden = (cross != cross.shift(1)) & (cross == True) & (d_sma20 <= 0)
# dead = (cross != cross.shift(1)) & (cross == False)
dead = (cross != cross.shift(1)) & (cross == False) & (d_sma20 >= 0)


#ゴールデンクロス、デッドクロスの位置をリスト化する
index_g = [i-1 for i, x in enumerate(golden) if x == True]
index_d = [i-1 for i, x in enumerate(dead) if x == True]

# X軸の見た目を整える
# 時間だけを切り出すために先頭からの12文字目から取るようにしている
xticks_number = 15  # 15分刻みに目盛りを書く
xticks_index = range(0, len(candle), xticks_number)
xticks_date = [candle.time.values[i][11:16] for i in xticks_index]

figure, ax = plt.subplots()
plt_candle(ax,
           opens=candle.o.values,
           highs=candle.h.values,
           lows=candle.l.values,
           closes=candle.c.values,
           width=0.6,
           colorup='#DC143C',
           colordown='#4169E1')
plt.plot(sma5, color='greenyellow', label='sma5')
plt.plot(sma20, color='darkgreen', label='sma20')
plt.scatter(index_g, sma20[index_g], color='red', s=500, label="golden cross")
plt.scatter(index_d, sma20[index_d], color='blue', s=500, label="dead cross")
plt.xticks(xticks_index, xticks_date, rotation=80)
plt.legend()
plt.show()
