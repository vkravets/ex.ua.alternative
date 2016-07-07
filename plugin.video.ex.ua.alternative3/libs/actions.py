# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import xbmc
from simpleplugin import Plugin
import exua

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
_ = plugin.initialize_gettext()


def _root():
    """
    Create plugin root listing
    """
    if 'video' in xbmc.getInfoLabel('Container.FolderPath'):
        content = 'video'
    else:
        content = 'audio'
    categories = exua.get_categories('/{0}/{1}?per=32'.format(plugin.site_lang, content))
    plugin.log(str(categories))
    for category in categories:
        yield {
            'label': u'{0} [{1}]'.format(category.name, category.items),
            'url': plugin.get_url(action='media_list', path=category.path, page='0'),
            'thumb': os.path.join(icons, content + '.png')
        }


def root(params):
    """
    Plugin root action
    """
    return plugin.create_listing(_root())


def _media_list(path, page):
    """
    Create the list of videos
    """
    media = exua.get_media_list(path, page, plugin.itemcount)
    plugin.log(str(media))
    yield {
        'label': u'<< {0}'.format(_('Home')),
        'url': plugin.get_url(),
        'thumb': os.path.join(icons, 'home.png')
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

    params: action, path, page
    """
    page = int(params['page'])
    return plugin.create_listing(_media_list(params['path'], page), update_listing=page > 0)


def display_path(params):
    return []


plugin.actions['root'] = root
plugin.actions['media_list'] = media_list
plugin.actions['display_path'] = display_path
