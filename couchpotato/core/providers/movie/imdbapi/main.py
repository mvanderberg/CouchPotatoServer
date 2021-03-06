from couchpotato.core.event import addEvent, fireEvent
from couchpotato.core.helpers.variable import tryInt, tryFloat
from couchpotato.core.logger import CPLog
from couchpotato.core.providers.movie.base import MovieProvider
from urllib import urlencode
import json
import re
import traceback

log = CPLog(__name__)


class IMDBAPI(MovieProvider):

    urls = {
        'search': 'http://www.imdbapi.com/?%s',
        'info': 'http://www.imdbapi.com/?i=%s&tomatoes=true',
    }

    http_time_between_calls = 0

    def __init__(self):
        addEvent('movie.search', self.search)
        addEvent('movie.info', self.getInfo)

    def search(self, q, limit = 12):

        name_year = fireEvent('scanner.name_year', q, single = True)

        cache_key = 'imdbapi.cache.%s' % q
        cached = self.getCache(cache_key, self.urls['search'] % urlencode({'t': name_year.get('name'), 'y': name_year.get('year')}))

        if cached:
            result = self.parseMovie(cached)
            log.info('Found: %s' % result['titles'][0] + ' (' + str(result['year']) + ')')

        return [result]

    def getInfo(self, identifier = None):

        cache_key = 'imdbapi.cache.%s' % identifier
        cached = self.getCache(cache_key, self.urls['info'] % identifier)

        if cached:
            result = self.parseMovie(cached)
            log.info('Found: %s' % result['titles'][0] + ' (' + str(result['year']) + ')')

        return result

    def parseMovie(self, movie):

        movie_data = {}
        try:

            if isinstance(movie, (str, unicode)):
                movie = json.loads(movie)

            movie_data = {
                'titles': [movie.get('Title', '')],
                'original_title': movie.get('Title', ''),
                'images': {
                    'poster': [movie.get('Poster', '')],
                },
                'rating': {
                    'imdb': (tryFloat(movie.get('Rating', 0)), tryInt(movie.get('Votes', ''))),
                    'rotten': (tryFloat(movie.get('tomatoRating', 0)), tryInt(movie.get('tomatoReviews', 0))),
                },
                'imdb': str(movie.get('ID', '')),
                'runtime': self.runtimeToMinutes(movie.get('Runtime', '')),
                'released': movie.get('Released', ''),
                'year': movie.get('Year', ''),
                'plot': movie.get('Plot', ''),
                'genres': movie.get('Genre', '').split(','),
                'directors': movie.get('Director', '').split(','),
                'writers': movie.get('Writer', '').split(','),
                'actors': movie.get('Actors', '').split(','),
            }
        except:
            log.error('Failed parsing IMDB API json: %s' % traceback.format_exc())

        return movie_data

    def runtimeToMinutes(self, runtime_str):
        runtime = 0

        regex = '(\d*.?\d+).(hr|hrs|mins|min)+'
        matches = re.findall(regex, runtime_str)
        for match in matches:
            nr, size = match
            runtime += tryInt(nr) * (60 if 'hr' in str(size) else 1)

        return runtime
