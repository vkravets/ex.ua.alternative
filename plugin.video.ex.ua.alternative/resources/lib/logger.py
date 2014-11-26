# -*- coding: utf-8 -*-
# Name:        logger
# Author:      Roman V.M.
# Created:     20.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import xbmcaddon

_addon = xbmcaddon.Addon()


def log(var_name='', variable=None):
    """
    Debug logger.
    """
    if _addon.getSetting('debug') == 'true':
        try:
            print u'plugin.video.ex.ua.alternative. {0}: {1}'.format(var_name, variable)
        except UnicodeEncodeError:
            print u'plugin.video.ex.ua.alternative. {0}: {1}'.format(var_name, variable.encode('utf-8'))


if __name__ == '__main__':
    pass
