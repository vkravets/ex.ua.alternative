# -*- coding: utf-8 -*-
# Name:        login_widow
# Author:      Roman V.M.
# Created:     18.02.2014
# Licence:     GPL v.3: http://www.gnu.org/copyleft/gpl.html

import pyxbmct.addonwindow as pyxbmct


class LoginWindow(pyxbmct.AddonDialogWindow):
    """ Login window class """

    def __init__(self, username='', password='', captcha=''):
        """ Class constructor """
        super(LoginWindow, self).__init__()
        self.setGeometry(500, 300, 5, 2)
        self.setWindowTitle(u'Вход на ex.ua')
        self.username = username
        self.password = password
        self.captcha = captcha
        self.captcha_text = ''
        self.captcha_present = len(self.captcha)
        self.login_cancelled = True
        self.set_controls()
        self.set_navigation()
        self.doModal()

    def set_controls(self):
        """ Set UI controls """
        username_label = pyxbmct.Label(u'Имя пользователя:')
        self.placeControl(username_label, 0, 0)
        self.username_entry = pyxbmct.Edit(u'Введите имя пользователя')
        self.placeControl(self.username_entry, 0, 1)
        self.username_entry.setText(self.username)
        password_label = pyxbmct.Label(u'Пароль:')
        self.placeControl(password_label, 1, 0)
        self.password_entry = pyxbmct.Edit(u'Введите пароль', isPassword=True)
        self.placeControl(self.password_entry, 1, 1)
        self.password_entry.setText(self.password)
        self.captcha_image = pyxbmct.Image(self.captcha)
        self.placeControl(self.captcha_image, 2, 0, rowspan=2)
        self.captcha_image.setVisible(self.captcha_present)
        captcha_label = pyxbmct.Label(u'Текст на картинке:')
        self.placeControl(captcha_label, 2, 1)
        captcha_label.setVisible(self.captcha_present)
        self.captcha_entry = pyxbmct.Edit(u'Введите текст на картинке')
        self.placeControl(self.captcha_entry, 3, 1)
        self.captcha_entry.setVisible(self.captcha_present)
        self.cancel_button = pyxbmct.Button(u'Отмена')
        self.placeControl(self.cancel_button, 4, 0)
        self.connect(self.cancel_button, self.close)
        self.login_button = pyxbmct.Button(u'Войти')
        self.placeControl(self.login_button, 4, 1)
        self.connect(self.login_button, self.login)

    def set_navigation(self):
        """ Set navigation rules for controls """
        self.username_entry.controlUp(self.login_button)
        self.username_entry.controlDown(self.password_entry)
        self.password_entry.controlUp(self.username_entry)
        if self.captcha_present:
            self.password_entry.controlDown(self.captcha_entry)
            self.captcha_entry.controlUp(self.password_entry)
            self.captcha_entry.controlDown(self.login_button)
            self.login_button.setNavigation(self.captcha_entry, self.username_entry, self.cancel_button, self.cancel_button)
            self.cancel_button.setNavigation(self.captcha_entry, self.username_entry, self.login_button, self.login_button)
        else:
            self.password_entry.controlDown(self.login_button)
            self.login_button.setNavigation(self.password_entry, self.username_entry, self.cancel_button, self.cancel_button)
            self.cancel_button.setNavigation(self.password_entry, self.username_entry, self.login_button, self.login_button)
        self.setFocus(self.username_entry)

    def login(self):
        """ Login user """
        self.login_cancelled = False
        self.username = self.username_entry.getText()
        self.password = self.password_entry.getText()
        if self.captcha_present:
            self.captcha_text = self.captcha_entry.getText()
        self.close()

    def close(self):
        """ Cancel login """
        if self.login_cancelled:
            self.username = ''
            self.password = ''
            self.captcha_text = ''
        super(LoginWindow, self).close()


if __name__ == '__main__':
    pass
