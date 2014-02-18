# -*- coding: utf-8 -*-
# Name:        webbot
# Author:      Roman V.M.
# Created:     18.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import os
import urllib
import urllib2
import cookielib
import re
import xbmc

LOGIN_URL = 'https://www.ex.ua/login'
HEADERS = [ ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0'),
            ('Accept-Charset', 'UTF-8'),
            ('Host', 'www.ex.ua'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Connection', 'keep-alive')]
COOKIE_DIR = 'special://masterprofile/addon_data/plugin.video.ex.ua.aternative'


class WebBot(object):

    def __init__(self):
        self.cookie_file = os.path.join(xbmc.translatePath(COOKIE_DIR), '.cookies')
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_file)
        if not os.path.exists(self.cookie_file):
            self.cookie_jar.save()
        self.cookie_jar.revert()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        self.opener.addheaders = HEADERS

    def get_page(self, url, data=None):
        try:
            session = self.opener.open(url, data)
        except urllib2.URLError:
            web_page = ''
        else:
            self.cookie_jar.save()
            web_page = session.read().decode('utf-8')
            session.close()
        return web_page

    def is_logged_in(self):
        for cookie in self.cookie_jar:
            if cookie.name == 'ukey':
                logged_in = True
                break
        else:
            logged_in = False
        return logged_in

    def check_captcha(self):
        web_page = self.get_page(LOGIN_URL)
        captcha_group = re.search('<img src=\'(\/captcha\?captcha_id=.+?)\'', web_page, re.UNICODE)
        if captcha_group is not None:
            captcha_file = os.path.join(xbmc.translatePath('special://temp'), 'captcha.png')
            urllib.urlretrieve('http://www.ex.ua' + captcha_group(0), captcha_file)
        else:
            captcha_file = ''
        return captcha_file

def main():
    pass

if __name__ == '__main__':
    main()
