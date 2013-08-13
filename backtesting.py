#!/usr/bin/env python
# coding:utf-8
'''
Candlestick strategy backtest functionality
'''
from __future__ import print_function

from datetime import datetime
from mktdata import init_marketdata, get_mkt_data
from helpers import load_symbols, find_candlestick_patterns


class MarketRules(object):
    pass

BUY_COMMISION = 0.0035
TXN_AMOUNT = 10000


class StrategyRunner(object):
    def __init__(self, pattern_alg, alg_value, hold_days, buy_side, limit):
        self._pattern_alg = pattern_alg
        self._alg_value = alg_value
        self._buy_side = buy_side
        self._hold_days = hold_days
        self._limit = limit
        #TODO: closing should be based on bollinger bands or sliding. Also we can close position when price reached some level (e.g. 10% grow).

        self.balance = 0

    def _process_long_position(self, mdata_idx, mdata):
        #TODO: check where no split/dividents in these period
        open_position = mdata['open'][mdata_idx + 1]
        close_position = mdata['open'][mdata_idx + 1 + self._hold_days]

        limit_level = mdata['low'][mdata_idx + 1:mdata_idx + 1 + self._hold_days]
        limit_level = min(limit_level)

        #TODO: output all transactions details
        cnt = int(TXN_AMOUNT / open_position)
        open_amount = cnt * (open_position + open_position * BUY_COMMISION)
        close_amount = cnt * close_position

        if limit_level < open_position - open_position * self._limit:  # check if price moves below threshold
            close_amount = cnt * (open_position - open_position * self._limit)

        profit = close_amount - open_amount
        self.balance += profit

    def _process_short_position(self, mdata_idx, mdata):
        #TODO: merge with _process_long_position
        open_position = mdata['open'][mdata_idx + 1]
        close_position = mdata['open'][mdata_idx + 1 + self._hold_days]

        limit_level = mdata['high'][mdata_idx + 1:mdata_idx + 1 + self._hold_days]
        limit_level = max(limit_level)

        cnt = int(TXN_AMOUNT / open_position)
        open_amount = cnt * (open_position + open_position * BUY_COMMISION)
        close_amount = cnt * close_position

        if limit_level > open_position + open_position * self._limit:  # check if price moves below threshold
            close_amount = cnt * (open_position + open_position * self._limit)

        profit = open_amount - close_amount
        self.balance += profit

    def __call__(self, symbols, from_date, to_date):
        for s in symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            res = find_candlestick_patterns(self._pattern_alg, mdata)
            for (idx, val) in res:
                if val == self._alg_value:
                    try:
                        if self._buy_side:
                            self._process_long_position(idx, mdata)
                        else:
                            self._process_short_position(idx, mdata)
                    except IndexError:  # TODO: eliminate out of bound exception
                        pass
        return self


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    strategy_inputs = [
        ('CDL3LINESTRIKE', -100, 9, 1, 0.02),
        ('CDLMORNINGDOJISTAR', 100, 6, 1, 0.02),
        ('CDL3LINESTRIKE', 100, 9, 1, 0.02),
        ('CDLGAPSIDESIDEWHITE', -100, 9, 1, 0.02),
        ('CDL3WHITESOLDIERS', 100, 3, 0, 0.02),
        ('CDLINNECK', -100, 9, 1, 0.02)]

    for x in strategy_inputs:
        sr = StrategyRunner(*x)(symbols, from_date, to_date)
        print(sr.balance)

if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
