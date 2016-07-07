# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import re
import os
import xbmc
from simpleplugin import Plugin
import exua

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
_ = plugin.initialize_gettext()


def _get_plugin_content_type(path):
    type_match = re.search(r'(video|audio)', path)
    if type_match is not None:
        return type_match.group(1)
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
        'label': u'[{0}]'.format(_('Search')),
        'url': plugin.get_url(action='search'),
        'thumb': os.path.join(icons, 'search.png')
    }


def root(params):
    """
    Plugin root action
    """
    content = _get_plugin_content_type(xbmc.getInfoLabel('Container.FolderPath'))
    categories = exua.get_categories('/{0}/{1}?per=32'.format(plugin.site_lang, content))
    plugin.log(str(categories))
    return plugin.create_listing(_media_categories(categories, content))


def _media_list(path, page, media):
    """
    Create the list of videos
    """
    yield {
        'label': u'<< {0}'.format(_('Home')),
        'url': plugin.get_url(),
        'thumb': os.path.join(icons, 'home.png')
    }
    if media.original_id is not None:
        yield {
            'label': u'[{0}]'.format(_('Search in the category')),
            'url': plugin.get_url(action='search', original_id=media.original_id),
            'thumb': os.path.join(icons, 'search.png')
        }
    if media.prev is not None:
        yield {
            'label': u'{0} < {1}'.format(media.prev, _('Previous')),
            'url': plugin.get_url(action='media_list', path=path, page=str(page - 1)),
            'thumb': os.path.join(icons, 'previous.png')
        }
    for item in media.media:
        yield {
            'label': item.title,
            'url': plugin.get_url(action='display_path', path=item.path),
            'thumb': item.thumb
        }
    if media.next is not None:
        yield {
            'label': u'{0} > {1}'.format(_('Next'), media.next),
            'url': plugin.get_url(action='media_list', path=path, page=str(page + 1)),
            'thumb': os.path.join(icons, 'next.png')
        }


def media_list(params):
    """
    Display the list of videos

    params: path, page
    """
    page = int(params['page'])
    media = exua.get_media_list(params['path'], page, plugin.itemcount)
    plugin.log(str(media))
    return plugin.create_listing(_media_list(params['path'], page, media), update_listing=page > 0)


def _media_info(media):
    """
    Show the page with media information
    """
    return []


def display_path(params):
    """
    Display a ex.ua page depending on its type

    params: path
    """
    result = exua.detect_page_type(params['path'])
    if result.type == 'media_page':
        listing = _media_info(result.content)
    elif result.type == 'media_list':
        listing = _media_list(params['path'], 0, result.content)
    elif result.type == 'media_categories':
        listing = _media_categories(result.content, _get_plugin_content_type(params['path']))
    else:
        listing = []
    return plugin.create_listing(listing)


def search(params):
    return []


plugin.actions['root'] = root
plugin.actions['media_list'] = media_list
plugin.actions['display_path'] = display_path
plugin.actions['search'] = search
