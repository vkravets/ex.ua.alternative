# -*- coding: utf-8 -*-
# Name:        parser
# Author:      Roman V.M.
# Created:     04.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import re
import ast
from bs4 import BeautifulSoup
import webbot
from logger import log as __log__

##def __log__(var_name='', variable=None):
##        print var_name + ': ', variable

SITE = 'http://www.ex.ua'
loader = webbot.WebBot()

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
    CAT_PATTERN = '<b>(.*?)</b></a><p><a href=\'(.*?)\' class=info>(.*?)</a>'
    parse = re.findall(CAT_PATTERN, web_page, re.UNICODE)
    categories = []
    for item in parse:
        category = {}
        category['name'] = item[0]
        category['url'] = item[1]
        category['items#'] = item[2]
        categories.append(category)
    return categories


def get_videos(category_url, page=0, pages='25'):
    """
    Get the list of videos from categories.
    Return the dictionary:
        videos: the list of videos, each item is a dict of the following properties:
            thumb
            url
            title
        prev: numbers of previous pages, if any.
        next: numbers of next pages, if any.
    """
    if page > 0:
        pageNo = '&p=' + str(page)
    else:
        pageNo = ''
    if  '?r=' not in category_url:
        page_count = ''
    else:
        page_count = '&per=' + pages
    web_page = loader.get_page(SITE + category_url + pageNo + page_count)
    __log__('exua_parser.get_videos; web_page', web_page)
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
                    thumb = image_tag['src'][:-3] + '200'
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
    return {'videos': videos, 'prev': prev_page, 'next': next_page}


def get_video_details(url):
    """
    Get video details.
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
    details = {}
    details['videos'] = []
    web_page = loader.get_page(SITE + url)
    __log__('exua_parser.get_video_details; web_page', web_page)
    soup = BeautifulSoup(web_page)
    if u'Артисты @ EX.UA' in soup.find('title').text:
        details['title'] = soup.find('meta', {'name': 'title'})['content']
        details['plot'] = soup.find('div', id="content_page").get_text(' ', strip=True)
        details['thumb'] = soup.find('link', rel='image_src')['href']
        video_url = re.search('playlist: \[ \"(.*?)\" \]',
                        soup.find('script', {'type':'text/javascript'}, text=re.compile('playlist')).text).group(1)
        details['videos'].append({'filename': 'Video', 'url': video_url})
        details['year'] = details['genre'] = details['director'] = details['duration'] = details['cast'] = ''
        details['flvs'] = []
    else:
        details['title'] = soup.find('h1').text
        thumb_tag = soup.find('link', rel='image_src')
        if thumb_tag is not None:
            details['thumb'] = thumb_tag['href']
        else:
            details['thumb'] = ''
        search_video = soup.find_all('a',
                        title=re.compile('(.*\.(?:avi|mkv|ts|m2ts|mp4|m4v|flv|vob|mpg|mpeg|iso|mov|wmv|rar|zip|'
                                                'AVI|MKV|TS|M2TS|MP4|M4V|FLV|VOB|MPG|MPEG|ISO|MOV|WMV|RAR|ZIP)(?!.))'))
        for video in search_video:
            item = {}
            item['filename'] = video.text
            item['url'] = video['href']
            details['videos'].append(item)
        search_script = soup.find_all('script')
        for script in search_script:
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
            search_detail =  soup.find(text=re.compile(DETAILS[detail][0], re.UNICODE))
            if search_detail is not None:
                detail_text = re.search(DETAILS[detail][1], search_detail, re.UNICODE)
                if detail_text is not None:
                    text = detail_text.group(1)
                if detail_text is None or len(text) <= 3:
                    while True:
                        next_= search_detail.find_next(text=True)
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
            plot_tags = soup.find('span', {'class': 'modify_time'})
            if plot_tags is not None:
                details['plot'] = plot_tags.find_next('p').get_text(' ', strip=True).replace(u'смотреть онлайн', '')
    return details


def main():
    """
    For testing only.
    """
    videos = get_video_details('/76311211?r=2,23775')
    print videos

if __name__ == '__main__':
    main()
