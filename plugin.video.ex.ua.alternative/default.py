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


# Create xbmcswift2 plugin instance.
plugin = Plugin()
addon_path = plugin.addon.getAddonInfo('path').decode('utf-8')
# Import custom modules.
sys.path.append(os.path.join(addon_path, 'resources', 'lib'))
import exua_parser
import webloader
import login_window
import views
from constants import SEARCH_CATEGORIES
from logger import log as __log__
# Create web loader instance.
loader = webloader.WebLoader()
# Create a persistent storage for search history.
storage = plugin.get_storage('storage')
if plugin.addon.getSetting('savesearch') == 'true':
    # Create search_history storage if not exists.
    if storage.get('search_history') is None:
        storage['search_history'] = []
    elif storage.get('search_history') is not None and len(storage.get('search_history')) >\
            int(plugin.addon.getSetting('historylength')):
        # Remove extra elements if search history has been decreased.
        storage['search_history'][-(len(storage.get('search_history')) -
                                    int(plugin.addon.getSetting('historylength'))):] = []


# Cache categories page for 3 hours
@plugin.cached(180)
def get_categories():
    return exua_parser.get_categories()


# Cache video list for 20 minutes
@plugin.cached(20)
def get_videos(path, page, pages):
    return exua_parser.get_videos(path, page=page, pages=pages)


# Cache checked page for 3 hours.
@plugin.cached(180)
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
    return plugin.finish(views.list_categories(plugin, categories), view_mode=50)


@plugin.route('/categories/<path>/<page_No>')
def video_articles(path, page_No='0'):
    """
    Show video articles.
    """
    __log__('video_articles; path', path)
    page = int(page_No)
    pages = plugin.addon.getSetting('itemcount')
    if plugin.addon.getSetting('cache_pages') == 'true':
        videos = get_videos(path, page, pages)
    else:
        videos = exua_parser.get_videos(path, page=page, pages=pages)
    listing = views.list_videos(plugin, videos, path, page)
    __log__('video_articles; listing', listing)
    return plugin.finish(listing, view_mode=50)


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
        listing = views.list_video_details(plugin, contents)
        if plugin.addon.getSetting('use_skin_info') == 'true':
            # Switch view based on a current skin.
            current_skin = xbmc.getSkinDir()
            if current_skin in ('skin.confluence', 'skin.confluence-plood', 'skin.confluence-plood-gotham'):
                view_mode = 503
            elif current_skin in ('skin.aeon.nox', 'skin.aeon.nox.gotham'):
                view_mode = 52
            elif current_skin == 'skin.aeon.nox.5':
                view_mode = 55
    elif page_type == 'video_list':
        listing = views.list_videos(plugin, contents, path=path)
    elif page_type == 'categories':
        listing = views.list_categories(plugin, contents)
    else:
        listing = []
    __log__('display_path; listing', listing)
    return plugin.finish(listing, view_mode=view_mode)


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
            if not path:
                xbmc.executebuiltin(u'Notification(Ошибка!,Ссылка недоступна)'.encode('utf-8'))
                return None
    __log__('play_video; path', path)
    __log__('play_video; cookies', cookies)
    plugin.set_resolved_url(path + cookies)


@plugin.route('/global_search/', name='global_search')
@plugin.route('/search_category/<path>')
def search_category(path=''):
    """
    Perform search in an ex.ua category or via Google.com.
    """
    listing = []
    keyboard = xbmc.Keyboard('', u'Поисковый запрос')
    keyboard.doModal()
    search_text = keyboard.getText()
    if search_text and keyboard.isConfirmed():
        if path:
            search_path = '/search?s={0}&original_id={1}'.format(urllib.quote_plus(search_text), SEARCH_CATEGORIES[path])
        else:
            if plugin.addon.getSetting('use_google') == 'false':
                search_path = '/search?s={0}'.format(urllib.quote_plus(search_text))
            else:
                search_path = 'http://www.google.com.ua/search?q=site%3Aex.ua+{0}'.format(urllib.quote_plus(search_text))
        __log__('search_category; search_path', search_path)
        if plugin.addon.getSetting('cache_pages') == 'true':
            videos = get_videos(search_path, page=0, pages=plugin.addon.getSetting('itemcount'))
        else:
            videos = exua_parser.get_videos(search_path, page=0, pages=plugin.addon.getSetting('itemcount'))
        listing = views.list_videos(plugin, videos, search_path)
        if listing and plugin.addon.getSetting('savesearch') == 'true':
            storage['search_history'].insert(0, {'text': search_text, 'query': search_path})
            if len(storage['search_history']) > int(plugin.addon.getSetting('historylength')):
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
    listing = views.list_search_history(plugin)
    __log__('search_history; listing', listing)
    return plugin.finish(listing, view_mode=50)


@plugin.route('/bookmarks/')
def bookmarks():
    """
    Login to display ex.ua bookmarks

    :return: None
    """
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
        del login_dialog
    __log__('bookmarks; is_logged_in', loader.is_logged_in())
    __log__('bookmarks; successful_login', successful_login)
    if loader.is_logged_in() or successful_login:
        listing += views.list_videos(plugin, exua_parser.get_videos('/buffer', loader))
    __log__('bookmarks; listing', listing)
    return plugin.finish(listing, view_mode=50)


if __name__ == '__main__':
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')  # Needed for extended view switching!
    plugin.run()
