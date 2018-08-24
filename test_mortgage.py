# -*- coding: utf8 -*-
import pytest
import requests
import random
import string
import uuid
import datetime
from urlparse import urljoin, urlunparse

HOST = 'mortgage.strahovka.ru'
BASEPATH = '/api/v1/'
SCHEMES = 'https'

BASE_REQUEST_URL = urlunparse((SCHEMES, HOST, BASEPATH))


# генератор запроса
def get_request(dict_updater=()):
    birth_date = (datetime.datetime.now() + datetime.timedelta(
                 days=-(18 + random.randint(0, 65 - 18)) * 365))

    def random_str(length=0, sample=u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя ', max_len=400):
        return "".join(random.choice(sample) for _ in xrange(length if length else random.randint(1, max_len)))

    request = {
        "mortgageRequestId": str(uuid.uuid4()),
        "customer": {
            "partnerCustomerId": random_str(sample=string.printable),
            "customerName": {
                "lastName": random_str(),
                "firstName": random_str(),
                "middleName": ""
            },
            "birthDate": birth_date.strftime("%d/%m/%Y"),
            "idDocument": {
                "documentType": '21',  # 21 для Паспорта РФ
                "series": random_str(4, string.digits),
                "number": random_str(6, string.digits),
                "issueDate": (birth_date + datetime.timedelta(days=(14 + random.random()) * 365)).strftime("%d/%m/%Y"),
                "issuedBy": random_str(),
                "departmentCode": ""
            }
        },
        "loanAmount": {
            "amount": int(random_str(string.digits)),
            "currency": "RUB"
        }
    }
    request.update(dict_updater)
    return request


@pytest.mark.parametrize('request', [get_request(),  # рандомно заполненные обязательные поля
                                     get_request({"customer": {"customerName": {"middleName": "kjnvsdmckjknlsknkfnkn"}}}),  # заполнены необязательные поля
                                     get_request({"customer": {"idDocument": {"departmentCode": "olololo"}}}),
                                     get_request({'loanAmount': {'currency': 'USD'}}),  # Валюта займа USD
                                     ])
def test_positive(request):
    """
    Базовое первоначальное создание заявки с верными данными
    """
    response = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    assert 201 == response.status_code


# TODO: надо подумать над генератором чтоб по шаблону сам обходил поля и делал все эти базовые тесты
@pytest.mark.parametrize('request', [{},  # вообще пустой запрос
                                     {'mortgageRequestId': "123"},  # одно поле есть
                                     {'customer': {}},
                                     {'loanAmount': {}},
                                     get_request({'mortgageRequestId': ""}),  # не заполнены обязательные поля
                                     get_request({'customer': {}}),
                                     get_request({'loanAmount': {}}),
                                     get_request({'customer': {}}),
                                     get_request({'customer': {"partnerCustomerId": ""}}),
                                     get_request({'customer': {"birthDate": ""}}),
                                     get_request({'customer': {"customerName": {}}}),
                                     get_request({'customer': {"idDocument": {}}}),
                                     get_request({'customer': {"idDocument": {"documentType": ""}}}),
                                     get_request({'customer': {"idDocument": {"series": ""}}}),
                                     get_request({'customer': {"idDocument": {"number": ""}}}),
                                     get_request({'customer': {"idDocument": {"issueDate": ""}}}),
                                     get_request({'customer': {"idDocument": {"issuedBy": ""}}}),
                                     get_request({'mortgageRequestId': 0}),  # в полях не те типы данных (опять по каждому полю)
                                     get_request({'loanAmount': {'amount': -112}}),  # отрицательная сумма займа
                                     get_request({'loanAmount': {'amount': '112'}}),  # сумма займа текстовая с числом
                                     get_request({'loanAmount': {'amount': 112.5}}),  # сумма займа c плавающей точкой
                                     get_request({'loanAmount': {'amount': 'ololo'}}),  # сумма займа текстовая, внутри не число
                                     get_request({'loanAmount': {'amount': 'ololo'}}),  # сумма займа текстовая, внутри не число
                                     get_request({'loanAmount': {'currency': 'OLOLO'}}),  # Валюта займа не по iso
                                     get_request({'customer': {"birthDate": "01/01/1999",
                                                               "idDocument": {"issueDate": "01/01/1998"}}}),  # паспорт выдан раньше дня рождения
                                     ])
def test_negative(request):
    response = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    assert 400 == response.status_code


# повторный запрос со сменой имени
def test_double_request_with_FIO_change():
    request = get_request()
    response = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    response_second = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request.update({'customer': {"customerName": {
                                                                                                           "lastName": request['customer']['customerName']['lastName'] + ' новый',
                                                                                                           "firstName": request['customer']['customerName']['firstName'] + ' новый',
                                                                                                           "middleName": ""
                                                                                                           }}}),
                                    headers={'content-type': 'application/json'})
    assert response_second == response


# повторный запрос
def test_double_request_with_no_changes():
    request = get_request()
    response = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    response_second = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                                    headers={'content-type': 'application/json'})
    assert response_second == response


# повторный запрос со сменой id
def test_already_requested_with_new_id():
    request = get_request()
    response = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    response_second = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request.update({'mortgageRequestId': str(uuid.uuid4())}),
                                    headers={'content-type': 'application/json'})
    assert response_second != response
