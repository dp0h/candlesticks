#!/usr/bin/env python
# coding:utf-8
'''
Candlestick strategy backtest functionality
'''
from __future__ import print_function
import sys
import getopt
from datetime import datetime
from mktdata import init_marketdata, get_mkt_data, has_split_dividents
from helpers import load_symbols, find_candlestick_patterns


class StrategyRunner(object):
    def __init__(self, pattern_alg, alg_value, hold_days, buy_side, limit, commision=0.0035, txn_amount=10000):
        self._pattern_alg = pattern_alg
        self._alg_value = alg_value
        self._buy_side = buy_side
        self._hold_days = hold_days
        self._limit = limit
        self._commision = commision
        self._txn_amount = txn_amount
        #TODO: closing should be based on bollinger bands or sliding. Also we can close position when price reached some level (e.g. 10% grow).

        self.balance = 0
        self.txns = []  # txns format (symbol, buy_date, sell_date, buy_price, sell_price, profit)

    def _process_position(self, symbol, mdata_idx, mdata):
        '''
        mdata_idx - position in market data when event happens
        '''
        mdata_len = len(mdata['open'])
        open_idx = min(mdata_idx + 1, mdata_len - 1)  # we can buy at day idx+1
        close_idx = min(mdata_idx + 1 + self._hold_days, mdata_len - 1)

        if close_idx - open_idx < self._hold_days / 2:
            return  # skip events if we don't have enough days

        if has_split_dividents(mdata, max(open_idx - 5, 0), close_idx):
            return  # skip events if split/dividents happens

        open_position = mdata['open'][open_idx]
        close_position = mdata['open'][close_idx]
        limit_level = min(mdata['low'][open_idx:close_idx]) if self._buy_side else max(mdata['high'][open_idx:close_idx])

        profit = self._process_long_position(open_position, close_position, limit_level) if self._buy_side else self._process_short_position(open_position, close_position, limit_level)

        self.txns.append((symbol, mdata['date'][open_idx], mdata['date'][close_idx], open_position, close_position, profit))
        self.balance += profit

    def _process_long_position(self, open_position, close_position, limit_level):
        cnt = int(self._txn_amount / open_position)
        open_amount = cnt * (open_position + open_position * self._commision)
        close_amount = cnt * close_position

        if limit_level < open_position - open_position * self._limit:  # check if price moves below threshold
            close_amount = cnt * (open_position - open_position * self._limit)

        return close_amount - open_amount

    def _process_short_position(self, open_position, close_position, limit_level):
        cnt = int(self._txn_amount / open_position)
        open_amount = cnt * (open_position - open_position * self._commision)
        close_amount = cnt * close_position

        if limit_level > open_position + open_position * self._limit:  # check if price moves below threshold
            close_amount = cnt * (open_position + open_position * self._limit)

        return open_amount - close_amount

    def __call__(self, symbols, from_date, to_date):
        for s in symbols:
            mdata = get_mkt_data(s, from_date, to_date)
            if mdata:
                res = find_candlestick_patterns(self._pattern_alg, mdata)
                for (idx, val) in res:
                    if val == self._alg_value:
                        self._process_position(s, idx, mdata)
        return self


def load_strategies(fname):
    with open(fname) as f:
        lines = f.readlines()
    res = []
    for x in lines:
        items = x.split(',')
        res.append((items[0], int(items[1]), int(items[2]), int(items[3]), float(items[4])))
    return res


def main(fname, from_date, to_date, strategies):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    strategies_cfg = load_strategies(strategies)

    #TODO: try to run with different limits

    for x in strategies_cfg:
        sr = StrategyRunner(*x)(symbols, from_date, to_date)
        print('%s %d: %f' % (x[0], x[1], sr.balance))
        #print(sr.txns)
        #TODO: need to combine these balances in one to see changes during period
        #TODO: get Sharpe ration for this profits


def usage(err):
    print('Error: %s\nUsage: %s -from YYYYMMDD -to YYYYMMDD -shares shares_file stategies_file' % (err, sys.argv[0]), file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    '''
        -from YYYYMMDD - from date
        -to YYYYMMDD - to date
        -shares shares_file - file with list of shares
        stategies_file - file with traiding strategies configurations
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:s:", ["from=", "to=", 'shares='])
    except getopt.GetoptError as err:
        usage(str(err))
    from_date = None
    to_date = None
    shares_file = None
    for o, a in opts:
        if o == '-f':
            from_date = a
        elif o == '-t':
            to_date = a
        elif o == '-s':
            shares_file = a
        else:
            usage('Unhandled option')
    if len(args) != 1:
        usage('Too many parameters.' if len(args) > 2 else 'Strategy file is not provided.')
    try:
        from_date = datetime(int(from_date[:4]), int(from_date[4:6]), int(from_date[6:]))
        to_date = datetime(int(to_date[:4]), int(to_date[4:6]), int(to_date[6:]))
    except:
        usage('Invalid date format.')

    main(shares_file, from_date, to_date, args[0])
