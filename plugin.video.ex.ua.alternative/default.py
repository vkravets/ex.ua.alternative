# -*- coding: utf-8 -*-
# Name:        plugin.video.ex.ua.alternative
# Author:      Roman V.M.
# Created:     04.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

# Import standard modules
import sys
import urllib
import urlparse
import os
# Import XBMC modules
import xbmc
import xbmcplugin
import xbmcgui
from xbmcswift2 import Plugin


# Numeric codes for search in video categories
SEARCH_CATEGORIES = {'/ru/video/foreign?r=23775': '2',
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


def get_history_length():
    """
    Get history length as an integer.
    """
    return {'0': 5, '1': 10, '2': 15, '3': 20, '4': 25}[plugin.addon.getSetting('historylength')]


def get_items_per_page():
    """Function description"""
    return {'0': '25', '1': '50', '2': '75', '3': '100'}[plugin.addon.getSetting('itemcount')]


# Create xbmcswift2 plugin instance.
plugin = Plugin()
addon_path = plugin.addon.getAddonInfo('path').decode('utf-8')
icons = os.path.join(addon_path, 'resources', 'icons')
# Import custom module.
sys.path.append(os.path.join(addon_path, 'resources', 'lib'))
import exua_parser
import webloader
import login_window
from logger import log as __log__
# Create web loader instance.
loader = webloader.WebLoader()
# Create persistent storage for history.
storage = plugin.get_storage('storage')
if plugin.addon.getSetting('savesearch') == 'true':
    # Create search_history storage if not exists.
    if storage.get('search_history') is None:
        storage['search_history'] = []
    elif storage.get('search_history') is not None and len(storage.get('search_history')) > get_history_length():
        # Remove extra elements if search history has been decreased.
        storage['search_history'][-(len(storage.get('search_history')) - get_history_length()):] = []


# Cache categories page for 3 hours
@plugin.cached(60 * 3)
def get_categories():
    return exua_parser.get_categories()


# Cache video list for 30 minutes
@plugin.cached(30)
def get_videos(path, page, pages):
    return exua_parser.get_videos(path, page=page, pages=pages)


# Cache checked page for 12 hours.
@plugin.cached(60 * 12)
def check_page(url):
    return exua_parser.check_page(url)


@plugin.route('/')
def categories():
    """
    Show home menu - ex.ua video categories.
    """
    if plugin.addon.getSetting('cache_pages') == 'true':
        categories = get_categories()
    else:
        categories = exua_parser.get_categories()
    return plugin.finish(list_categories(categories), view_mode=50)


def list_categories(categories):
    """
    Create a list of video categories form ex.ua
    """
    listing = []
    for category in categories:
        item = {'label': category['name'] + ' [' + category['items#'] + ']',
                'path': plugin.url_for('video_articles', mode='list', path=category['path'], page_No='0'),
                'thumbnail': os.path.join(icons, 'video.png')
        }
        listing.append(item)
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


@plugin.route('/categories/<path>/<page_No>')
def video_articles(path, page_No='0'):
    """
    Show video articles.
    """
    __log__('video_articles; path', path)
    page = int(page_No)
    pages = get_items_per_page()
    if plugin.addon.getSetting('cache_pages') == 'true':
        videos = get_videos(path, page, pages)
    else:
        videos = exua_parser.get_videos(path, page=page, pages=pages)
    listing = list_videos(videos, path, page)
    if page_No != '0':
        listing.insert(0, {'label': u'<< Главная',
                           'path': plugin.url_for('categories'),
                           'thumbnail': os.path.join(icons, 'home.png')})
    __log__('video_articles; listing', listing)
    return plugin.finish(listing, view_mode=50)


def list_videos(videos, path='', page=0):
    """
    Create a list of video articles to browse.
    """
    listing = []
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
        if path in SEARCH_CATEGORIES.keys() and page == 0:
            listing.insert(0, {'label': u'[Поиск…]',
                           'path': plugin.url_for('search_category', path=path),
                           'thumbnail': os.path.join(icons, 'search.png')})
    return listing


@plugin.route('/videos/<path>')
def display_path(path):
    """
    Display path depending on its contents: video item, video list or categories.
    """
    __log__('display_path; path', path)
    if plugin.addon.getSetting('cache_pages') == 'true':
        page_type, contents = check_page(path)
    else:
        page_type, contents = exua_parser.check_page(path)
    view_mode = 50
    if page_type == 'video_page':
        listing = list_video_details(contents)
        if plugin.addon.getSetting('use_skin_info') == 'true':
            # Switch view based on a current skin.
            current_skin = xbmc.getSkinDir()
            if current_skin == 'skin.confluence' or current_skin == 'skin.confluence-plood':
                view_mode = 503
            elif current_skin == 'skin.aeon.nox':
                view_mode = 52
            elif current_skin == 'skin.aeon.nox.5':
                view_mode = 55
    elif page_type == 'video_list':
        listing = list_videos(contents, path=path)
    elif page_type == 'categories':
        listing = list_categories(contents)
    else:
        listing = []
    __log__('display_path; listing', listing)
    return plugin.finish(listing, view_mode=view_mode)


def list_video_details(video_details):
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


@plugin.route('/play/<path>/<mirrors>/<flv>', name='select_mirror')
@plugin.route('/play/<path>')
def play_video(path, mirrors='', flv=''):
    """
    Play video.
    """
    if mirrors and flv:
        if plugin.addon.getSetting('choose_mirrors') == '1':
            if mirrors != 'none':
                mirrors_list = urlparse.parse_qsl(mirrors)
                menu_items = [u'Зеркало ' + item[0] for item in mirrors_list]
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
                path = urls[index]
            else:
                return None
        elif plugin.addon.getSetting('choose_mirrors') == '2':
            path = flv
    if plugin.addon.getSetting('authorization') == 'true' and loader.is_logged_in():
        cookies = '|Cookie=' + urllib.urlencode(loader.get_cookies())
    else:
        cookies = ''
    if path[0] == '/':
        path = 'http://www.ex.ua' + path
        if plugin.addon.getSetting('direct_link') == 'true':
            path = loader.get_direct_link(path)
    __log__('play_video; path', path)
    __log__('play_video; cookies', cookies)
    plugin.set_resolved_url(path + cookies)


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
        __log__('search_category; search_path', search_path)
        if plugin.addon.getSetting('cache_pages') == 'true':
            videos = get_videos(search_path, page=0, pages=get_items_per_page())
        else:
            videos = exua_parser.get_videos(search_path, page=0, pages=get_items_per_page())
        listing = list_videos(videos, search_path)
        if listing and plugin.addon.getSetting('savesearch') == 'true':
            storage['search_history'].insert(0, {'text': search_text, 'query': search_path})
            if len(storage['search_history']) > get_history_length():
                storage['search_history'].pop(-1)
        elif not listing:
            xbmcgui.Dialog().ok(u'Ничего не найдено!', u'Уточните поисковый запрос и повторите попытку.')
    __log__('search_category; listing', listing)
    return plugin.finish(listing, view_mode=50)


@plugin.route('/search_history/')
def search_history():
    """
    Show search history.
    """
    listing = []
    for item in storage.get('search_history'):
        listing.append({'label': item['text'],
                        'path': plugin.url_for('video_articles', path=item['query'], page_No='0'),
                        'thumbnail': os.path.join(icons, 'search.png')})
    __log__('search_history; listing', listing)
    return plugin.finish(listing, view_mode=50)


@plugin.route('/bookmarks/')
def bookmarks():
    successful_login = False
    listing = []
    if not loader.is_logged_in():
        username = plugin.addon.getSetting('username')
        password = webloader.decode(plugin.addon.getSetting('password'))
        captcha = loader.check_captcha()
        login_dialog = login_window.LoginWindow(username, password, captcha['captcha_file'])
        if not login_dialog.login_cancelled:
            successful_login = loader.login(login_dialog.username, login_dialog.password,
                                            captcha_text=login_dialog.captcha_text, captcha_id=captcha['captcha_id'])
            if successful_login:
                plugin.addon.setSetting('username', login_dialog.username)
                if plugin.addon.getSetting('save_pass') == 'true':
                    plugin.addon.setSetting('password', webloader.encode(login_dialog.password))
                else:
                    plugin.addon.setSetting('password', '')
            else:
                xbmcgui.Dialog().ok(u'Ошибка входа!', u'Проверьте логин и пароль, а затем повторите попытку.')
    __log__('bookmarks; is_logged_in', loader.is_logged_in())
    __log__('bookmarks; successful_login', successful_login)
    if loader.is_logged_in() or successful_login:
        listing += list_videos(exua_parser.get_videos('/buffer', loader))
    __log__('bookmarks; listing', listing)
    return plugin.finish(listing, view_mode=50)


if __name__ == '__main__':
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    plugin.run()
