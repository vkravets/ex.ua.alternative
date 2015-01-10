# -*- coding: utf-8 -*-
# Name:        parser
# Author:      Roman V.M.
# Created:     04.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import re
import ast
import urllib2
from bs4 import BeautifulSoup
from constants import MEDIA_EXTENSIONS, VIDEO_DETAILS


if __name__ == '__main__':
    # This is for testing purposes when the module is run from console.

    IMG_QUALITY = '200'

    class WebLoader(object):
        """ WebLoader class for testing purposes only """
        def get_page(self, url):
            """
            Load a web-page with provided url.
            Return a loaded page or an empty string in case of a network error.
            """
            request = urllib2.Request(url, None,
                              {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
                              'Host': SITE[7:],
                              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                              'Accept-Charset': 'UTF-8'})
            try:
                session = urllib2.urlopen(request)
            except urllib2.URLError:
                page = ''
            else:
                page = session.read().decode('utf-8')
                session.close()
            return page

    def __log__(var_name='', variable=None):
        pass

else:  # If the module is imported during normal plugin run within XBMC.
    import xbmcaddon
    from webloader import WebLoader, Opener
    from logger import log as __log__
    _addon = xbmcaddon.Addon()
    google_icon = os.path.join(_addon.getAddonInfo('path'), 'resources', 'icons', 'google.png')
    if _addon.getSetting('hq_posters') == 'true':
        IMG_QUALITY = '400'
    else:
        IMG_QUALITY = '200'

SITE = 'http://www.ex.ua'
loader = WebLoader()


def get_categories():
    """
    Get the list of video categories.
    Return the list of caterory properies:
    name
    url
    items# (items count)
    """
    web_page = loader.get_page('http://www.ex.ua/ru/video?per=24')
    __log__('exua_parser.get_categories; web_page', web_page)
    return parse_categories(web_page)


def parse_categories(web_page):
    """
    Parse categories page.
    Return the list of caterory properies:
    name
    url
    items# (items count)
    """
    parse = re.findall('<b>(.*?)</b></a><p><a href=\'(.*?)\' class=info>(.*?)</a>', web_page, re.UNICODE)
    categories = []
    for item in parse:
        categories.append({'name': item[0], 'path': item[1], 'items#': item[2]})
    __log__('exua_parser.get_categories; categories', categories)
    return categories


def get_videos(path, page_loader=loader, page=0, pages='25'):
    """
    Get the list of videos from categories.
    Return the dictionary:
        videos: the list of videos, each item is a dict of the following properties:
            thumb
            path
            title
        prev: numbers of previous pages, if any.
        next: numbers of next pages, if any.
    """
    if 'www.google.com.ua' in path:
        start = ''
        if page > 0:
            start = '&start={0}'.format(10 * page)
        url = path + start
        results = google_search(url)
    else:
        if page > 0:
            if '?r=' in path or '?s=' in path:
                p = '&p='
            else:
                p = '?p='
            pageNo = p + str(page)
        else:
            pageNo = ''
        if path != '/buffer':
            page_count = '&per={0}'.format(pages)
        else:
            page_count = ''
        url = SITE + path + pageNo + page_count
        web_page = page_loader.get_page(url)
        results = parse_videos(web_page)
        __log__('exua_parser.get_videos; web_page', web_page)
    __log__('exua_parser.get_videos; url', url)
    return results


def parse_videos(web_page):
    """
    Parse a list of videos.
    Return the dictionary:
        videos: the list of videos, each item is a dict of the following properties:
            thumb
            path
            title
        prev: numbers of previous pages, if any.
        next: numbers of next pages, if any.
    """
    soup = BeautifulSoup(web_page)
    videos = []
    content_table = soup.find('table', cellspacing='8')
    if content_table is not None:
        content_cells = content_table.find_all('td')
        for content_cell in content_cells:
            try:
                link_tag = content_cell.find('a')
                path = link_tag['href']
                image_tag = content_cell.find('img')
                if image_tag is not None:
                    thumb = image_tag['src'][:-3] + IMG_QUALITY
                    title = image_tag['alt']
                else:
                    thumb = ''
                    title = link_tag.text
            except TypeError:
                continue
            else:
                videos.append({'thumb': thumb, 'path': path, 'title': title})
        nav_table = soup.find('table', cellpadding='5')
        if nav_table is not None:
            prev_tag = nav_table.find('img', alt=re.compile(u'предыдущую', re.UNICODE))
            if prev_tag is not None:
                prev_page = prev_tag.find_previous('a', text=re.compile(u'\.\.')).text
            else:
                prev_page = ''
            next_tag = nav_table.find('img', alt=re.compile(u'следующую', re.UNICODE))
            if next_tag is not None:
                next_page = next_tag.find_next('a', text=re.compile(u'\.\.')).text
            else:
                next_page = ''
        else:
            prev_page = next_page = ''
    else:
        prev_page = next_page = []
    result = {'videos': videos, 'prev': prev_page, 'next': next_page}
    __log__('exua_parser.parse_videos; result', result)
    return result


def get_video_details(path):
    """
    Get video details.
    Return a dictionary with the following properties:
        title
        thumb
        videos [the list of dicts with pairs of 'filename': 'path']
        flvs [the list of LQ .flv videos, if any]
        year
        genre
        director
        duration
        plot
    """
    web_page = loader.get_page(SITE + path)
    __log__('exua_parser.get_video_details; web_page', web_page)
    return parse_video_details(web_page)


