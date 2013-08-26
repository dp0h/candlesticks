# coding:utf-8
'''
Marketdata helpers
'''

from functools32 import lru_cache
import numpy as np
from datetime import timedelta
from marketdata import update, access
from marketdata.symbols import Symbols


MktTypes = ['open', 'high', 'low', 'close']
_AllFiels = ['date', 'adj_close'] + MktTypes


def _check_db(symbols, from_date, to_date):
    ''' Checks in very naive way if marketdata db is created and populated with data '''
    try:
        l = list(Symbols().symbols())
        if len(l) < len(symbols):
            return False
        if len(_get_marketdata(symbols[0], from_date, from_date + timedelta(days=10))) == 0:  # check if we have market data for first equity
            return False
        if len(_get_marketdata(symbols[-1], to_date - timedelta(days=10), to_date)) == 0:  # check if we have market data for the last equity
            return False
        return True
    except:
        return False


def _init_db(symbols, from_date, to_date):
    ''' Initializes marketdata db '''
    print('Fetching marketdata')
    Symbols().clean()
    Symbols().add(symbols)
    update.update_marketdata(from_date, to_date)


def init_marketdata(symbols, from_date, to_date):
    if not _check_db(symbols, from_date, to_date):
        _init_db(symbols, from_date, to_date)


def _get_marketdata(symbol, from_date, to_date):
    return access.get_marketdata(symbol, from_date, to_date)


def _to_talib_format(mdata):
    ''' Converts market data to talib format '''
    if len(mdata) == 0:
        return None
    res = {}
    for x in _AllFiels:
        res[x] = np.array([])
    for md in mdata:
        for x in _AllFiels:
            res[x] = np.append(res[x], md[x])
    return res


@lru_cache(maxsize=32)
def get_mkt_data(symbol, from_date, to_date):
    return _to_talib_format(_get_marketdata(symbol, from_date, to_date))


def approx_equal(a, b, tol):
    return abs(a - b) < tol


def percent_equal(a, b, comp, tol):
    return (abs(a - b) / comp) * 100 < tol


def has_split_dividents(mdata, from_date, to_date):
    ''' Verifies if market data interval has splits, dividends '''
    from_diff = abs(mdata['close'][from_date] - mdata['adj_close'][from_date])
    to_diff = abs(mdata['close'][to_date] - mdata['adj_close'][to_date])
    if approx_equal(from_diff, to_diff, 0.0001):
        return False
    return not percent_equal(from_diff, to_diff, mdata['close'][to_date], 0.8)
