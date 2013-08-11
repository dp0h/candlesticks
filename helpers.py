# coding:utf-8
'''
Helper functions
'''

import talib
import numpy as np
import pylab as pl
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick


def talib_candlestick_funcs():
    ''' Retrieves candlestick function names '''
    return [x for x in talib.get_functions() if 'CDL' in x]


def talib_call(func, open, high, low, close):
    f = getattr(talib, func)
    return f(open, high, low, close)


def find_candlestick_patterns(cfunc, mdata):
    res = talib_call(cfunc, mdata['open'], mdata['high'], mdata['low'], mdata['close'])
    return ((idx, val) for idx, val in enumerate(res) if val != 0)


def load_symbols(fname):
    return np.loadtxt(fname, dtype='S10', comments='#', skiprows=0)


def show_candlestick(quotes):
    '''
    quotes should have the following format: [(date1, open1, close1, high1, low1), (date2, open2, ...), (...), ...]
    '''
    mondays = WeekdayLocator(MONDAY)
    alldays = DayLocator()
    weekFormatter = DateFormatter('%b %d')

    fig = pl.figure()
    fig.subplots_adjust(bottom=0.2)
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)

    candlestick(ax, quotes, width=0.6, colorup='g')
    ax.xaxis_date()
    ax.autoscale_view()
    pl.setp(pl.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    pl.show()
