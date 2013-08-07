# coding:utf-8
'''
Helper functions
'''

import functools
import talib
import numpy
import pylab as pl
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick


def memoized(func):
    '''Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.'''
    cache = {}

    @functools.wraps(func)
    def memoizer(*args, **kwargs):
        keywords = tuple(sorted(kwargs.iteritems()))
        key = (args, keywords)
        try:
            return cache[key]
        except KeyError:
            value = func(*args, **kwargs)
            cache[key] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return func(*args, **kwargs)

    memoizer.cache = cache
    return memoizer


def talib_candlestick_funcs():
    return [x for x in talib.get_functions() if 'CDL' in x]


def talib_call(func, open, high, low, close):
    f = getattr(talib, func)
    return f(open, high, low, close)


def load_symbols(fname):
    return numpy.loadtxt(fname, dtype='S10', comments='#', skiprows=0)


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
