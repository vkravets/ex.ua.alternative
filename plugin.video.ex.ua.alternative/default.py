# -*- coding: utf-8 -*-
# Name:        plugin.video.ex.ua.alternative
# Author:      Roman V.M.
# Created:     04.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

# Import standard modules
import sys
import re
import urllib
import os
# Import XBMC modules
import xbmc
import xbmcplugin
import xbmcgui
from xbmcswift2 import Plugin


# Numeric codes for search in video categories
SEARCH_CATEGORIES = {   '/ru/video/foreign?r=23775': '2',
                        '/ru/video/our?r=23775': '70538',
                        '/ru/video/foreign_series?r=23775': '1988',
                        '/ru/video/our_series?r=23775': '422546',
                        '/ru/video/cartoon?r=23775': '1989',
                        '/ru/video/anime?r=23775': '23786',
                        '/ru/video/documentary?r=23775': '1987',
                        '/ru/video/trailer?r=23775': '1990',
                        '/ru/video/clip?r=23775': '1991',
                        '/ru/video/concert?r=23775': '70533',
                        '/ru/video/show?r=23775': '23775',
                        '/ru/video/training?r=23775': '28714',
                        '/ru/video/sport?r=23775': '69663',
                        '/ru/video/short?r=23775': '23785',
                        '/ru/video/theater?r=23775': '70665',
                        '/ru/video/sermon?r=23775': '371146',
                        '/ru/video/commercial?r=23775': '371152',
                        '/ru/video/mobile?r=23775': '607160',
                        '/ru/video/artist?r=23775': '7513588',
                        '/73427589?r=23775': '73427589'}


def _log(var_name='', variable=None):
    """
    Debug logger.
    """
    print u'***!!!DEBUG!!!*** plugin.video.ex.ua.alternative. %s: %s' % (var_name, variable)


def get_history_length():
    """
    Get history length as an integer.
    """
    return {'0': 5, '1': 10, '2': 15, '3': 20, '4': 25}[plugin.addon.getSetting('historylength')]


# Create xbmcswift2 plugin instance.
plugin = Plugin()
addon_path = plugin.addon.getAddonInfo('path').decode('utf-8')
icons = os.path.join(addon_path, 'resources', 'icons')
# Import custom module.
sys.path.append(os.path.join(addon_path, 'resources', 'lib'))
import exua_parser
import webbot
import login_window
# Create login bot instance.
login_bot = webbot.WebBot()
# Create persistent storage for history.
storage = plugin.get_storage('storage')
if plugin.addon.getSetting('savesearch') == 'true':
    # Create search_history storage if not exists.
    if storage.get('search_history') is None:
        storage['search_history'] = []
    elif storage.get('search_history') is not None and len(storage.get('search_history')) > get_history_length():
        # Remove extra elements if search history has been decreased.
        storage['search_history'][-(len(storage.get('search_history')) - get_history_length()):] = []


# Cache the main page for 3 hours
@plugin.cached(60*3)
def get_categories():
    return exua_parser.get_categories()


# Cache video list for 30 minutes
@plugin.cached(30)
def get_videos(path, page, pages):
    return exua_parser.get_videos(path, page, pages)


# Cache video details for 1 day.
@plugin.cached()
def get_video_details(video_url):
    return exua_parser.get_video_details(video_url)


def list_videos(path, page_No, mode):
    """
    Create a list of video articles to browse.
    """
    listing = []
    page = int(page_No)
    pages = {'0': '25', '1': '50', '2': '75', '3': '100'}[plugin.addon.getSetting('itemcount')]
    if path == '/buffer':
        videos = exua_parser.get_videos(path, page, pages)
    else:
        videos = get_videos(path, page, pages)
