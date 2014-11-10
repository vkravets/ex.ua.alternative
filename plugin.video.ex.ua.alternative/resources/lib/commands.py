# -*- coding: utf-8 -*-
# Name:        commands
# Author:      Roman V.M.
# Created:     15.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import sys
import urllib
import urlparse
import xbmcvfs
import xbmcgui
from SimpleDownloader import SimpleDownloader


def clear_history():
    """Clear search history"""
    if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить историю поиска?'):
        xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.storage/storage')


def clear_chache():
    """Clear page cache"""
    if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно очистить кэш стнаниц?'):
        xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.storage/.functions')


def delete_cookies():
    """Delete cookies"""
    if xbmcgui.Dialog().yesno(u'Внимание!', u'Действительно удалить cookies?'):
        xbmcvfs.delete('special://profile/addon_data/plugin.video.ex.ua.alternative/.cookies')


def download_file():
    """Download a video file"""
    filename = urllib.unquote_plus(sys.argv[2]).decode('utf-8')
    path = sys.argv[3]
    mirrors = sys.argv[4]
    flv = sys.argv[5]
    if mirrors != 'none':
        mirrors_list = urlparse.parse_qsl(mirrors)
        menu_items = [u'Зеркало {0}'.format(item[0]) for item in mirrors_list]
        urls = [item[1] for item in mirrors_list]
    else:
        urls = []
        menu_items = []
    urls.insert(0, path)
    menu_items.insert(0, u'Оригинальное видео')
    if flv != 'none':
        urls.append(flv)
        menu_items.append(u'Облегченное видео (FLV)')
    index = xbmcgui.Dialog().select(u'Выберите видео', menu_items)
    if index >= 0:
        download_path = xbmcgui.Dialog().browse(0, u'Выберите папку для загрузки', 'video')
        if download_path:
            url = urls[index]
            if index == len(menu_items) - 1:
                filename = filename[:-3] + 'flv'
            else:
                url = 'http://www.ex.ua' + url
            downloader = SimpleDownloader()
            params = {'url': url, 'download_path': download_path, 'Title': u'Загрузка файла'}
            downloader.download(filename, params)


if __name__ == '__main__':
    if sys.argv[1] == 'history':
        clear_history()
    elif sys.argv[1] == 'cache':
        clear_chache()
    elif sys.argv[1] == 'cookies':
        delete_cookies()
    elif sys.argv[1] == 'download':
        download_file()
