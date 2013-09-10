# coding:utf-8
'''
Helper functions
'''

import os
import talib
import numpy as np
import pylab as pl
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick
from datetime import datetime


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


def save_candlestick_chart(fname, quotes):
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

    pl.savefig(fname)


def create_result_dir(name):
    now = datetime.now()
    outpath = "./results-%s-%d-%02d-%02d_%02d-%02d-%02d" % (name, now.year, now.month, now.day, now.hour, now.minute, now.second)
    os.makedirs(outpath)
    return outpath


def create_table(f, header, values, valueFormat):
    table_header(f, header)
    for x in values:
        table_row(f, x, valueFormat)
    table_close(f)


def table_header(f, header):
    f.write('<table border="1">')
    f.write('<tr>')
    for x in header:
        f.write('<th>%s</th>' % x)
    f.write('</tr>')


def table_row(f, value, valueFormat):
    f.write('<tr>')
    for i in range(0, len(valueFormat)):
        f.write(('<th>' + valueFormat[i] + ' </th>') % value[i])
    f.write('</tr>')


def table_close(f):
    f.write('</table>')


def mkdate(datestr):
    return datetime(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:]))
