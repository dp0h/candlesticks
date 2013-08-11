# coding:utf-8
'''
Marketdata helpers
'''

from functools32 import lru_cache
import numpy as np
from marketdata import update, access
from marketdata.symbols import Symbols

MktTypes = ['open', 'high', 'low', 'close']


def _check_db():
    ''' Checks if marketdata db is created '''
    try:
        l = list(Symbols().symbols())
        if len(l) > 0:
            return True
        #TODO: check if values are in DB
    except:
        pass


def _init_db(symbols, from_date, to_date):
    ''' Initializes marketdata db '''
    print('Fetching marketdata')
    Symbols().clean()
    Symbols().add(symbols)
    update.update_marketdata(from_date, to_date)


def init_marketdata(symbols, from_date, to_date):
    if not _check_db():
        _init_db(symbols, from_date, to_date)


def _get_marketdata(symbol, from_date, to_date):
    return access.get_marketdata(symbol, from_date, to_date)


def _to_talib_format(mdata):
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
    return _to_talib_format(_get_marketdata(symbol, from_date, to_date))
