#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
import numpy as np
from marketdata import symbol, schema, update, access
import talib


def check_db():
    ''' Checks if marketdata db is created '''
    try:
        l = list(symbol.symbols())
        if len(l) > 0:
            return True
    except:
        pass


def init_db(symbols, from_date, to_date):
    ''' Initializes marketdata db '''
    schema.create()
    schema.disable_warnings()
    symbol.add_symbols(symbols)
    update.update_marketdata(from_date, to_date)


def to_talib_format(mdata):
    ''' Converts market daata to talib format '''
    return (np.array([datetime(x.year, x.month, x.day) for x in mdata.index]), np.array([float(x) for x in mdata[0]]), np.array([float(x) for x in mdata[1]]), np.array([float(x) for x in mdata[2]]), np.array([float(x) for x in mdata[3]]))


def find_candlestick_patterns(dates, open, high, low, close):
    ''' Tries to recognize different candlestick patterns for specified marketdata '''
    palg = [x for x in talib.get_functions() if 'CDL' in x]
    for a in palg:
        f = getattr(talib, a)
        res = f(open, high, low, close)
        res = list(res)
        if len([x for x in res if x != 0]) > 0:
            print(a)
            for idx, val in enumerate(res):
                if val != 0:
                    print('%s: %s' % (str(dates[idx]).split(' ')[0], val))


def main(fname, from_date, to_date):
    # TODO: perhaps marketdata could be rewritten with use of MongoDb
    #symbols = np.loadtxt(fname, dtype='S10', comments='#', skiprows=0)
    symbols = ['BG.L']  # TEMP
    if not check_db():
        init_db(symbols, from_date, to_date)

    # TODO: put all market data in separate class where we have logic to retrieve anything with lazy logic + caching
    mdata = {}
    for s in symbols:
        mdata[s] = to_talib_format(access.get_marketdata(s, from_date, to_date, [access.Column.Open, access.Column.High, access.Column.Low, access.Column.Close]))

    #palg = [x for x in talib.get_functions() if 'CDL' in x]
    palg = ['CDLTHRUSTING']  # TEMP
    for a in palg:
        cnt = 0
        aopen = [0] * 10
        ahigh = [0] * 10
        alow = [0] * 10
        aclose = [0] * 10

        for s in symbols:
            f = getattr(talib, a)
            res = f(mdata[s][1], mdata[s][2], mdata[s][3], mdata[s][4])
            res = list(res)
            #dates = [mdata[s][0][idx] for idx, val in enumerate(res) if val != 0]
            for x in (idx for idx, val in enumerate(res) if val != 0):
                open = mdata[s][1][x]
                cnt += 1
                for i in range(10):
                    aopen[i] = mdata[s][1][x + i]/open
                    ahigh[i] = mdata[s][2][x + i]/open
                    alow[i] = mdata[s][3][x + i]/open
                    aclose[i] = mdata[s][4][x + i]/open
        for x in range(10):
            aopen[i] /= cnt
            ahigh[i] /= cnt
            alow[i] /= cnt
            aclose[i] /= cnt
        print(aopen)
        print(ahigh)
        print(alow)
        print(aclose)
        # TODO: dates processing could be done using map-reduce, i.e. coungint average values
    # TODO:
    # Analize prices after event happens (for 10 days). Consider open and close prices.
    # Show graph for average case


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
