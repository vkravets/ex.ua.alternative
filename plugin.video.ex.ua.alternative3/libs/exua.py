# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence: GPL v.3: http://www.gnu.org/copyleft/gpl.html

import ast
import re
import sys
from collections import namedtuple
from bs4 import BeautifulSoup
from simpleplugin import Plugin
import webclient

SITE = 'http://www.ex.ua'

# Extensions for supported media files
MEDIA_EXTENSIONS = 'avi|mkv|ts|m2ts|mp4|m4v|flv|vob|mpg|mpeg|iso|mov|wmv|rar|zip|' \
                   'mp3|aac|ogg|wav|dts|ac3|flac'
VIDEO_DETAILS = {
    'year': ur'(?:[Гг]од|[Рр]ік).*?: *?(\d{4})',
    'genre': ur'[Жж]анр.*?:(.*)',
    'director': ur'[Рр]ежисс?[её]р.*?:(.*)',
    'plot': ur'(?:Описание|О фильме|Сюжет|О чем|О сериале).*?:\n?(.*)',
    'cast': ur'(?:[ВвУу] ролях|[Аа]кт[ео]р[ыи]).*?:(.*)',
    'rating': ur'IMD[Bb].*?: *?(\d\.\d)',
    }

MediaCategory = namedtuple('MediaCategory', ['name', 'path', 'items'])
MediaList = namedtuple('MediaList', ['media', 'prev', 'next', 'original_id'])
MediaItem = namedtuple('MediaItem', ['title', 'thumb', 'path'])
MediaDetails = namedtuple('MediaDetails', ['title', 'thumb', 'files', 'mp4', 'info'])
MediaFile = namedtuple('MediaFile', ['filename', 'path', 'mirrors'])
ExUaPage = namedtuple('ExUaPage', ['type', 'content'])

plugin = Plugin()
if plugin.hq_posters:
    poster_quality = '400'
else:
    poster_quality = '200'


def get_categories(path):
    """
    Get video categories
    """
    return parse_categories(webclient.load_page(SITE + path))


def parse_categories(web_page):
    """
    Parse media categories list
    """
    parse = re.findall('<b>(.*?)</b></a><p><a href=\'(.*?)\' class=info>(.*?)</a>', web_page)
    listing = []
    for item in parse:
        listing.append(MediaCategory(item[0], item[1], item[2]))
    return listing


def get_media_list(path, page=0, items=25):
    """
    Get the list of media articles
    """
    if int(page) > 0:
        if '?r=' in path or '?s=' in path:
            p = '&p={0}'.format(page)
        else:
            p = '?p={0}'.format(page)
    else:
        p = ''
    if path != '/buffer':
        per = '&per={0}'.format(items)
    else:
        per = ''
    url = SITE + path + p + per
    web_page = webclient.load_page(url)
    return parse_media_list(web_page)


def parse_media_list(web_page):
    """
    Parse a media list page to get the list of videos and navigation links
    """
    # html.parser is faster but does not work properly on Python < 2.7.3
    if sys.version_info[1] >= 7 and sys.version_info[2] >= 3:
        soup = BeautifulSoup(web_page, 'html.parser')
    else:
        soup = BeautifulSoup(web_page, 'html5lib')
    nav_table = soup.find('table', border='0', cellpadding='5', cellspacing='0')
    if nav_table is not None:
        prev_tag = nav_table.find('img', src='/t3/arr_l.gif')
        if prev_tag is not None:
            prev_page = prev_tag.find_previous('a', text=re.compile('\.\.')).text
        else:
            prev_page = None
        next_tag = nav_table.find('img', src='/t3/arr_r.gif')
        if next_tag is not None:
            next_page = next_tag.find_next('a', text=re.compile('\.\.')).text
        else:
            next_page = None
    else:
        prev_page = next_page = None
    content_table = soup.find('table', width='100%', border='0', cellpadding='0', cellspacing='8')
    if content_table is not None:
        media = parse_media_items(content_table)
    else:
        media = []
    original_id_tag = soup.find('input', {'type': 'hidden', 'name': 'original_id'})
    if original_id_tag is not None:
        original_id = original_id_tag['value']
    else:
        original_id = None
    return MediaList(media, prev_page, next_page, original_id)


