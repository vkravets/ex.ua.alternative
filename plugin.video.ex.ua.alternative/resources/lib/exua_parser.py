# -*- coding: utf-8 -*-
# Name:        parser
# Author:      Roman V.M.
# Created:     04.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import re
import ast
from bs4 import BeautifulSoup

if __name__ == '__main__':
    # This is for testing purposes when the module is run from console.
    import urllib2

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
    from webloader import WebLoader
    from logger import log as __log__
    _addon = xbmcaddon.Addon()
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
    web_page = loader.get_page('http://www.ex.ua/ru/video')
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
    CAT_PATTERN = '<b>(.*?)</b></a><p><a href=\'(.*?)\' class=info>(.*?)</a>'
    parse = re.findall(CAT_PATTERN, web_page, re.UNICODE)
    categories = []
    for item in parse:
        categories.append({'name': item[0], 'url': item[1], 'items#': item[2]})
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
    if page > 0:
        pageNo = '&p=' + str(page)
    else:
        pageNo = ''
    if '?r=' in path or 'search' in path:
        page_count = '&per=' + pages
    else:
        page_count = ''
    web_page = page_loader.get_page(SITE + path + pageNo + page_count)
    __log__('exua_parser.get_videos; web_page', web_page)
    return parse_videos(web_page)


def parse_videos(web_page):
    """
    Parse a list of videos.
    Return the dictionary:
        videos: the list of videos, each item is a dict of the following properties:
            thumb
            url
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
                url = link_tag['href']
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
                videos.append({'thumb': thumb, 'url': url, 'title': title})
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
        video_url = re.search('playlist: \[ \"(.*?)\" \]',
                          soup.find('script', {'type': 'text/javascript'}, text=re.compile('playlist')).text).group(1)
        details['videos'].append({'filename': 'Video', 'url': video_url})
        details['year'] = details['genre'] = details['director'] = details['duration'] = details['cast'] = ''
        details['flvs'] = []
    else:
        details['title'] = soup.find('h1').text
        thumb_tag = soup.find('link', rel='image_src')
        if thumb_tag is not None:
            details['thumb'] = thumb_tag['href'][:-3] + IMG_QUALITY
        else:
            details['thumb'] = ''
        video_tags = soup.find_all('a', title=re.compile(
            '(.*\.(?:avi|mkv|ts|m2ts|mp4|m4v|flv|vob|mpg|mpeg|iso|mov|wmv|rar|zip|'
            'AVI|MKV|TS|M2TS|MP4|M4V|FLV|VOB|MPG|MPEG|ISO|MOV|WMV|RAR|ZIP)(?!.))'))
        for video_tag in video_tags:
            # mirror_tags = video_tag.find_next('td', {'class': 'small'}).find_all('a', {'rel': 'nofollow', 'title': True})
            # mirrors = []
            # if mirror_tags:
            #     for mirror_tag in mirror_tags:
            #         mirrors.append({'name': mirror_tag.text, 'path': mirror_tag['href']})
            details['videos'].append({'filename': video_tag.text, 'url': video_tag['href']})
        for script in soup.find_all('script'):
            var_player_list = re.search('player_list = \'(.*)\';', script.text)
            if var_player_list is not None:
                details['flvs'] = []
                for flv_item in ast.literal_eval('[' + var_player_list.group(1) + ']'):
                    details['flvs'].append(flv_item['url'])
                break
        else:
            details['flvs'] = ''
        DETAILS = {
            'year': [u'(?:[Гг]од|[Рр]ік).*', u'(?:[Гг]од|[Рр]ік).*?: *?([0-9]{4})', '([0-9]{4})'],
            'genre': [u'[Жж]анр.*', u'[Жж]анр.*?: *?(.*)', '.*'],
            'director': [u'[Рр]ежисс?[её]р.*', u'[Рр]ежисс?[её]р.*?: *?(.*)', '(.*)'],
            'duration': [u'Продолжительность.*', u'Продолжительность.*?: *?(.*)', '(.*)'],
            'plot': [u'(?:Описание|О фильме|Сюжет|О чем|О сериале).*',
                     u'(?:Описание|О фильме|Сюжет|О чем|О сериале).*?: *?(.*)', '(.*)'],
            'cast': [u'[ВвУу] ролях.*', u'[ВвУу] ролях.*?: *?(.*)', '.*'],
        }
        for detail in DETAILS.keys():
            search_detail = soup.find(text=re.compile(DETAILS[detail][0], re.UNICODE))
            if search_detail is not None:
                detail_text = re.search(DETAILS[detail][1], search_detail, re.UNICODE)
                if detail_text is not None:
                    text = detail_text.group(1)
                if detail_text is None or len(text) <= 3:
                    while True:
                        next_ = search_detail.find_next(text=True)
                        text_group = re.search(DETAILS[detail][2], next_, re.UNICODE)
                        if text_group is not None:
                            text = text_group.group(0)
                        else:
                            text = ''
                        if len(text) > 3:
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
                        text += next_tag.get_text('\n', strip=True)
                        prev_tag = next_tag
                details['plot'] = text.replace(u'смотреть онлайн', '')
    __log__('exua_parser.get_videos; parse_video_details', details)
    return details


def check_page(path):
    web_page = loader.get_page(SITE + path)
    try:
        if re.search(u'Файлы:', web_page, re.UNICODE) is not None:
            page_type = 'video_page'
            contents = parse_video_details(web_page)
            raise RuntimeError
        elif re.search(u'Видео на других языках', web_page, re.UNICODE) is not None:
            page_type = 'categories'
            contents = parse_categories(web_page)
            raise RuntimeError
        elif re.search('<table width=100%.+?cellspacing=8', web_page, re.UNICODE) is not None:
            page_type = 'video_list'
            contents = parse_videos(web_page)
            raise RuntimeError
        else:
            page_type = 'unknown'
            contents = None
    except RuntimeError:
        pass
    __log__('exua_parser.check_page; page_type', page_type)
    __log__('exua_parser.check_page; contents', contents)
    return page_type, contents

if __name__ == '__main__':
    pass
