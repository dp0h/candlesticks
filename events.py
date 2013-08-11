#!/usr/bin/env python
# coding:utf-8
'''
Candlestick events analyzer
'''
from __future__ import print_function

from datetime import datetime
import numpy as np
from functools32 import lru_cache
from marketdata import update, access
from marketdata.symbols import Symbols
from helpers import talib_candlestick_funcs, talib_call, load_symbols, show_candlestick


def check_db():
    ''' Checks if marketdata db is created '''
    try:
        l = list(Symbols().symbols())
        if len(l) > 0:
            return True
    except:
        pass


def init_db(symbols, from_date, to_date):
    ''' Initializes marketdata db '''
    print('Fetching marketdata')
    Symbols().add(symbols)
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
        return '<AverageChange. Number of events: %d\n%s>' % (self.cnt(), '\n'.join(val))


def to_talib_format(mdata):
    ''' Converts market data to talib format '''
    res = {}
    for x in ['date'] + MktTypes:
        res[x] = np.array([])
    for md in mdata:
        for x in ['date'] + MktTypes:
            res[x] = np.append(res[x], md[x])
    return res


#TODO: need market data validation to exclude splits/dividents/corrupted data
@lru_cache(maxsize=32)
def get_mkt_data(symbol, from_date, to_date):
    return to_talib_format(access.get_marketdata(symbol, from_date, to_date))


CONSIDERED_NDAYS = 10


def find_candlestick_patterns(cfunc, mdata):
    res = talib_call(cfunc, mdata['open'], mdata['high'], mdata['low'], mdata['close'])
    return ((idx, val) for idx, val in enumerate(res) if val != 0)


class CandlestickPatternEvents(object):
    ''' Class for finding candlestick pattern events and counting average changes. '''
    def __init__(self, symbols, candlestick_funcitons):
        self.__symbols = symbols
        self.__avgs = {}
        self.__palg = candlestick_funcitons

    def __get_average_changes(self):
        for k in self.__avgs.keys():
            yield (k, self.__avgs[k])
    average_changes = property(__get_average_changes)

    def _process_patterns(self, res, mdata, alg):
        for (idx, val) in res:
            next_day_open = mdata['open'][idx + 1] if idx + 1 < len(mdata['open']) else 0
            for m in MktTypes:
                key = '%s:%d' % (alg, val)
                if key not in self.__avgs:
                    self.__avgs[key] = AverageChange(CONSIDERED_NDAYS)
                self.__avgs[key].add(m, next_day_open, mdata[m][idx + 1:idx + 1 + min(CONSIDERED_NDAYS, len(mdata['open']) - (idx+1))])

    def __call__(self):
        for s in self.__symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            for a in self.__palg:
                res = find_candlestick_patterns(a, mdata)
                self._process_patterns(res, mdata, a)
        return self


def output_results(average_changes, diff_level, min_cnt):
    #TODO: output results and graphs to files/html

    i = 0
    for (k, val) in average_changes:
        mn = mx = 1.0
        for x in ['open', 'close']:
            v = val.average(x)
            mn = min(mn, min(v))
            mx = max(mx, max(v))
        if (mx > 1.0 + diff_level or mn < 1.0 - diff_level) and val.cnt() >= min_cnt:
            print(k)
            print(repr(val))
            i += 1
            val = [val.average(t) for t in [MktTypes[0], MktTypes[3], MktTypes[1], MktTypes[2]]]
            days = [[x for x in range(len(val[0]))]]  # put fake dates
            quotes = days + val
            quotes = zip(*quotes)
            show_candlestick(quotes)
    print('Total: %d' % i)


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    if not check_db():
        init_db(symbols, from_date, to_date)

    palg = talib_candlestick_funcs()

    c = CandlestickPatternEvents(symbols, palg)()

    diff_level = 0.02  # output patterns where up/down > diff_level
    min_cnt = 5  # output patterns with > min_cnt events

    output_results(c.average_changes, diff_level, min_cnt)


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
