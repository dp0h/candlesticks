#!/usr/bin/env python
# coding:utf-8
'''
Candlestick strategy backtest functionality
'''
import os
import argparse
from mktdata import init_marketdata, get_mkt_data, has_split_dividents
from helpers import load_symbols, find_candlestick_patterns, create_result_dir, create_table, mkdate
from multiprocessing import Pool


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


def output_transactions(outpath, sparams, txns):
    with open(os.path.join(outpath, 'txns_%s_%d_%d_%d_%d.html' % (sparams[0], sparams[1], sparams[2], sparams[3], sparams[4])), 'w') as f:
        create_table(f, ['Symbol', 'Buy date', 'Sell date', 'Buy price', 'Sell prive', 'Profit'], txns, ['%s', '%s', '%s', '%f', '%f', '%f'])


def strategy_runner((outpath, symbols, from_date, to_date, strategy)):
    sr = StrategyRunner(*strategy)(symbols, from_date, to_date)
    output_transactions(outpath, (strategy[0], strategy[1], strategy[2], strategy[3], strategy[4]), sr.txns)
    return (strategy[0], strategy[1], strategy[2], strategy[3], strategy[4], sr.balance)


def backtesting_main(fname, from_date, to_date, strategies, async=False):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)
    strategies_cfg = load_strategies(strategies)
    outpath = create_result_dir('backtesting')

    pool = Pool(4)
    res = pool.map(strategy_runner, [(outpath, symbols, from_date, to_date, x) for x in strategies_cfg])

    with open(os.path.join(outpath, 'backtesting.html'), 'w') as f:
        create_table(f, ['Pattern', 'Pattern params', 'Hold days', 'Buy side', 'Limit', 'Profit'], res, ['%s', '%d', '%d', '%d', '%f', '%f'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Candlestick strategy backtesting')
    parser.add_argument('-f', '--fromdate', metavar='YYYYMMDD', type=mkdate, required=True, help='from date in format YYYYMMDD')
    parser.add_argument('-t', '--todate', metavar='YYYYMMDD', type=mkdate, required=True, help='from date in format YYYYMMDD')
    parser.add_argument('-s', '--shares', metavar='FILENAME', type=str, required=True, help='file with list of shares')
    parser.add_argument('strategies', metavar='STRATEGIES_FILE', type=str, nargs=1, help='')

    args = parser.parse_args()
    backtesting_main(args.shares, args.fromdate, args.todate, args.strategies[0])
