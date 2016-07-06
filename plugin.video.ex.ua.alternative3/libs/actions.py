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


def root(params):
    """
    Plugin root
    """
    categories = exua.get_categories('/{0}/video?per=32'.format(plugin.site_lang))
    listing = []
    for category in categories:
        listing.append({
            'label': u'{0} [{1}]'.format(category.name, category.items),
            'url': plugin.get_url(action='video_list', path=category.path, page='0'),
            'thumb': os.path.join(icons, 'video.png')
        })
    return listing


def video_list(params):
    """
    Display the list of videos

    params: action, path, page
    """
    videos = exua.get_video_list(params['path'], params['page'], plugin.itemcount)
    listing = [{
        'label': u'<< {0}'.format(_('Home')),
        'url': plugin.get_url(action='root'),
        'thumb': os.path.join(icons, 'home.png')
    }]
    page = int(params['page'])
    if videos.prev is not None:
        listing.append({
            'label': u'{0} < {1}'.format(videos.prev, _('Previous')),
            'url': plugin.get_url(action='video_list', path=params['path'], page=str(page - 1)),
            'thumb': os.path.join(icons, 'previous.png')
        })
    for item in videos.videos:
        listing.append({
            'label': item.title,
            'url': plugin.get_url(action='display_path', path=item.path),
            'thumb': item.thumb
        })
    if videos.next is not None:
        listing.append({
            'label': u'{0} > {1}'.format(_('Next'), videos.next),
            'url': plugin.get_url(action='video_list', path=params['path'], page=str(page + 1)),
            'thumb': os.path.join(icons, 'next.png')
        })
    plugin.log(str(listing))
    return plugin.create_listing(listing, update_listing=page > 0)


def display_path(params):
    return []


plugin.actions['root'] = root
plugin.actions['video_list'] = video_list
plugin.actions['display_path'] = display_path