def parse_video_details(web_page):
    """
    Parse video details page.
    Return a dictionary with the following properties:
        title
        thumb
        videos [the list of dicts with pairs of 'filename': 'url']
        flvs [the list of LQ .flv videos, if any]
        year
        genre
        director
        duration
        plot
    """
    details = {'videos': []}
    soup = BeautifulSoup(web_page)
    if u'Артисты @ EX.UA' in soup.find('title').text:
        details['title'] = soup.find('meta', {'name': 'title'})['content']
        details['plot'] = soup.find('div', id="content_page").get_text(' ', strip=True)
        details['thumb'] = soup.find('link', rel='image_src')['href'][:-3] + IMG_QUALITY
        video_path = re.search('playlist: \[ \"(.*?)\" \]',
                          soup.find('script', {'type': 'text/javascript'}, text=re.compile('playlist')).text).group(1)
        details['videos'].append({'filename': 'Video', 'path': video_path, 'mirrors': []})
        details['year'] = details['genre'] = details['director'] = details['duration'] = details['cast'] = ''
        details['flvs'] = []
        details['rating'] = ''
    else:
        details['title'] = soup.find('h1').text
        thumb_tag = soup.find('link', rel='image_src')
        if thumb_tag is not None:
            details['thumb'] = thumb_tag['href'][:-3] + IMG_QUALITY
        else:
            details['thumb'] = ''
        video_tags = soup.find_all('a', title=re.compile('(.*\.(?:{0})(?!.))'.format(MEDIA_EXTENSIONS)))
        for video_tag in video_tags:
            mirror_tags = video_tag.find_next('td', {'class': 'small'}).find_all('a', {'rel': 'nofollow', 'title': True})
            mirrors = []
            if mirror_tags:
                for mirror_tag in mirror_tags:
                    mirrors.append((mirror_tag.text, mirror_tag['href']))
            details['videos'].append({'filename': video_tag.text, 'path': video_tag['href'], 'mirrors': mirrors})
        flvs = re.compile('player_list = \'(.*)\';')
        var_player_list = soup.find('script', text=flvs)
        if var_player_list is not None:
            details['flvs'] = []
            for flv_item in ast.literal_eval('[' + re.search(flvs, var_player_list.text).group(1) + ']'):
                details['flvs'].append(flv_item['url'])
        else:
            details['flvs'] = ''
        for detail in VIDEO_DETAILS.keys():
            search_detail = soup.find(text=re.compile(VIDEO_DETAILS[detail][0], re.UNICODE))
            if search_detail is not None:
                detail_text = re.search(VIDEO_DETAILS[detail][1], search_detail, re.UNICODE)
                if detail_text is not None:
                    text = detail_text.group(1)
                if detail_text is None or len(text) <= 3:
                    while True:
                        next_ = search_detail.find_next(text=True)
                        try:
                            text_group = re.search(VIDEO_DETAILS[detail][2], next_, re.UNICODE)
                        except TypeError:
                            text = ''
                            break
                        if text_group is not None:
                            text = text_group.group(0)
                        else:
                            text = ''
                        if len(text) > 2:
                            break
                        else:
                            search_detail = next_
            else:
                text = ''
            details[detail] = text.replace(': ', '')
        if not details['plot']:
            prev_tag = soup.find('span', {'class': 'modify_time'})
            if prev_tag is not None:
                text = ''
                while True:
                    next_tag = prev_tag.find_next()
                    if next_tag.name == 'span':
                        break
                    else:
                        try:
                            text += next_tag.get_text('\n', strip=True)
                            prev_tag = next_tag
                        except AttributeError:
                            break
                details['plot'] = text.replace(u'смотреть онлайн', '')
    __log__('exua_parser.get_videos; parse_video_details', details)
    return details


def check_page(path):
    """
    Check page type by common patterns.
    Return page type and its parsed contents depending on the type.
    """
    page_type = 'unknown'
    contents = None
    __log__('exua_parser.check_page; path', path)
    web_page = loader.get_page(SITE + path)
    __log__('exua_parser.check_page; page', web_page)
    if re.search(u'Файлы:', web_page, re.UNICODE) is not None:
        page_type = 'video_page'
        contents = parse_video_details(web_page)
    elif re.search(u'Видео на других языках', web_page, re.UNICODE) is not None:
        page_type = 'categories'
        contents = parse_categories(web_page)
    elif re.search('<table width=100%.+?cellspacing=8', web_page, re.UNICODE) is not None:
        page_type = 'video_list'
        contents = parse_videos(web_page)
    __log__('exua_parser.check_page; page_type', page_type)
    __log__('exua_parser.check_page; contents', contents)
    return page_type, contents


def google_search(url):
    """
    Search ex.ua videos on Google.com
    :param url: str
    :return: dict
    """
    __log__('exua_parser.google_search; url', url)
    videos = []
    opener = Opener(host='www.google.com.ua', language='uk-ua')
    soup = BeautifulSoup(opener.get_page(url))
    results = soup.find_all('a', {'href': re.compile('^' + SITE)})
    for result in results:
        videos.append({'thumb': google_icon,
                       'path': result['href'].replace(SITE, ''),
                       'title': result.get_text()})
    prev = next_ = ''
    prev_tag = soup.find('span', text=u'Назад')
    if prev_tag is not None:
        prev = '<'
    next_tag = soup.find('span', text=u'Уперед')
    if next_tag is not None:
        next_ = '>'
    return {'videos': videos, 'prev': prev, 'next': next_}


if __name__ == '__main__':
    print parse_video_details(loader.get_page('http://www.ex.ua/80628362?r=2'))
