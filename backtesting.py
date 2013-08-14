#!/usr/bin/env python
# coding:utf-8
'''
Candlestick strategy backtest functionality
'''
from __future__ import print_function
import sys
import getopt
from datetime import datetime
from mktdata import init_marketdata, get_mkt_data
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

    def _process_long_position(self, mdata_idx, mdata):
        #TODO: check where no split/dividents in these period
        # this could be done just by comparind close and adj_close
        open_position = mdata['open'][mdata_idx + 1]
        close_position = mdata['open'][mdata_idx + 1 + self._hold_days]
        limit_level = min(mdata['low'][mdata_idx + 1:mdata_idx + 1 + self._hold_days])

        #TODO: output all transactions details
        cnt = int(self._txn_amount / open_position)
        open_amount = cnt * (open_position + open_position * self._commision)
        close_amount = cnt * close_position

        if limit_level < open_position - open_position * self._limit:  # check if price moves below threshold
            close_amount = cnt * (open_position - open_position * self._limit)

        profit = close_amount - open_amount
        self.balance += profit

    def _process_short_position(self, mdata_idx, mdata):
        open_position = mdata['open'][mdata_idx + 1]
        close_position = mdata['open'][mdata_idx + 1 + self._hold_days]
        limit_level = max(mdata['high'][mdata_idx + 1:mdata_idx + 1 + self._hold_days])

        cnt = int(self._txn_amount / open_position)
        open_amount = cnt * (open_position - open_position * self._commision)
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


def main(fname, from_date, to_date, strategies):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    #TODO: load from file
    strategy_inputs = [
        ('CDL3LINESTRIKE', -100, 9, 1, 0.02),
        ('CDLMORNINGDOJISTAR', 100, 6, 1, 0.02),
        ('CDL3LINESTRIKE', 100, 9, 1, 0.02),
        ('CDLGAPSIDESIDEWHITE', -100, 9, 1, 0.02),
        ('CDL3WHITESOLDIERS', 100, 3, 0, 0.02),
        ('CDLINNECK', -100, 9, 1, 0.02)]

    #TODO: try to run with different paramentes (holding days, limit)

    for x in strategy_inputs:
        sr = StrategyRunner(*x)(symbols, from_date, to_date)
        print(sr.balance)
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
