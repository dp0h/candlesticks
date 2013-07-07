# coding:utf-8

from datetime import datetime, timedelta
from helpers import show_candlestick


def graph():
    dt = datetime.now() - timedelta(days=10)
    #date = [dt.toordinal(), ]

    date = []
    for x in range(7):
        dt = dt + timedelta(days=1)
        date.append(dt.toordinal())
        #date.append(x)
    print(date)
    open = [1258.0, 1226.50, 1190.0, 1242.5, 1253.5, 1276.5, 1252.0]
    high = [1265.0, 1245.93, 1262.5, 1254.5, 1284.0, 1293.5, 1264.0]
    low = [1230.0, 1215.50, 1180.0, 1227.0, 1251.0, 1262.0, 1245.5]
    close = [1236.0, 1220.0, 1246.0, 1253.5, 1277.5, 1262.0, 1263.5]

    res = []
    for x in range(7):
        res.append((date[x], open[x], close[x], high[x], low[x], 1000))

    show_candlestick(res)

if __name__ == '__main__':
    graph()
