# -*- coding: utf-8 -*-
# Module: views
# Author: Roman V. M.
# Created on: 25.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import os
import urllib
import xbmcaddon
from webloader import WebLoader
from logger import log as __log__
from constants import SEARCH_CATEGORIES

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path').decode('utf-8')
icons = os.path.join(addon_path, 'resources', 'icons')
loader = WebLoader()


def list_categories(plugin, categories):
    """
    Create a list of video categories form ex.ua
    """
    listing = []
    for category in categories:
        item = {'label': u'{0} [{1}]'.format(category['name'], category['items#']),
                'path': plugin.url_for('video_articles', mode='list', path=category['path'], page_No='0'),
                'thumbnail': os.path.join(icons, 'video.png')}
        listing.append(item)
    if addon.getSetting('usegoogle') == 'false':
        search_label = u'[Поиск…]'
        search_icon = os.path.join(icons, 'search.png')
    else:
        search_label = u'[Поиск Google…]'
        search_icon = os.path.join(icons, 'google.png')
    listing.append({'label': search_label,
                    'path': plugin.url_for('global_search'),
                    'thumbnail': search_icon})
    if plugin.addon.getSetting('savesearch') == 'true':
        listing.append({'label': u'[История поиска]',
                        'path': plugin.url_for('search_history'),
                        'thumbnail': os.path.join(icons, 'search.png')})
    if plugin.addon.getSetting('authorization') == 'true':
        if loader.is_logged_in():
            label = u'[Мои запомненные]'
            thumbnail = os.path.join(icons, 'bookmarks.png')
        else:
            label = u'[Войти на ex.ua]'
            thumbnail = os.path.join(icons, 'key.png')
        listing.append({'label': label,
                        'path': plugin.url_for('bookmarks'),
                        'thumbnail': thumbnail})
    __log__('categories; listing', listing)
    return listing


def list_videos(plugin, videos, path='', page=0):
    """
    Create a list of video articles to browse.
    """
    listing = []
    if path in SEARCH_CATEGORIES.keys() and page == 0:
            listing.append({'label': u'[Поиск в разделе…]',
                           'path': plugin.url_for('search_category', path=path),
                           'thumbnail': os.path.join(icons, 'search.png')})
    if addon.getSetting('show_home') == 'true' or page > 0:
        listing.append({'label': u'<< Главная',
                        'path': plugin.url_for('categories'),
                        'thumbnail': os.path.join(icons, 'home.png')})
    if videos['videos']:
        if videos['prev']:
            listing.append({'label': videos['prev'] + u' < Назад',
                            'path': plugin.url_for('video_articles', path=path, page_No=str(page - 1)),
                            'thumbnail': os.path.join(icons, 'previous.png')})
        for video in videos['videos']:
            item = {'label': video['title'],
                    'thumbnail': video['thumb'],
                    'path': plugin.url_for('display_path', path=video['path'])}
            listing.append(item)
        if videos['next']:
            listing.append({'label': u'Вперед > ' + videos['next'],
                            'path': plugin.url_for('video_articles', path=path, page_No=str(page + 1)),
                            'thumbnail': os.path.join(icons, 'next.png')})
    return listing


def list_video_details(plugin, video_details):
    """
    Show video details.
    """
    listing = []
    i = 0
    for video in video_details['videos']:
        if video['mirrors']:
            mirrors = urllib.urlencode(video['mirrors'])
        else:
            mirrors = 'none'
        try:
            flv = video_details['flvs'][i]
        except IndexError:
            flv = 'none'
        i += 1
        item = {'label': video['filename'],
                'thumbnail': video_details['thumb'],
                'path': plugin.url_for('select_mirror', path=video['path'], mirrors=mirrors, flv=flv),
                'info': {'title': video['filename'],
                         'genre': video_details['genre'],
                         'director': video_details['director'],
                         'plot': video_details['plot']},
                'is_playable': True,
                'context_menu': [(u'Загрузить файл…',
                u'RunScript({addon_path}/resources/lib/commands.py,download,{filename},{path},{mirrors},{flv})'.format(
                    addon_path=addon_path, filename=urllib.quote_plus(video['filename'].encode('utf-8')),
                        path=video['path'], mirrors=mirrors, flv=flv)),
                                (u'Просмотрено/не просмотрено', 'Action(ToggleWatched)')]
                }
        try:
            item['info']['year'] = int(video_details['year'])
        except ValueError:
            pass
        if video_details['cast']:
            item['info']['cast'] = video_details['cast'].split(', ')
        if video_details['rating']:
            try:
                item['info']['rating'] = float(video_details['rating'])
            except ValueError:
                pass
        listing.append(item)
    return listing
