# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua
# Licence: GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import cPickle as pickle
import hashlib
import base64
import re
from collections import namedtuple
import requests
from simpleplugin import Plugin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Accept-Charset': 'UTF-8',
    'Accept': 'text/html',
    'Referer': 'http://www.ex.ua/'
    }
LOGIN_URL = 'http://www.ex.ua/login'
CAPTCHA_URL = 'http://www.ex.ua/captcha?captcha_id={0}'

Captcha = namedtuple('Captcha', ['captcha_id', 'image'])

plugin = Plugin()
cookies_file = os.path.join(plugin.config_dir, '__cookies__.pcl')


class CookiesError(Exception):
    pass


def _read_cookies():
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as fo:
            try:
                return pickle.load(fo)
            except (pickle.PickleError, EOFError):
                pass
    raise CookiesError


def load_page(url, post_data=None):
    """
    Load a webpage from ex.ua by given url
    """
    plugin.log('Loading page {0} with post_data {1}'.format(url, post_data))
    session = requests.Session()
    session.headers = HEADERS.copy()
    try:
        session.cookies = _read_cookies()
    except CookiesError:
        pass
    if post_data is not None:
        resp = session.post(url, data=post_data)
    else:
        resp = session.get(url)
    with open(cookies_file, 'wb') as fo:
        pickle.dump(session.cookies, fo)
    page = resp.text
    plugin.log('Page loaded:\n{0}'.format(page.encode('utf-8')))
    return page


def is_logged_in():
    """
    Check if cookies conatain a user ID
    """
    result = False
    try:
        cookie_jar = _read_cookies()
    except CookiesError:
        pass
    else:
        cookies = requests.utils.dict_from_cookiejar(cookie_jar)
        result = 'ukey' in cookies and len(cookies['ukey']) > 1
    return result


def check_captcha():
    """
    Check if there is a captcha on a loging page. Returns a namedtuple
    with 'captcha_id' and 'image' elements.
    """
    web_page = load_page(LOGIN_URL)
    captcha_match = re.search('<img src=\'/captcha\?captcha_id=(.+?)\'', web_page, re.UNICODE)
    if captcha_match is not None:
        captcha_id = captcha_match.group(1)
        captcha = Captcha(captcha_id, CAPTCHA_URL.format(captcha_id))
    else:
        captcha = Captcha('', '')
    plugin.log('Captcha: {0}'.format(captcha))
    return captcha


def login(username, password, remember_user=True, captcha_value='', captcha_id=''):
    """
    Send loging data to ex.ua. Returns True on successful login.
    """
    login_data = {
        'login': username,
        'password': password,
        'flag_permanent': '1' if remember_user else '0',
        'flag_not_ip_assign': '1'
        }
    if captcha_value:
        login_data['captcha_value'] = captcha_value
        login_data['captcha_id'] = captcha_id
    result_page = load_page(LOGIN_URL, login_data)
    return 'i_error.png' not in result_page


def encode(clear):
    key = hashlib.md5(str(True)).hexdigest()
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode(''.join(enc))


def decode(enc):
    key = hashlib.md5(str(True)).hexdigest()
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return ''.join(dec)
