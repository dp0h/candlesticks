#!/usr/bin/env python
# coding:utf-8
'''
Candlestick events analyzer
'''
from __future__ import print_function
import sys
import os
import getopt
from datetime import datetime
from helpers import talib_candlestick_funcs, load_symbols, save_candlestick_chart, find_candlestick_patterns
from mktdata import MktTypes, init_marketdata, get_mkt_data


class AverageChange(object):
    ''' Class for calculating normalized average values '''
    def __init__(self, size):
        self._dict = {}
        for x in MktTypes:
            self._dict[x] = [(0, 0)] * size

    def add_item(self, type, idx, relative_val, val):
        acc = self._dict[type][idx][0] + float(val)/relative_val
        cnt = self._dict[type][idx][1] + 1
        self._dict[type][idx] = (acc, cnt)

    def add(self, type, relative_val, vals):
        for idx, val in enumerate(vals):
            self.add_item(type, idx, relative_val, val)

    def average(self, type):
        return [acc/cnt for (acc, cnt) in self._dict[type] if cnt > 0]

    def cnt(self):
        return self._dict['open'][0][1]

    def __repr__(self):
        val = ['%s: %s' % (x, str(self.average(x))) for x in MktTypes]
        return '<AverageChange. Number of events: %d\n%s>' % (self.cnt(), '\n'.join(val))


CONSIDERED_NDAYS = 10


class CandlestickPatternEvents(object):
    ''' Class for finding candlestick pattern events and counting average changes. '''
    def __init__(self, symbols, candlestick_funcitons, from_date, to_date):
        self._symbols = symbols
        self._avgs = {}
        self._palg = candlestick_funcitons
        self._from_date = from_date
        self._to_date = to_date

    def __get_average_changes(self):
        for k in self._avgs.keys():
            yield (k, self._avgs[k])
    average_changes = property(__get_average_changes)

    def _process_patterns(self, res, mdata, alg):
        for (idx, val) in res:
            #TODO: filter events if there split/divedents around
            #TODO: output detail values for each event to file, plus index for comparison
            next_day_open = mdata['open'][idx + 1] if idx + 1 < len(mdata['open']) else 0
            for m in MktTypes:
                key = '%s:%d' % (alg, val)
                if key not in self._avgs:
                    self._avgs[key] = AverageChange(CONSIDERED_NDAYS)
                self._avgs[key].add(m, next_day_open, mdata[m][idx + 1:idx + 1 + min(CONSIDERED_NDAYS, len(mdata['open']) - (idx+1))])

    def __call__(self):
        for s in self._symbols:
            mdata = get_mkt_data(s, self._from_date, self._to_date)
            for a in self._palg:
                res = find_candlestick_patterns(a, mdata)
                self._process_patterns(res, mdata, a)
        return self


def output_results(average_changes, diff_level, min_cnt):
    now = datetime.now()
    outpath = "./results-events-%d-%02d-%02d_%02d-%02d-%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    os.makedirs(outpath)

    with open(os.path.join(outpath, 'events.html'), 'w') as f:
        i = 0
        for (k, val) in average_changes:
            mn = mx = 1.0
            for x in ['open', 'close']:
                v = val.average(x)
                mn = min(mn, min(v))
                mx = max(mx, max(v))
            if (mx > 1.0 + diff_level or mn < 1.0 - diff_level) and val.cnt() >= min_cnt:
                f.write('<h3>%s</h3>' % k)
                f.write('<b>Number of events: %d</b><br/>' % val.cnt())
                f.write('</br><code>%s</code>' % repr(val).replace('<', '&lt;').replace('>', '&gt;'))
                i += 1
                val = [val.average(t) for t in [MktTypes[0], MktTypes[3], MktTypes[1], MktTypes[2]]]
                days = [[x for x in range(len(val[0]))]]  # put fake dates
                quotes = days + val
                quotes = zip(*quotes)
                img_name = '%s.png' % k
                save_candlestick_chart(os.path.join(outpath, img_name), quotes)
                f.write('<img src="./%s"/>' % img_name)
                f.write('<hr/>')
        f.write('<b>Total: %d</b>' % i)


def main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    palg = talib_candlestick_funcs()

    c = CandlestickPatternEvents(symbols, palg, from_date, to_date)()

    diff_level = 0.02  # output patterns where up/down > diff_level
    min_cnt = 5  # output patterns with > min_cnt events

    output_results(c.average_changes, diff_level, min_cnt)


def usage(err):
    print('Error: %s\nUsage: %s -from YYYYMMDD -to YYYYMMDD -shares shares_file' % (err, sys.argv[0]), file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    '''
        -from YYYYMMDD - from date
        -to YYYYMMDD - to date
        -shares shares_file - file with list of shares
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:t:s:", ["from=", "to=", 'shares='])
    except getopt.GetoptError as err:
        usage(str(err))
    from_date = None
    to_date = None
    shares_file = None
    for o, a in opts:
        if o == '-f':
            from_date = a
        elif o == '-t':
            to_date = a
        elif o == '-s':
            shares_file = a
        else:
            usage('Unhandled option')
    if len(args) != 0:
        usage('Too many parameters.')
    try:
        from_date = datetime(int(from_date[:4]), int(from_date[4:6]), int(from_date[6:]))
        to_date = datetime(int(to_date[:4]), int(to_date[4:6]), int(to_date[6:]))
    except:
        usage('Invalid date format.')

    main(shares_file, from_date, to_date)
