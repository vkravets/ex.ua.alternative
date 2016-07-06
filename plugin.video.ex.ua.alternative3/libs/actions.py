# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
from simpleplugin import Plugin
import exua

plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
_ = plugin.initialize_gettext()


def _root():
    """
    Create plugin root listing
    """
    categories = exua.get_categories('/{0}/video?per=32'.format(plugin.site_lang))
    plugin.log(str(categories))
    for category in categories:
        yield {
            'label': u'{0} [{1}]'.format(category.name, category.items),
            'url': plugin.get_url(action='video_list', path=category.path, page='0'),
            'thumb': os.path.join(icons, 'video.png')
        }


def root(params):
    """
    Plugin root
    """
    return plugin.create_listing(_root())


def _video_list(path, page):
    """
    Create the list of videos
    """
    videos = exua.get_video_list(path, page, plugin.itemcount)
    plugin.log(str(videos))
    yield {
        'label': u'<< {0}'.format(_('Home')),
        'url': plugin.get_url(action='root'),
        'thumb': os.path.join(icons, 'home.png')
    }
    if videos.prev is not None:
        yield {
            'label': u'{0} < {1}'.format(videos.prev, _('Previous')),
            'url': plugin.get_url(action='video_list', path=path, page=str(page - 1)),
            'thumb': os.path.join(icons, 'previous.png')
        }
    for item in videos.videos:
        yield {
            'label': item.title,
            'url': plugin.get_url(action='display_path', path=item.path),
            'thumb': item.thumb
        }
    if videos.next is not None:
        yield {
            'label': u'{0} > {1}'.format(_('Next'), videos.next),
            'url': plugin.get_url(action='video_list', path=path, page=str(page + 1)),
            'thumb': os.path.join(icons, 'next.png')
        }


def video_list(params):
    """
    Display the list of videos

    params: action, path, page
    """
    page = int(params['page'])
    return plugin.create_listing(_video_list(params['path'], page), update_listing=page > 0)


def display_path(params):
    return []


plugin.actions['root'] = root
plugin.actions['video_list'] = video_list
plugin.actions['display_path'] = display_path
