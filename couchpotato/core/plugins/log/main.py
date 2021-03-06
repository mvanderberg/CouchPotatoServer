from couchpotato.api import addApiView
from couchpotato.core.helpers.request import jsonified, getParam, getParams
from couchpotato.core.logger import CPLog
from couchpotato.core.plugins.base import Plugin
from couchpotato.environment import Env
import os
import traceback

log = CPLog(__name__)


class Logging(Plugin):

    def __init__(self):
        addApiView('logging.get', self.get)
        addApiView('logging.clear', self.clear)
        addApiView('logging.log', self.log)

    def get(self):

        nr = int(getParam('nr', 0))
        current_path = None

        total = 1
        for x in range(0, 50):

            path = '%s%s' % (Env.get('log_path'), '.%s' % x if x > 0 else '')

            # Check see if the log exists
            if not os.path.isfile(path):
                total = x - 1
                break

            # Set current path
            if x is nr:
                current_path = path

        log = ''
        if current_path:
            f = open(current_path, 'r')
            log = f.read()

        return jsonified({
            'success': True,
            'log': log,
            'total': total,
        })

    def clear(self):

        for x in range(0, 50):
            path = '%s%s' % (Env.get('log_path'), '.%s' % x if x > 0 else '')

            if not os.path.isfile(path):
                break

            try:

                # Create empty file for current logging
                if x is 0:
                    self.createFile(path, '')
                else:
                    os.remove(path)

            except:
                log.error('Couldn\'t delete file "%s": %s', (path, traceback.format_exc()))

        return jsonified({
            'success': True
        })

    def log(self):

        params = getParams()

        try:
            log_message = 'API log: %s' % params
            try:
                getattr(log, params.get('type', 'error'))(log_message)
            except:
                log.error(log_message)
        except:
            log.error('Couldn\'t log via API: %s' % params)


        return jsonified({
            'success': True
        })
