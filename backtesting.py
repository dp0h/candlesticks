#!/usr/bin/env python
# coding:utf-8
'''
'''
from __future__ import print_function

from datetime import datetime
from helpers import load_symbols


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    if not check_db():
        init_db(symbols, from_date, to_date)

if __name__ == '__main__':
    from_date = datetime(2012, 1, 1)
    to_date = datetime(2012, 12, 31)
    main('idx_ftse100.txt', from_date, to_date)
