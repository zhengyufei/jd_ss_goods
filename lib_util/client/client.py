import time as base_time
import requests

from lib_config.vo import load_inner_vo_data
from .const import *


class BaseException(Exception):
    def __init__(self, data, flag="third"):
        err = '{} error: code {}, msg {}'.format(flag, data['code'], data['message'])
        self.data = data
        Exception.__init__(self, err)


class BaseClient:
    def __init__(self, name):
        from lib_config import env
        from lib_config.log.log import logging

        self.remote_server = env['client'][name]
        self.log = logging.getLogger(name)
        self.flag = name
        self.exception = BaseException

    def raise_error(self, data):
        if data['code'] != CODE_OK:
            raise BaseException(data, self.flag)

    def get_url(self, path):
        return self.remote_server + path

    def get(self, path, params=None, **kwargs):
        url = self.get_url(path)
        start_ts = base_time.time()
        resp = requests.get(url=url, params=params, **kwargs)

        elapse_seconds = base_time.time() - start_ts
        self.log.info("{} get {}, params: {}, kwargs {}, elapse {}s".format(
            self.flag, url, params, kwargs, elapse_seconds))
        if resp.status_code != 200:
            self.log.error("{} get {}, params: {}, kwargs {}, status: {} response {}".format(
                self.flag, url, params, kwargs, resp.status_code, resp.text))
            raise Exception("{} get {} status_code {}".format(self.flag, url, resp.status_code))

        data = load_inner_vo_data(resp.text)
        self.log.info("{} resp {}".format(self.flag, data))
        self.raise_error(data)

        return data

    def post(self, path, data=None, json=None, **kwargs):
        url = self.get_url(path)
        start_ts = base_time.time()
        resp = requests.post(url, data=data, json=json, **kwargs)
        elapse_seconds = base_time.time() - start_ts
        self.log.info("{} post {}, data: {}, json: {}, kwargs {}, elapse {}s".format(
            self.flag, url, data, json, kwargs, elapse_seconds))
        if resp.status_code != 200:
            self.log.error("{} post {}, data: {}, json: {}, kwargs {}, status: {} response {}".format(
                self.flag, url, data, json, kwargs, resp.status_code, resp.text))
            raise Exception("{} get {} status_code {}".format(self.flag, url, resp.status_code))

        self.log.info("{} resp text {}".format(self.flag, resp.text))
        data = load_inner_vo_data(resp.text)
        self.log.info("{} resp {}".format(self.flag, data))
        self.raise_error(data)

        return data

    def decorator_retry(self, retry=3):
        def decorator(func):
            def wrapper(obj, *args, **kwargs):
                n = 0
                while True:
                    n += 1
                    try:
                        return func(obj, *args, **kwargs)
                    except BaseException as e:
                        self.log.error("{} {} {} {} failed {} {}".format(
                            func, obj, args, kwargs, e, n
                        ))
                        if n > retry:
                            raise e
                        else:
                            continue
            return wrapper
        return decorator
