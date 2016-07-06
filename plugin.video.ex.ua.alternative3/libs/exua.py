# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence: GPL v.3: http://www.gnu.org/copyleft/gpl.html

import re
from collections import namedtuple
from bs4 import BeautifulSoup
from simpleplugin import Plugin
import webclient

SITE = 'http://www.ex.ua'

VideoCategory = namedtuple('VideoCategory', ['name', 'path', 'items'])
VideoList = namedtuple('VideoList', ['videos', 'prev', 'next'])
VideoItem = namedtuple('VideoItem', ['title', 'thumb', 'path'])

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


def parse_categories(html):
    """
    Parse video categories list
    """
    parse = re.findall('<b>(.*?)</b></a><p><a href=\'(.*?)\' class=info>(.*?)</a>', html, re.UNICODE)
    for item in parse:
        yield VideoCategory(item[0], item[1], item[2])


def get_video_list(path, page=0, pages=25):
    """
    Get the list of video articles
    """
    if int(page) > 0:
        if '?r=' in path or '?s=' in path:
            p = '&p={0}'.format(page)
        else:
            p = '?p={0}'.format(page)
    else:
        p = ''
    if path != '/buffer':
        per = '&per={0}'.format(pages)
    else:
        per = ''
    url = SITE + path + p + per
    web_page = webclient.load_page(url)
    return parse_videos(web_page)


def parse_videos(web_page):
    """
    Parse a video list page to get the list of videos and navigation links
    """
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
        videos = parse_video_list(content_table)
    else:
        videos = []
    return VideoList(videos, prev_page, next_page)


def parse_video_list(content_table):
    """
    Parse the list of videos
    """
    content_cells = content_table.find_all('td')
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
                yield VideoItem(title, thumb, link_tag['href'])
        except TypeError:
            pass
