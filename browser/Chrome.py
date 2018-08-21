#!/usr/bin/env python
# -*- coding: utf8 -*-
import pytest
import allure
import os
from time import sleep

from selenium import webdriver


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")


class Chrome:  # chrome based (Chrome, yandex-browser)
    @pytest.allure.step('Open driver session')
    def __init__(self, browser='chrome', version='67.0'):
        self.browser = browser
        chrome_options = webdriver.ChromeOptions()
        webdriver.DesiredCapabilities()
        capabilities = chrome_options.to_capabilities()
        capabilities.update({'env': ["LANG=ru_RU.UTF-8", "LANGUAGE=ru:en", "LC_ALL=ru_RU.UTF-8"],
                             'version': version,
                             'browserName': browser})

        print 'Create Driver session: browser: {}, version: {}'.format(browser, version)
        self.driver = webdriver.Chrome()
        print 'Session ID: {}'.format(self.driver.session_id)
        self.driver.set_script_timeout(10)

    def __enter__(self):
        return self

    def getConsoleLog(self):
        print self.driver.get_log('browser')

    @pytest.allure.step('Open url {1}')
    def openUrl(self, url, timeout=10):
        self.driver.get(url)
        i = 0
        print "Checking if {} page is loaded.".format(self.driver.current_url)
        while i < timeout:
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                break
            else:
                print '.'
                i += 1
                sleep(1)

    def SwitchToDefaultFrame(self):
        self.driver.switch_to.default_content()

    @pytest.allure.step('Get Screenshot')
    def getPageFullScreenshot(self):
        print 'Set max window size to get full screenshot'
        self.SwitchToDefaultFrame()
        width = self.driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = self.driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        self.driver.set_window_size(width, height)
        allure.attach(self.driver.get_screenshot_as_png())

    @pytest.allure.step('Close driver session')
    def close(self):
        print 'End session {}'.format(self.driver.session_id)
        self.driver.close()

    def __exit__(self, type, value, traceback):
        if type is None:  # Если исключение не возникло
            print "Исключение не возникло"
        else:  # Если возникло исключение
            print "Value =", value
            return False
        self.close()
