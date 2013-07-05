#!/usr/bin/env python
# coding: utf-8

import unittest
from test import test_support
from main import AverageMove


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

if __name__ == '__main__':
    test_support.run_unittest(TestAverageMove)
