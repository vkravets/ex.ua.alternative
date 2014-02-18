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
        """
        Class constructor.
        Prepare a cookie jar and a web-page opener.
        """
        self.cookie_file = os.path.join(xbmc.translatePath(COOKIE_DIR), '.cookies')
        self.cookie_jar = cookielib.LWPCookieJar(self.cookie_file)
        if not os.path.exists(self.cookie_file):
            self.cookie_jar.save()
        self.cookie_jar.revert()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        self.opener.addheaders = HEADERS

    def get_page(self, url, data=None):
        """
        Load a web-page with a given url.
        """
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
        """
        Check if the cookie jar has login data. Returns True, if login cookie is present.
        """
        for cookie in self.cookie_jar:
            if cookie.name == 'ukey':
                logged_in = True
                break
        else:
            logged_in = False
        return logged_in

    def check_captcha(self):
        """
        Check if there is a captcha on a loging page. Returns a path to a downloaded captcha,
        if any, or an empty string if ther is none.
        """
        web_page = self.get_page(LOGIN_URL)
        captcha_group = re.search('<img src=\'(\/captcha\?captcha_id=.+?)\'', web_page, re.UNICODE)
        if captcha_group is not None:
            captcha_file = os.path.join(xbmc.translatePath('special://temp'), 'captcha.png')
            urllib.urlretrieve('http://www.ex.ua' + captcha_group(0), captcha_file)
        else:
            captcha_file = ''
        return captcha_file

    def check_error(self, web_page):
        """
        Check if there is an error image on a web-page,
        Returns True if there is no error, and False if the error image is present.
        """
        if re.search('i_error.png', web_page) is None:
            return True
        else:
            return False

    def login(self, username, password, remember_user=True, captcha_text=''):
        """
        Send loging data to ex.ua. Returns True on successful login.
        """
        login_data = [('login', username), ('password', password), ('flag_permanent', int(remember_user)),
                                                                    ('flag_not_ip_assign', 1)]
        if captcha_text:
            login_data.append(('captcha_value', captcha_text))
        post_data = urllib.urlencode(login_data)
        result_page = self.get_page(LOGIN_URL, post_data)
        return check_error(result_page)


def main():
    pass

if __name__ == '__main__':
    main()
