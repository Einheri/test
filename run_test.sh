#!/bin/sh
py.test --alluredir=./allure_res/ ./test_converter.py
allure generate ./allure_res/ --clean
allure open