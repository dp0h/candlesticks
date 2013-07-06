#!/usr/bin/env python
# coding: utf-8

import unittest
from test import test_support
from main import AverageMove, find_candlestick_patterns
import numpy as np


class TestAverageMove(unittest.TestCase):
    def test_add_with_one_idx(self):
        o = AverageMove(1)
        o.add('open', 0, 1, 1)
        o.add('open', 0, 1, 2)
        self.assertAlmostEquals(1.5, o.average('open')[0])

    def test_add_with_three_idx(self):
        o = AverageMove(3)
        o.add('open', 0, 2, 1)
        o.add('open', 0, 2, 2)
        o.add('open', 0, 2, 3)
        o.add('open', 1, 2, 4)
        o.add('open', 1, 2, 4)
        o.add('open', 2, 2, 10)

        self.assertEquals(3, len(o.average('open')))
        self.assertAlmostEquals(1, o.average('open')[0])
        self.assertAlmostEquals(2, o.average('open')[1])
        self.assertAlmostEquals(5, o.average('open')[2])

    def test_add_for_openclose(self):
        o = AverageMove(1)
        o.add('open', 0, 2, 1)
        o.add('close', 0, 1, 2)
        self.assertAlmostEquals(0.5, o.average('open')[0])
        self.assertAlmostEquals(2, o.average('close')[0])


class TestFindCandlestickPatterns(unittest.TestCase):
    def test_CDL3OUTSIDE_res(self):
        open = [1258.0, 1226.50, 1190.0, 1242.5, 1253.5, 1276.5, 1252.0]
        high = [1265.0, 1245.93, 1262.5, 1254.5, 1284.0, 1293.5, 1264.0]
        low = [1230.0, 1215.50, 1180.0, 1227.0, 1251.0, 1262.0, 1245.5]
        close = [1236.0, 1220.0, 1246.0, 1253.5, 1277.5, 1262.0, 1263.5]

        mdata = {'open': np.array(open), 'high': np.array(high), 'low': np.array(low), 'close': np.array(close)}
        res = find_candlestick_patterns('CDL3OUTSIDE', mdata)
        self.assertEquals([(3, 100)], list(res))

if __name__ == '__main__':
    test_support.run_unittest(TestAverageMove)
    test_support.run_unittest(TestFindCandlestickPatterns)
