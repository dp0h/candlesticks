#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
from mktdata import init_marketdata, get_mkt_data
from helpers import load_symbols, find_candlestick_patterns


class MarketRules(object):
    pass


class StrategyRunner(object):
    def __init__(self, pattern_alg, alg_value, hold_days):
        self._pattern_alg = pattern_alg
        self._alg_value = alg_value
        #TODO: implemete buy/sell
        #self._side = side
        self._hold_days = hold_days
        #TODO: implemente limit transactions
        #self._limit = limit
        #TODO: closing should be based on bollinger bands (or sliding)

        self.balance = 0

    def _process_event(self, mdata_idx, mdata):
        #TODO: include transaction cost
        buy_price = mdata['open'][mdata_idx + 1]
        sell_price = mdata['open'][mdata_idx + 1 + self._hold_days]

        #TMP assume we buy each time for 1000 (and 5 is txn cost)
        self.balance -= 1005
        cnt = 1000 / buy_price
        profit = cnt * sell_price
        self.balance += profit
        if buy_price > 1000:
            print('!')

    def __call__(self, symbols, from_date, to_date):
        for s in symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            res = find_candlestick_patterns(self._pattern_alg, mdata)
            for (idx, val) in res:
                if val == self._alg_value:
                    try:
                        self._process_event(idx, mdata)
                    except IndexError:
                        pass
        return self


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    strategy_inputs = [
        ('CDL3LINESTRIKE', -100, 9),
        ('CDLMORNINGDOJISTAR', 100, 5),
        ('CDL3LINESTRIKE', 100, 9),
        ('CDLGAPSIDESIDEWHITE', -100, 9),
        ('CDL3WHITESOLDIERS', 100, 8),
        ('CDLINNECK', -100, 8)]

    for x in strategy_inputs:
        sr = StrategyRunner(*x)(symbols, from_date, to_date)
        print(sr.balance)

if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
