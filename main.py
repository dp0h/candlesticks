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
    symbols = np.loadtxt(fname, dtype='S10', comments='#', skiprows=0)
    if not check_db():
        init_db(symbols, from_date, to_date)
    for s in symbols:
        mdata = access.get_marketdata(s, from_date, to_date, [access.Column.Open, access.Column.High, access.Column.Low, access.Column.Close])
        find_candlestick_patterns(*to_talib_format(mdata))
        break  # remove
    # TODO:
    # Analize prices after event happens (for 10 days). Consider open and close prices.
    # Show graph for average case


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
