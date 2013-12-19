import argparse
import redis
import pandas
import numpy
import sys
from matplotlib import pyplot
from pandas.tools.plotting import bootstrap_plot

def stack():
    '''s is a custom python interactive debugger'''
    try:
        from IPython.core.debugger import Pdb, BdbQuit_excepthook
    except ImportError as ex:
        print ex
        return

    BdbQuit_excepthook.excepthook_ori = sys.excepthook
    Pdb().set_trace(sys._getframe().f_back)

class TimeSeries(object):
    def __init__(self, data, name):
        self.name = name

        if isinstance(data, list):
            self.data = numpy.array([float(x) for x in data])
        else:
            self.data = data

        self.s = pandas.Series(self.data)

    def summary(self):
        print '{}\n{}'.format(self.name, len(self.name)*'-')
        print self.s.describe()

    def plot(self):
        #fig = bootstrap_plot(self.s, color='grey')
        fig = pyplot.figure()
        #s = self.s.plot(figsize=(6, 6), style='k--') #kind='kde')
        self.s.hist(color='k', alpha=0.3, bins=50)
        #pyplot.scatter(df.col1, df.col2)
        #pyplot.legend()
        fig.savefig('data/'+self.name +'.png')

    def __add__(self, other):
        data = numpy.concatenate((self.data, other.data))
        return TimeSeries(data, self.name + " + " + other.name)

class Timings(object):
    def __init__(self, redis_uri, redis_prefix):
        redis_host, redis_port = redis_uri.split(':')
        self.prefix = redis_prefix + 'timing'
        self.redis = redis.StrictRedis(host=redis_host, port=int(redis_port))

    def series(self, name):
        series = []

        for key in self._fetch_series_keys(name):
            s = self._fetch_series(key)
            series.append(s)

        return series

    def series_date(self, name, date):
        pass

    def _fetch_series_keys(self, name):
        key = self.prefix + ':' + name + ':*'
        return self.redis.keys(key)

    def _fetch_series(self, key):
        data = self.redis.lrange(key, 0, -1)
        return TimeSeries(data, key)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Timings.')
    parser.add_argument('redis_uri', type=str, help='redis uri')
    parser.add_argument('redis_prefix', type=str, help='redis prefix')
    args = parser.parse_args()

    t = Timings(args.redis_uri, args.redis_prefix)

    for name in ('game_liked', 'game_playing_now', 'game_all', 'game_popular', 'game_popular_now'):
        series = t.series(name)
        s = reduce(lambda x, y: x+y, series)
        s.summary()
        s.plot()