def parse_media_items(content_table):
    """
    Parse the list of media
    """
    content_cells = content_table.find_all('td')
    listing = []
    for content_cell in content_cells:
        try:
            link_tag = content_cell.find('a')
            if link_tag is not None:
                image_tag = content_cell.find('img')
                if image_tag is not None:
                    thumb = image_tag['src'][:-3] + poster_quality
                    title = image_tag['alt']
                else:
                    thumb = ''
                    title = link_tag.text
                listing.append(MediaItem(title, thumb, link_tag['href']))
        except TypeError:
            pass
    return listing


def get_media_details(path):
    """
    Get video details.
    """
    web_page = webclient.load_page(SITE + path)
    return parse_media_details(web_page)


def _is_descr_table(tag):
    return (
        tag.name == 'table' and
        tag.has_attr('width') and
        tag.has_attr('cellpadding') and
        tag.has_attr('cellspacing') and
        tag.has_attr('border') and
        not tag.has_attr('height')
    )


def parse_media_details(web_page):
    """
    Parse a video item page to extract as much details as possible
    """
    soup = BeautifulSoup(web_page, 'html5lib')
    # Try to extract tags with links to media files
    media_tags = soup.find_all('a',
                                title=re.compile('^(.+\.(?:{0}))$'.format(MEDIA_EXTENSIONS), re.IGNORECASE),
                                rel='nofollow')
    # Try to use html.parser if no tags found (probably of malformed html).
    # This is only for Python 2.7.3 and above because on lower versions
    # html.parser does not work properly.
    if not media_tags and sys.version_info[1] >= 7 and sys.version_info[2] >= 3:
        soup = BeautifulSoup(web_page, 'html.parser')
        media_tags = soup.find_all('a',
                                   title=re.compile('^(.+\.(?:{0}))$'.format(MEDIA_EXTENSIONS), re.IGNORECASE),
                                   rel='nofollow')
    # Extract mediafiles
    files = []
    for media_tag in media_tags:
        mirror_tags = media_tag.find_next('td', class_='small').find_all('a', rel='nofollow', title=True)
        mirrors = []
        if mirror_tags:
            for mirror_tag in mirror_tags:
                mirrors.append(mirror_tag['href'])
        files.append(MediaFile(media_tag.text, media_tag['href'], mirrors))
    # Extract ligtweight mp4 videos
    mp4_regex = re.compile('player_list = \'(.*)\';')
    var_player_list = soup.find('script', text=mp4_regex)
    if var_player_list is not None:
        mp4 = []
        for mp4_item in ast.literal_eval('[' + re.search(mp4_regex, var_player_list.text).group(1) + ']'):
            mp4.append(mp4_item['url'])
    else:
        mp4 = None
    # Extract title and poster
    title = soup.find('h1').text
    thumb_tag = soup.find('link', rel='image_src')
    if thumb_tag is not None:
        thumb = thumb_tag['href'][:-3]
    else:
        thumb = ''
    # Extract description if possible
    info = {}
    descr_table_tag = soup.find(_is_descr_table)
    if descr_table_tag is not None:
        try:
            # Clean the media item description
            brs = descr_table_tag.find_all('br')
            for br in brs:
                br.replace_with('\n')
            ps = descr_table_tag.find_all('p')
            text = u''
            for p in ps:
                text += p.text + '\n'
            # Extract info
            for detail, regex in VIDEO_DETAILS.iteritems():
                match = re.search(regex, text)
                if match is not None:
                    info[detail] = match.group(1).lstrip()
            if not info.get('plot'):
                info['plot'] = text
        except AttributeError:  # May throw on malformed html
            pass
    return MediaDetails(title, thumb, files, mp4, info)


def detect_page_type(path):
    """
    Detect the type of an ex.ua page
    """
    page_type = None
    content = None
    web_page = webclient.load_page(SITE + path)
    if '<table width=100% class=list border=0 cellpadding=0 cellspacing=0 style=\'padding-top: 8px\'>' in web_page:
        page_type = 'media_page'
        content = parse_media_details(web_page)
    elif ('<table width=100% border=0 cellpadding=0 cellspacing=8' in web_page and
              ('<form name=search action=\'/search\'>' in web_page or '<span class=modify_time>' in web_page)):
        page_type = 'media_list'
        content = parse_media_list(web_page)
    elif '<table width=100% border=0 cellpadding=0 cellspacing=8 class=include_0>' in web_page:
        page_type = 'media_categories'
        content = parse_categories(web_page)
    result = ExUaPage(page_type, content)
    plugin.log(str(result))
    return result
