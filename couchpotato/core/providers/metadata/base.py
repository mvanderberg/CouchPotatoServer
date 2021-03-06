from couchpotato.core.event import addEvent, fireEvent
from couchpotato.core.helpers.variable import mergeDicts
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
import json
import os.path
import shutil
import traceback

log = CPLog(__name__)


class MetaDataBase(Plugin):

    enabled_option = 'meta_enabled'

    def __init__(self):
        addEvent('renamer.after', self.create)

    def create(self, release):
        if self.isDisabled(): return

        log.info('Creating %s metadata.' % self.getName())

        # Update library to get latest info
        try:
            updated_library = fireEvent('library.update', release['library']['identifier'], force = True, single = True)
            release['library'] = mergeDicts(release['library'], updated_library)
        except:
            log.error('Failed to update movie, before creating metadata: %s' % traceback.format_exc())

        root = self.getRootName(release)

        try:
            movie_info = json.loads(release['library'].get('info'))
        except:
            log.error('Failed to parse movie info: %s' % traceback.format_exc())
            movie_info = {}

        for file_type in ['nfo', 'thumbnail', 'fanart']:
            try:
                # Get file path
                name = getattr(self, 'get' + file_type.capitalize() + 'Name')(root)

                if name and self.conf('meta_' + file_type):

                    # Get file content
                    content = getattr(self, 'get' + file_type.capitalize())(movie_info = movie_info, data = release)
                    if content:
                        log.debug('Creating %s file: %s' % (file_type, name))
                        if os.path.isfile(content):
                            shutil.copy2(content, name)
                        else:
                            self.createFile(name, content)

            except:
                log.error('Unable to create %s file: %s' % (file_type, traceback.format_exc()))

    def getRootName(self, data):
        return

    def getFanartName(self, root):
        return

    def getThumbnailName(self, root):
        return

    def getNfoName(self, root):
        return

    def getNfo(self, movie_info = {}, data = {}):
        return

    def getThumbnail(self, movie_info = {}, data = {}, wanted_file_type = 'poster_original'):
        file_types = fireEvent('file.types', single = True)
        for file_type in file_types:
            if file_type.get('identifier') == wanted_file_type:
                break

        for cur_file in data['library'].get('files', []):
            if cur_file.get('type_id') is file_type.get('id'):
                return cur_file.get('path')

    def getFanart(self, movie_info = {}, data = {}):
        return self.getThumbnail(movie_info = movie_info, data = data, wanted_file_type = 'backdrop_original')
