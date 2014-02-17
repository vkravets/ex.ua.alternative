# -*- coding: utf-8 -*-
# Name:        downloader
# Author:      Roman V.M.
# Created:     10.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import sys
import xbmcgui
from SimpleDownloader import SimpleDownloader


def download_file():
    downloader = SimpleDownloader()
    dialog = xbmcgui.Dialog()
    download_path = dialog.browse(0, u'Выберите папку для загрузки', 'video')
    if download_path:
        params = {'url': 'http://www.ex.ua' + sys.argv[1], 'download_path': download_path, 'Title': u'Загрузка файла'}
        downloader.download(sys.argv[2].decode('utf-8'), params)

if __name__ == '__main__':
    download_file()