##    _log('bookmarked videos', videos)
    if videos['videos']:
        if page or mode == 'search':
            listing.append({'label': u'<< Главная',
                            'path': plugin.url_for('categories'),
                            'thumbnail': os.path.join(icons, 'home.png')})
        if page:
            listing.append({'label': videos['prev'] + u' < Назад',
                            'path': plugin.url_for('video_articles', mode=mode, path=path, page_No=str(page - 1)),
                            'thumbnail': os.path.join(icons, 'previous.png')})
        for video in videos['videos']:
            item = {'label': video['title'],
                    'thumbnail': video['thumb'],
                    'path': plugin.url_for('video_item', video_url=video['url'])
                    }
            listing.append(item)
        if videos['next']:
            listing.append({'label': u'Вперед > ' + videos['next'],
                            'path': plugin.url_for('video_articles', mode=mode, path=path, page_No=str(page + 1)),
                            'thumbnail': os.path.join(icons, 'next.png')})
    return listing


@plugin.route('/')
def categories():
    """
    Show home menu - ex.ua video categories.
    """
    categories = get_categories()
    listing = []
    for category in categories:
        item = {'label': category['name'] + ' [' + category['items#'] + ']',
                'path': plugin.url_for('video_articles', mode='list', path=category['url'], page_No='0'),
                'thumbnail': os.path.join(icons, 'video.png')
                }
        listing.append(item)
    if plugin.addon.getSetting('savesearch') == 'true':
        listing.append({'label': u'[История поиска]',
                        'path': plugin.url_for('search_history'),
                        'thumbnail': os.path.join(icons, 'search.png')})
    if plugin.addon.getSetting('authorization') == 'true':
        if login_bot.is_logged_in():
            label = u'[Мои закладки]'
            thumbnail = os.path.join(icons, 'bookmarks.png')
        else:
            label = u'[Войти на ex.ua]'
            thumbnail = os.path.join(icons, 'key.png')
        listing.append({'label': label,
                        'path': plugin.url_for('bookmarks'),
                        'thumbnail': thumbnail})
    return plugin.finish(listing, view_mode=50)


@plugin.route('/categories/<mode>/<path>/<page_No>')
def video_articles(mode, path, page_No='0'):
    """
    Show video articles.
    """
    listing = list_videos(path, page_No, mode)
    if page_No == '0' and mode == 'list':
        listing.insert(0, {'label': u'[Поиск…]',
                            'path': plugin.url_for('search_category', path=path),
                            'thumbnail': os.path.join(icons, 'search.png')})
        listing.insert(1, {'label': u'< Главная',
                            'path': plugin.url_for('categories'),
                            'thumbnail': os.path.join(icons, 'home.png')})
    return plugin.finish(listing, view_mode=50)


@plugin.route('/videos/<video_url>')
def video_item(video_url):
    """
    Show video details.
    """
    video_details = get_video_details(video_url)
    if video_details['videos']:
        if plugin.addon.getSetting('prefer_lq') == 'true' and video_details['flvs']:
            videos_list = []
            for index in range(len(video_details['flvs'])):
                flv = {}
                flv['filename'] = 'Video ' + str(index + 1)
                flv['url'] = video_details['flvs'][index]
            videos_list.append(flv)
        else:
            videos_list = video_details['videos']
        listing = []
        for video in videos_list:
            item = {'label': video['filename'],
                    'thumbnail': video_details['thumb'],
                    'info': {   'title': video['filename'],
                                'genre': video_details['genre'],
                                'director': video_details['director'],
                                'plot': video_details['plot']},
                    'is_playable': True,
                    'path': plugin.url_for('play_video', url=video['url']),
                    'context_menu': [(u'Загрузить файл…',
                                        u'RunScript({path}/resources/lib/downloader.py,{url},{filename})'.format(
                                                    path=addon_path, url=video['url'],
                                                        filename=video['filename']))]
                    }
            if video_details['year']:
                try:
                    item['info']['year'] = int(video_details['year'])
                except ValueError:
                    pass
            if video_details['cast']:
                item['info']['cast'] = video_details['cast'].split(', ')
