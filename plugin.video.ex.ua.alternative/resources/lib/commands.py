# -*- coding: utf-8 -*-
# Name:        commands
# Author:      Roman V.M.
# Created:     15.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import sys
import xbmc
import xbmcvfs
import xbmcgui
from SimpleDownloader import SimpleDownloader
from logger import log as __log__


def main():
    if sys.argv[1] == 'history':
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить историю поиска?'):
            xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.storage/storage')
    elif sys.argv[1] == 'cache':
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить кэш стнаниц?'):
            xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.storage/.functions')
    elif sys.argv[1] == 'cookies':
        if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно удалить cookies?'):
            xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.cookies')
    elif sys.argv[1] == 'download':
        downloader = SimpleDownloader()
        download_path = xbmcgui.Dialog().browse(0, u'Выберите папку для загрузки', 'video')
        if download_path:
            params = {'url': 'http://www.ex.ua' + sys.argv[2], 'download_path': download_path, 'Title': u'Загрузка файла'}
            downloader.download(sys.argv[3].decode('utf-8'), params)
    elif sys.argv[1] == 'play_flv':
        __log__('commands; play flv_file')
        xbmc.Player().play(sys.argv[2])


if __name__ == '__main__':
    __log__('commands run')
    main()
