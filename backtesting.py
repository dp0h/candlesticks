#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
from helpers import load_symbols, check_db, init_db, get_mkt_data


class StrategyRunner(object):
    def __init__(self, pattern_alg, alg_value, side, hold_days, limit):
        self._pattern_alg = pattern_alg
        self._alg_value = alg_value
        self._side = side
        self._hold_days = hold_days
        self._limit = limit

        self._balance = 0

    def __call__(self, symbols, from_date, to_date):
        for s in self.__symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            for a in self.__palg:
                res = find_candlestick_patterns(a, mdata)
                pass
                #self._process_patterns(res, mdata, a)
        return self


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    if not check_db():
        init_db(symbols, from_date, to_date)

    strategy_inputs = [
        ('CDL3LINESTRIKE', -100, 'buy', 10, 1.5),
        ('CDLMORNINGDOJISTAR', 100, 'buy', 7, 1.0)]

    for x in strategy_inputs:
        sr = StrategyRunner(*x)(symbols, from_date, to_date)
        break

if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