##            if video_details['duration']:
##                duration = video_details['duration'].split(':')
##                try:
##                    item['info']['duration'] = str(int(duration[0]) * 60 + int(duration[1]))
##                except ValueError:
##                    pass
            listing.append(item)
        # Switch view based on a current skin.
        current_skin = xbmc.getSkinDir()
        if current_skin == 'skin.confluence' or current_skin == 'skin.confluence-plood':
            view_mode = 503
        elif current_skin == 'skin.aeon.nox':
            view_mode = 52
        elif current_skin == 'skin.aeon.nox.5':
            view_mode = 55
        else:
            view_mode = 50
    else:
        listing = list_videos(video_url, '0', mode='list')
        view_mode = 50
    return plugin.finish(listing, view_mode=view_mode)


@plugin.route('/play/<url>')
def play_video(url):
    """
    Play video.
    """
    if url[0] == '/':
        url = 'http://www.ex.ua' + url
    if plugin.addon.getSetting('authorization') == 'true' and login_bot.is_logged_in():
        cookies = '|Cookie=' + urllib.urlencode(login_bot.get_cookies())
    else:
        cookies = ''
    _log('cookies', cookies)
    plugin.set_resolved_url(url + cookies)


@plugin.route('/search_category/<path>')
def search_category(path):
    """
    Show search.
    """
    keyboard = xbmc.Keyboard('', u'Поисковый запрос')
    keyboard.doModal()
    search_text = keyboard.getText()
    if search_text and keyboard.isConfirmed():
        search_path = '/search?s={query}&original_id={id_}'.format(
                            query=urllib.quote_plus(search_text), id_=SEARCH_CATEGORIES[path])
        listing = list_videos(search_path, '0', mode='search')
        if listing and plugin.addon.getSetting('savesearch') == 'true':
            storage['search_history'].insert(0, {'text': search_text, 'query': search_path})
            if len(storage['search_history']) > get_history_length():
                storage['search_history'].pop(-1)
        elif not listing:
            xbmcgui.Dialog().ok(u'Ничего не найдено!', u'Уточните поисковый запрос и повторите попытку.')
    else:
        listing = []
    listing.insert(1, {'label': u'< Назад',
                            'path': plugin.url_for('video_articles', mode='list', path=path, page_No='0'),
                            'thumbnail': os.path.join(icons, 'previous.png')})
    return plugin.finish(listing, view_mode=50)


@plugin.route('/search_history/')
def search_history():
    """
    Show search history.
    """
    listing = [{'label': u'< Главная',
                            'path': plugin.url_for('categories'),
                            'thumbnail': os.path.join(icons, 'home.png')}]
    for item in storage.get('search_history'):
        listing.append({'label': item['text'],
                        'path': plugin.url_for('video_articles', mode='search', path=item['query'], page_No='0'),
                        'thumbnail': os.path.join(icons, 'search.png')})
    return plugin.finish(listing, view_mode=50)


@plugin.route('/bookmarks/')
def bookmarks():
    successful_login = False
    listing = [{'label': u'< Главная',
                            'path': plugin.url_for('categories'),
                            'thumbnail': os.path.join(icons, 'home.png')}]
    if not login_bot.is_logged_in():
        username = plugin.addon.getSetting('username')
        password = webbot.decode(plugin.addon.getSetting('password'))
        captcha = login_bot.check_captcha()
        if not captcha:
            captcha['captcha_id'] = captcha['captcha_file'] = ''
        login_dialog = login_window.LoginWindow(username, password, captcha['captcha_file'])
        if not login_dialog.login_cancelled:
            successful_login = login_bot.login(login_dialog.username, login_dialog.password,
                                        login_dialog.remember_user, login_dialog.captcha_text, captcha['captcha_id'])
            if successful_login:
                plugin.addon.setSetting('username', login_dialog.username)
                if plugin.addon.getSetting('save_pass') == 'true':
                    plugin.addon.setSetting('password', webbot.encode(login_dialog.password))
                else:
                    plugin.addon.setSetting('password', '')
            else:
                xbmcgui.Dialog().ok(u'Ошибка входа!', u'Проверьте логин и пароль, а затем повторите попытку')
    if login_bot.is_logged_in() or successful_login:
        listing = listing + list_videos('/buffer', '0', mode='list')
    return plugin.finish(listing, view_mode=50)


if __name__ == '__main__':
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    plugin.run()
