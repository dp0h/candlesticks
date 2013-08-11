# coding:utf-8
'''
Marketdata helpers
'''

from marketdata import update, access
from marketdata.symbols import Symbols


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


def get_marketdata(symbol, from_date, to_date):
    return access.get_marketdata(symbol, from_date, to_date)
