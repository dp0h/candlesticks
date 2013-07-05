#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
import numpy as np
from marketdata import symbol, schema, update, access
import talib
import functools


def memoized(func):
    '''Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.'''
    cache = {}

    @functools.wraps(func)
    def memoizer(*args, **kwargs):
        keywords = tuple(sorted(kwargs.iteritems()))
        key = (args, keywords)
        try:
            return cache[key]
        except KeyError:
            value = func(*args, **kwargs)
            cache[key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return func(*args, **kwargs)

    memoizer.cache = cache
    return memoizer


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


class AverageMove(object):
    ''' Class for calculating normalized average values '''
    def __init__(self, size):
        self.__dict = {}
        for x in MktTypes:
            self.__dict[x] = [(0, 0)] * size

    def add(self, type, idx, relative_val, val):
        self.__dict[type][idx] = (self.__dict[type][idx][0] + float(val)/relative_val, self.__dict[type][idx][1] + 1)

    def average(self, type):
        return [acc/cnt for (acc, cnt) in self.__dict[type]]


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


def main(fname, from_date, to_date):
    # TODO: perhaps marketdata could be rewritten with use of MongoDb
    #symbols = np.loadtxt(fname, dtype='S10', comments='#', skiprows=0)
    symbols = ['BG.L']  # TEMP
    if not check_db():
        init_db(symbols, from_date, to_date)

    avgs = {}
    #palg = [x for x in talib.get_functions() if 'CDL' in x]
    palg = ['CDLTHRUSTING']  # TEMP
    for a in palg:
        for s in symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            f = getattr(talib, a)
            res = f(mdata['open'], mdata['high'], mdata['low'], mdata['close'])
            for (idx, val) in ((idx, val) for idx, val in enumerate(res) if val != 0):
                open = mdata['open'][idx]
                for i in range(CONSIDERED_NDAYS):
                    for m in MktTypes:
                        key = '%s:%d' % (a, val)
                        if key not in avgs:
                            avgs[key] = AverageMove(CONSIDERED_NDAYS)
                        try:
                            avgs[key].add(m, i, open, mdata[m][idx + i])
                        except IndexError:
                            pass

    for k in avgs.keys():
        print(key)
        for x in MktTypes:
            print(avgs[k].average(x))
    # TODO: dates processing could be done using map-reduce, i.e. coungint average values
    # Show graph for all cases average case


if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
