# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import re
import xbmc
import xbmcgui
from xbmcaddon import Addon

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(basedir, 'addon.xml')) as fo:
    addon_id = re.search(r'addon id="(.+?)"', fo.read()).group(1)

addon = Addon(addon_id)
config_dir = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
icon = os.path.join(basedir, 'icon.png')
dialog = xbmcgui.Dialog()


def loc_string(id_):
    return addon.getLocalizedString(id_).encode('utf-8')


def clear_cache():
    cache = os.path.join(config_dir, '__cache__.pcl')
    if os.path.exists(cache) and dialog.yesno(loc_string(32025), loc_string(32026)):
        os.remove(cache)
        if not os.path.exists(cache):
            dialog.notification(addon_id, loc_string(32017), icon=icon, sound=False)
