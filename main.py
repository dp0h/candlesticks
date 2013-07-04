#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from collections import namedtuple
from copy import deepcopy
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

MktTypeNames = ['open', 'high', 'low', 'close']

MktItem = namedtuple('MktItem', ['date'] + MktTypeNames)


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

MktType = enum(*MktTypeNames)


class AverageMove(object):
    def __init__(self, size):
        val = [(0, 0)] * size
        self.__dict = {MktType.open: deepcopy(val), MktType.high: deepcopy(val),
                       MktType.low: deepcopy(val), MktType.close: deepcopy(val)}

    def add(self, type, idx, relative_val, val):
        self.__dict[type][idx] = (self.__dict[type][idx][0] + float(val)/relative_val, self.__dict[type][idx][1] + 1)

    def average(self, type):
        return [acc/cnt for (acc, cnt) in self.__dict[type]]


def to_talib_format(mdata):
    ''' Converts market daata to talib format '''
    return MktItem(np.array([datetime(x.year, x.month, x.day) for x in mdata.index]), np.array([float(x) for x in mdata[0]]), np.array([float(x) for x in mdata[1]]), np.array([float(x) for x in mdata[2]]), np.array([float(x) for x in mdata[3]]))


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


CONSIDERED_NDAYS = 10


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
        avg = AverageMove(CONSIDERED_NDAYS)

        #TODO: different results should be consideres separateley, since we coldn't consider 100 and -100 in one avg.
        for s in symbols:
            f = getattr(talib, a)
            res = f(mdata[s].open, mdata[s].high, mdata[s].low, mdata[s].close)
            res = list(res)
            for x in (idx for idx, val in enumerate(res) if val != 0):
                open = mdata[s].open[x]
                for i in range(CONSIDERED_NDAYS):
                    avg.add(MktType.open, i, open, mdata[s].open[x + i])
                    avg.add(MktType.high, i, open, mdata[s].high[x + i])
                    avg.add(MktType.low, i, open, mdata[s].low[x + i])
                    avg.add(MktType.close, i, open, mdata[s].close[x + i])
        print(avg.average(MktType.open))
        print(avg.average(MktType.high))
        print(avg.average(MktType.low))
        print(avg.average(MktType.close))
        # TODO: dates processing could be done using map-reduce, i.e. coungint average values
    # Show graph for all cases average case


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
