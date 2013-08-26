#!/usr/bin/env python
# coding:utf-8
'''
Candlestick events analyzer
'''
import os
import argparse
from helpers import talib_candlestick_funcs, load_symbols, save_candlestick_chart, find_candlestick_patterns, create_result_dir, mkdate
from mktdata import MktTypes, init_marketdata, get_mkt_data, has_split_dividents


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
            try:
                mdata_len = len(mdata['open'])
                open_idx = min(idx + 1, mdata_len - 1)
                close_idx = min(idx + 1 + CONSIDERED_NDAYS, mdata_len - 1)

                if close_idx - open_idx < CONSIDERED_NDAYS / 2:
                    continue  # skip events if we don't have enough days

                if has_split_dividents(mdata, max(open_idx - 5, 0), close_idx):
                    continue  # skip events if split/dividents happens

                #TODO: output detail values for each event to file, plus index for comparison
                next_day_open = mdata['open'][open_idx]
                for m in MktTypes:
                    key = '%s:%d' % (alg, val)
                    if key not in self._avgs:
                        self._avgs[key] = AverageChange(CONSIDERED_NDAYS)
                    self._avgs[key].add(m, next_day_open, mdata[m][open_idx:close_idx])
            except:
                pass

    def __call__(self):
        for s in self._symbols:
            mdata = get_mkt_data(s, self._from_date, self._to_date)
            if mdata:
                for a in self._palg:
                    res = find_candlestick_patterns(a, mdata)
                    self._process_patterns(res, mdata, a)
        return self


def output_results(average_changes, diff_level, min_cnt, params):
    outpath = create_result_dir('events')

    with open(os.path.join(outpath, 'params.txt'), 'w') as f:
        f.write('File: %s\nFrom: %s\nTo: %s' % (params[0], params[1], params[2]))

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


def events_main(fname, from_date, to_date):
    symbols = load_symbols(fname)
    init_marketdata(symbols, from_date, to_date)

    palg = talib_candlestick_funcs()

    c = CandlestickPatternEvents(symbols, palg, from_date, to_date)()

    diff_level = 0.02  # output patterns where up/down > diff_level
    min_cnt = 5  # output patterns with > min_cnt events

    output_results(c.average_changes, diff_level, min_cnt, [fname, from_date, to_date])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Candlestick events analyzer')
    parser.add_argument('-f', '--fromdate', metavar='YYYYMMDD', type=mkdate, required=True, help='from date in format YYYYMMDD')
    parser.add_argument('-t', '--todate', metavar='YYYYMMDD', type=mkdate, required=True, help='from date in format YYYYMMDD')
    parser.add_argument('-s', '--shares', metavar='FILENAME', type=str, required=True, help='file with list of shares')

    args = parser.parse_args()
    events_main(args.shares, args.fromdate, args.todate)
