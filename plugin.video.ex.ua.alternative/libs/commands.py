# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import re
import sys
import xbmc
import xbmcgui
from xbmcaddon import Addon

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(basedir, 'addon.xml')) as fo:
    addon_id = re.search(r'addon id="(.+?)"', fo.read()).group(1)

# Here I use the vanilla Kodi Python API instead of SimplePlugin
# because using library addons in non-addon scripts
# may be depreciated in the future (according to a warning in the Kodi log).
addon = Addon(addon_id)
config_dir = xbmc.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
icon = os.path.join(basedir, 'icon.png')
dialog = xbmcgui.Dialog()


def loc_string(id_):
    return addon.getLocalizedString(id_).encode('utf-8')


def clear_history():
    history = os.path.join(config_dir, '__history__.pcl')
    if os.path.exists(history) and dialog.yesno(loc_string(32025), loc_string(32047)):
        os.remove(history)
        if not os.path.exists(history):
            dialog.notification(addon_id, loc_string(32048), icon=icon, sound=False)


def clear_cache():
    cache = os.path.join(config_dir, '__cache__.pcl')
    if os.path.exists(cache) and dialog.yesno(loc_string(32025), loc_string(32026)):
        os.remove(cache)
        if not os.path.exists(cache):
            dialog.notification(addon_id, loc_string(32027), icon=icon, sound=False)


def clear_cookies():
    cookies = os.path.join(config_dir, '__cookies__.pcl')
    if os.path.exists(cookies) and dialog.yesno(loc_string(32025), loc_string(32049)):
        os.remove(cookies)
        if not os.path.exists(cookies):
            dialog.notification(addon_id, loc_string(32050), icon=icon, sound=False)


if __name__ == '__main__':
    if sys.argv[1] == 'history':
        clear_history()
    elif sys.argv[1] == 'cache':
        clear_cache()
    elif sys.argv[1] == 'cookies':
        clear_cookies()
