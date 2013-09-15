#!/usr/bin/env python
# coding: utf-8

import unittest
from test import test_support
import numpy as np
from datetime import datetime
from events import AverageChange, CandlestickPatternEvents
from mktdata import init_marketdata, has_split_dividents, odd_data
from helpers import talib_candlestick_funcs, find_candlestick_patterns
from backtesting import StrategyRunner


class TestAverageChange(unittest.TestCase):
    def test_add_item_with_one_idx(self):
        o = AverageChange(1)
        o.add_item('open', 0, 1, 1)
        o.add_item('open', 0, 1, 2)
        self.assertAlmostEquals(1.5, o.average('open')[0])

    def test_add_item_with_three_idx(self):
        o = AverageChange(3)
        o.add_item('open', 0, 2, 1)
        o.add_item('open', 0, 2, 2)
        o.add_item('open', 0, 2, 3)
        o.add_item('open', 1, 2, 4)
        o.add_item('open', 1, 2, 4)
        o.add_item('open', 2, 2, 10)

        self.assertEquals(3, len(o.average('open')))
        self.assertAlmostEquals(1, o.average('open')[0])
        self.assertAlmostEquals(2, o.average('open')[1])
        self.assertAlmostEquals(5, o.average('open')[2])

    def test_add_item_for_openclose(self):
        o = AverageChange(1)
        o.add_item('open', 0, 2, 1)
        o.add_item('close', 0, 1, 2)
        self.assertAlmostEquals(0.5, o.average('open')[0])
        self.assertAlmostEquals(2, o.average('close')[0])

    def test_add_with_three_idx(self):
        o = AverageChange(3)
        o.add('open', 2, [1, 4, 10])
        o.add('open', 2, [2, 4])
        o.add('open', 2, [3])

        self.assertEquals(3, len(o.average('open')))
        self.assertAlmostEquals(1, o.average('open')[0])
        self.assertAlmostEquals(2, o.average('open')[1])
        self.assertAlmostEquals(5, o.average('open')[2])


class TestFindCandlestickPatterns(unittest.TestCase):
    def test_CDL3OUTSIDE_res(self):
        open = [1258.0, 1226.50, 1190.0, 1242.5, 1253.5, 1276.5, 1252.0]
        high = [1265.0, 1245.93, 1262.5, 1254.5, 1284.0, 1293.5, 1264.0]
        low = [1230.0, 1215.50, 1180.0, 1227.0, 1251.0, 1262.0, 1245.5]
        close = [1236.0, 1220.0, 1246.0, 1253.5, 1277.5, 1262.0, 1263.5]

        mdata = {'open': np.array(open), 'high': np.array(high), 'low': np.array(low), 'close': np.array(close)}
        res = find_candlestick_patterns('CDL3OUTSIDE', mdata)
        self.assertEquals([(3, 100)], list(res))


class EventsRegressionTest(unittest.TestCase):
    def test_CandlestickPatternEvents(self):
        from_date = datetime(2012, 1, 1)
        to_date = datetime(2012, 1, 31)
        symbols = ['ABF.L', 'ADM.L']
        init_marketdata(symbols, from_date, to_date)

        palg = talib_candlestick_funcs()

        c = CandlestickPatternEvents(symbols, palg, from_date, to_date)()
        changes = list(c.average_changes)
        self.assertEquals(17, len(changes))
        self.assertEquals('CDLSPINNINGTOP:100', changes[16][0])
        self.assertEquals(3, changes[16][1].cnt())
        self.assertAlmostEquals(1.02994350282, changes[16][1].average('open')[-1])


class TestMarketDataModule(unittest.TestCase):
    def test_has_split_dividents(self):
        self.assertFalse(has_split_dividents({'close': [1, 2, 3], 'adj_close': [1, 2, 3]}, 0, 2))
        self.assertFalse(has_split_dividents({'close': [1, 3], 'adj_close': [2, 4]}, 0, 1))
        self.assertTrue(has_split_dividents({'close': [1, 3], 'adj_close': [2, 8]}, 0, 1))
        self.assertTrue(has_split_dividents({'close': [1.0, 1.0], 'adj_close': [1.0, 1.2]}, 0, 1))
        self.assertFalse(has_split_dividents({'close': [100.0, 100.0], 'adj_close': [100.0, 100.4]}, 0, 1))

    def test_odd_data(self):
        self.assertFalse(odd_data(100, 100))
        self.assertFalse(odd_data(100, 200))
        self.assertTrue(odd_data(100, 201))


class StrategyRunnerRegressionTest(unittest.TestCase):
    def test_long_strategy(self):
        from_date = datetime(2012, 1, 1)
        to_date = datetime(2012, 1, 31)
        symbols = ['BRBY.L', 'CNA.L', 'MGGT.L']
        init_marketdata(symbols, from_date, to_date)

        sr = StrategyRunner('CDL3LINESTRIKE', -100, 9, 1, 0.02)(symbols, from_date, to_date)
        self.assertAlmostEqual(-353.443, sr.balance, 2)

    def test_short_strategy(self):
        from_date = datetime(2012, 1, 1)
        to_date = datetime(2012, 12, 31)
        symbols = ['AZN.L', 'FRES.L', 'IAG.L']
        init_marketdata(symbols, from_date, to_date)

        sr = StrategyRunner('CDL3WHITESOLDIERS', 100, 3, 0, 0.02)(symbols, from_date, to_date)
        self.assertAlmostEqual(295.808, sr.balance, 2)


class TestStrategyRunner(unittest.TestCase):
    def test_process_long_position(self):
        s = StrategyRunner('', [], 0, True, 0.02, txn_amount=100)

        self.assertAlmostEqual(9.65, s._process_long_position(100, 110, 98))
        self.assertAlmostEqual(-2.349, s._process_long_position(100, 110, 97), 2)

    def test_process_short_position(self):
        s = StrategyRunner('', [], 0, False, 0.02, txn_amount=100)

        self.assertAlmostEqual(9.65, s._process_short_position(100, 90, 102))
        self.assertAlmostEqual(-2.349, s._process_short_position(100, 90, 103), 2)


if __name__ == '__main__':
    test_support.run_unittest(TestAverageChange)
    test_support.run_unittest(TestFindCandlestickPatterns)
    test_support.run_unittest(EventsRegressionTest)
    test_support.run_unittest(TestMarketDataModule)
    test_support.run_unittest(StrategyRunnerRegressionTest)
    test_support.run_unittest(TestStrategyRunner)
