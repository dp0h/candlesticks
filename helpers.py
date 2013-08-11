# coding:utf-8
'''
Helper functions
'''

import talib
import numpy as np
import pylab as pl
from functools32 import lru_cache
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick
from marketdata import update, access
from marketdata.symbols import Symbols


def talib_candlestick_funcs():
    ''' Retrieves candlestick function names '''
    return [x for x in talib.get_functions() if 'CDL' in x]


def talib_call(func, open, high, low, close):
    f = getattr(talib, func)
    return f(open, high, low, close)


def load_symbols(fname):
    return np.loadtxt(fname, dtype='S10', comments='#', skiprows=0)


MktTypes = ['open', 'high', 'low', 'close']


def to_talib_format(mdata):
    ''' Converts market data to talib format '''
    res = {}
    for x in ['date'] + MktTypes:
        res[x] = np.array([])
    for md in mdata:
        for x in ['date'] + MktTypes:
            res[x] = np.append(res[x], md[x])
    return res


#TODO: need market data validation to exclude splits/dividents/corrupted data
@lru_cache(maxsize=32)
def get_mkt_data(symbol, from_date, to_date):
    return to_talib_format(access.get_marketdata(symbol, from_date, to_date))


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


def check_db():
    ''' Checks if marketdata db is created '''
    try:
        l = list(Symbols().symbols())
        if len(l) > 0:
            return True
    except:
        pass


def init_db(symbols, from_date, to_date):
    ''' Initializes marketdata db '''
    print('Fetching marketdata')
    Symbols().add(symbols)
    update.update_marketdata(from_date, to_date)
