#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
import numpy as np
from marketdata import symbol, schema, update, access
from helpers import memoized, talib_candlestick_funcs, talib_call, load_symbols


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

MktTypes = ['open', 'high', 'low', 'close']


class AverageChange(object):
    ''' Class for calculating normalized average values '''
    def __init__(self, size):
        self.__dict = {}
        for x in MktTypes:
            self.__dict[x] = [(0, 0)] * size

    def add_item(self, type, idx, relative_val, val):
        acc = self.__dict[type][idx][0] + float(val)/relative_val
        cnt = self.__dict[type][idx][1] + 1
        self.__dict[type][idx] = (acc, cnt)

    def add(self, type, relative_val, vals):
        for idx, val in enumerate(vals):
            self.add_item(type, idx, relative_val, val)

    def average(self, type):
        return [acc/cnt for (acc, cnt) in self.__dict[type] if cnt > 0]

    def cnt(self):
        return self.__dict['open'][0][1]

    def __repr__(self):
        val = ['%s: %s' % (x, str(self.average(x))) for x in MktTypes]
        return 'Number of events: %d\n%s' % (self.cnt(), '\n'.join(val))


def to_talib_format(mdata):
    ''' Converts market daata to talib format '''
    res = {'date': np.array([datetime(x.year, x.month, x.day) for x in mdata.index])}
    for (idx, val) in enumerate(MktTypes):
        res[val] = np.array([float(x) for x in mdata[idx]])
    return res


@memoized
def get_mkt_data(symbol, from_date, to_date):
    return to_talib_format(access.get_marketdata(symbol, from_date, to_date, [access.Column.Open, access.Column.High, access.Column.Low, access.Column.Close]))


CONSIDERED_NDAYS = 10


def find_candlestick_patterns(cfunc, mdata):
    res = talib_call(cfunc, mdata['open'], mdata['high'], mdata['low'], mdata['close'])
    return ((idx, val) for idx, val in enumerate(res) if val != 0)


class CandlestickEvents(object):
    ''' '''
    def __init__(self, symbols):
        self.__symbols = symbols

    def __get_events(self):
        pass
    events = property(__get_events, None)

    def __gex_xxx(sefl):
        pass


def main(fname, from_date, to_date):
    # TODO: perhaps marketdata could be rewritten with use of MongoDb
    symbols = load_symbols(fname)
    #symbols = ['BG.L']  # TEMP
    if not check_db():
        init_db(symbols, from_date, to_date)

    avgs = {}
    palg = talib_candlestick_funcs()
    #palg = ['CDLTHRUSTING']  # TEMP

    for a in palg:
        for s in symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            res = find_candlestick_patterns(a, mdata)

            #xxx
            for (idx, val) in res:
                open = mdata['open'][idx + 1] if idx + 1 < len(mdata['open']) else 0
                for m in MktTypes:
                    key = '%s:%d' % (a, val)
                    if key not in avgs:
                        avgs[key] = AverageChange(CONSIDERED_NDAYS)
                    avgs[key].add(m, open, mdata[m][idx + 1:idx + 1 + min(CONSIDERED_NDAYS, len(mdata['open']) - (idx+1))])

    for k in avgs.keys():
        print(k)
        print(repr(avgs[k]))
    # TODO: dates processing could be done using map-reduce, i.e. coungint average values
    # Show graph for all cases average case


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
