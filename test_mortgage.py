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

    def random_str(length=0, sample='АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя  ', max_len=400):
        return "".join(random.choice(sample) for _ in xrange(length if length else random.randint(1, max_len)))

    request = {
        "mortgageRequestId": str(uuid.uuid4()),
        "customer": {
            "partnerCustomerId": [random.sample(string.printable, random.randint(1, len(string.printable)))],
            "customerName": {
                "lastName": random_str(),
                "firstName": random_str(),
                "middleName": ""
            },
            "birthDate": birth_date.strftime("%d/%m/%Y"),
            "idDocument": {
                "documentType": '21',  # 21 для Паспорта РФ
                "series": "".join(random.sample(string.digits, 4)),
                "number": "".join(random.sample(string.digits, 6)),
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


@pytest.mark.parametrize('request', [get_request(),  # рандомно заполненный обязательные поля поля
                                     get_request()])
def test_pass(request):
    """
    Базовое первоначальное создание заявки с верными данными
    :return:
    """
    responce = requests.post(urljoin(BASE_REQUEST_URL, 'insurances/mortgage'), json=request,
                             headers={'content-type': 'application/json'})
    assert 201 == responce.status_code


# паспорт выдан позже рождения
# не заполнено какое-то поле
def test_negative():
    assert 400
