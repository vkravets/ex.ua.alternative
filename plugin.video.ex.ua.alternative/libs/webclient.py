# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence: GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import cPickle as pickle
import requests
from simpleplugin import Plugin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Accept-Charset': 'UTF-8',
    'Accept': 'text/html',
    }
plugin = Plugin()
cookies_file = os.path.join(plugin.config_dir, 'cookies.pcl')


def load_page(url, post_data=None):
    """
    Load a webpage from ex.ua by given url
    """
    session = requests.Session()
    session.headers = HEADERS.copy()
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as fo:
            session.cookies = pickle.load(fo)
    if post_data is not None:
        resp = session.post(url, data=post_data)
    else:
        resp = session.get(url)
    with open(cookies_file, 'wb') as fo:
        pickle.dump(session.cookies, fo)
    return resp.text
