# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import urllib
from collections import namedtuple
import xbmc
import xbmcgui
from simpleplugin import Plugin
import exua

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
_ = plugin.initialize_gettext()
SearchQuery = namedtuple('SearchQuery', ['query', 'path'])


def _get_plugin_content_type(path):
    if 'audio' in path:
        return 'audio'
    return 'video'


def _media_categories(categories, content):
    """
    Create plugin root listing
    """
    for category in categories:
        yield {
            'label': u'{0} [{1}]'.format(category.name, category.items),
            'url': plugin.get_url(action='media_list', path=category.path, page='0'),
            'thumb': os.path.join(icons, content + '.png')
        }
    yield {
        'label': u'[{0}]'.format(_('Search...')),
        'url': plugin.get_url(action='search'),
        'thumb': os.path.join(icons, 'search.png')
    }
    if plugin.savesearch:
        yield {
            'label': u'[{0}]'.format(_('Search history')),
            'url': plugin.get_url(action='search_history'),
            'thumb': os.path.join(icons, 'search.png')
        }


@plugin.cached(180)
def _get_categories(path):
    return exua.get_categories(path)


def root(params):
    """
    Plugin root action
    """
    content = _get_plugin_content_type(xbmc.getInfoLabel('Container.FolderPath'))
    if plugin.cache_pages:
        categories = _get_categories('/{0}/{1}?per=32'.format(plugin.site_lang, content))
    else:
        categories = exua.get_categories('/{0}/{1}?per=32'.format(plugin.site_lang, content))
    plugin.log(str(categories))
    return plugin.create_listing(_media_categories(categories, content))


def _media_list(path, media_listing, page=0):
    """
    Create the list of videos
    """
    if plugin.show_home:
        yield {
            'label': u'<< {0}'.format(_('Home')),
            'url': plugin.get_url(),
            'thumb': os.path.join(icons, 'home.png')
        }
    if media_listing.original_id is not None:
        yield {
            'label': u'[{0}]'.format(_('Search in the category...')),
            'url': plugin.get_url(action='search', original_id=media_listing.original_id),
            'thumb': os.path.join(icons, 'search.png')
        }
    if media_listing.prev is not None:
        yield {
            'label': u'{0} < {1}'.format(media_listing.prev, _('Previous')),
            'url': plugin.get_url(action='media_list', path=path, page=str(page - 1)),
            'thumb': os.path.join(icons, 'previous.png')
        }
    for item in media_listing.media:
        yield {
            'label': item.title,
            'url': plugin.get_url(action='display_path', path=item.path),
            'thumb': item.thumb
        }
    if media_listing.next is not None:
        yield {
            'label': u'{0} > {1}'.format(_('Next'), media_listing.next),
            'url': plugin.get_url(action='media_list', path=path, page=str(page + 1)),
            'thumb': os.path.join(icons, 'next.png')
        }


@plugin.cached(30)
def _get_media_list(path, page, items):
    return exua.get_media_list(path, page, items)


def media_list(params):
    """
    Display the list of videos

    params: path, page
    """
    page = int(params['page'])
    if plugin.cache_pages:
        media_listing = _get_media_list(params['path'], page, plugin.itemcount)
    else:
        media_listing = exua.get_media_list(params['path'], page, plugin.itemcount)
    plugin.log(str(media_listing))
    return plugin.create_listing(_media_list(params['path'], media_listing, page), update_listing=page > 0)


def _media_info(media_details):
    """
    Show a page with media information
    """
    for index, mediafile in enumerate(media_details.files):
        info = {}
        if media_details.info.get('year'):
            try:
                info['year'] = int(media_details.info['year'])
            except ValueError:
                pass
        if media_details.info.get('genre'):
            info['genre'] = media_details.info['genre']
        if media_details.info.get('director'):
            info['director'] = media_details.info['director']
        if media_details.info.get('plot'):
            info['plot'] = info['plotoutline'] = media_details.info['plot']
        if media_details.info.get('cast'):
            info['cast'] = media_details.info['cast'].split(', ')
        if media_details.info.get('rating'):
            try:
                info['rating'] = float(media_details.info['rating'])
            except ValueError:
                pass
        try:
            mp4 = media_details.mp4[index]
        except (IndexError, TypeError):
            mp4 = ''
        yield {
            'label': mediafile.filename,
            'thumb': media_details.thumb,
            'icon': media_details.thumb,
            'art': {'poster': media_details.thumb},
            'url': plugin.get_url(action='play',
                                  path=mediafile.path,
                                  mirrors=mediafile.mirrors,
                                  mp4=mp4),
            'is_playable': True,
            'context_menu': [(_('Mark as watched/unwatched'), 'Action(ToggleWatched)')],
            'info': {'video': info}
            }


@plugin.cached(180)
def _detect_page_type(path):
    return exua.detect_page_type(path)


def display_path(params):
    """
    Display a ex.ua page depending on its type

    params: path
    """
    if plugin.cache_pages:
        result = _detect_page_type(params['path'])
    else:
        result = exua.detect_page_type(params['path'])
    content = None
    if result.type == 'media_page':
        listing = _media_info(result.content)
        content = 'movies'  # The best tried and tested variant
    elif result.type == 'media_list':
        listing = _media_list(params['path'], result.content)
    elif result.type == 'media_categories':
        listing = _media_categories(result.content, _get_plugin_content_type(params['path']))
    else:
        listing = []
    return plugin.create_listing(listing, content=content)


def search(params):
    """
    Search on ex.ua

    params: oritinal_id (optional)
    """
    listing = []
    keyboard = xbmc.Keyboard('', _('Search query'))
    keyboard.doModal()
    search_text = keyboard.getText()
    if keyboard.isConfirmed() and search_text:
        search_path = '/search?s={0}'.format(urllib.quote_plus(search_text))
        if params.get('original_id'):
            search_path += '&original_id={0}'.format(params['original_id'])
        results = exua.get_media_list(search_path, 0, plugin.itemcount)
        plugin.log('Search results:' + str(results))
        if results.media:
            listing = _media_list(search_path, results)
            if plugin.savesearch:
                with plugin.get_storage() as storage:
                    history = storage.get('history', [])
                    history.insert(0, SearchQuery(search_text, search_path))
                    if len(history) > plugin.historylength:
                        history.pop(-1)
                    storage['history'] = history
        else:
            xbmcgui.Dialog().ok(_('No results found'), _('Refine your search and try again'))
    return plugin.create_listing(listing)


def search_history(params):
    listing = []
    with plugin.get_storage() as storage:
        history = storage.get('history', [])
        if len(history) > plugin.historylength:
            history[plugin.historylength - len(history):] = []
            storage['history'] = history
        for item in history:
            listing.append({
                'label': item.query,
                'url': plugin.get_url(action='media_list', path=item.path, page='0'),
                'thumb': os.path.join(icons, 'search.png')
            })
    return listing


def play(params):
    return exua.SITE + params['path']


plugin.actions['root'] = root
plugin.actions['media_list'] = media_list
plugin.actions['display_path'] = display_path
plugin.actions['search'] = search
plugin.actions['play'] = play
plugin.actions['search_history'] = search_history
