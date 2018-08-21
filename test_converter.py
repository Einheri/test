#!/usr/bin/env python
# -*- coding: utf8 -*-
import pytest
import re

from browser.Chrome import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'http://www.sberbank.ru/ru/quotes/converter'


@pytest.mark.parametrize('summ, curr_in, curr_out', [(10000, 'CNY', 'USD')])
def test_convert_result(summ, curr_in, curr_out):
    with Chrome() as chrome:
        chrome.openUrl(BASE_URL)
        # установим сумму
        summ_elem = chrome.driver.find_element_by_css_selector('input[placeholder="Сумма"]')
        summ_elem.clear()
        summ_elem.send_keys(summ)
        # установим валюту ИЗ которой переводим
        elem = chrome.driver.find_element_by_css_selector('select[name="converterFrom"] + div[class="select"]')
        elem.click()
        curr = elem.find_element_by_xpath("//span[text()='{}']".format(curr_in))
        # chrome.driver.execute_script("arguments[0].scrollIntoView(true);", curr)
        curr.click()
        # установим валюту В которую переводим
        # elem = chrome.driver.find_element_by_css_selector('select[name="converterTo"] + div[class="select"]')
        # elem.click()
        # curr = elem.find_element_by_xpath("./span[text()='{}']".format(curr_out))
        # chrome.driver.execute_script("arguments[0].scrollIntoView(true);", curr)
        # curr.click()
        # кликем Перевод
        rates = chrome.driver.find_element_by_css_selector('button[class="rates-button"]')
        chrome.driver.execute_script("arguments[0].scrollIntoView(true);", rates)
        rates.click()

        WebDriverWait(chrome.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='rates-converter-result__total']")))

        # заскриншотим результат
        chrome.getPageFullScreenshot()
        text = chrome.driver.find_element_by_css_selector('span[class="rates-converter-result__total-to"]').text
        assert re.match('[\d\s,]+?{}'.format(curr_out), text)


# #@pytest.mark.parametrize()
# def test_currancy_change():
#     with Chrome(command_executor=SELENIUM_EXECUTER) as chrome:
#         chrome.openUrl(BASE_URL)
#
#
# #@pytest.mark.parametrize()
# def test_1():
#     with Chrome(command_executor=SELENIUM_EXECUTER) as chrome:
#         chrome.openUrl(BASE_URL)
