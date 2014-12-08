# -*- coding: utf-8 -*-
# Name:        logger
# Author:      Roman V.M.
# Created:     20.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import xbmc


def log(var_name='', variable=None):
    """
    Debug logger.
    """
    try:
        xbmc.log(u'plugin.video.ex.ua.alternative. {0}: {1}'.format(var_name, variable), xbmc.LOGDEBUG)
    except UnicodeEncodeError:
        xbmc.log('plugin.video.ex.ua.alternative. {0}: {1}'.format(var_name, variable.encode('utf-8')), xbmc.LOGDEBUG)


if __name__ == '__main__':
    pass
