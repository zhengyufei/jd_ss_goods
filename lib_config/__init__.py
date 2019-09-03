from .redis import *

import argparse
import os
import json

from lib_config.mongodb import load_mongodb


def load_conf():
    """
    解析环境变量(CONFIG_FILE)或命令行参数(-c), 获取配置文件
    manage.py运行的脚本不能通过命令行参数传入配置文件, 规范统一从环境变量中获取配置文件
    需要优先解析环境变量, 因为脚本可能会用-c参数代表其他参数(如数据库表)
    """
    config_file = os.getenv("CONFIG_FILE")
    if not config_file:
        parser = argparse.ArgumentParser(description='configure-jd')
        parser.add_argument('-c', metavar='ConfigFile', type=str, help='config file')
        args, _ = parser.parse_known_args()
        config_file = os.path.abspath(args.c)

    if not config_file:
        print('no config file provided')
        exit(1)
    with open(config_file) as f:
        env = json.load(f, encoding='utf-8')
    return env


env = load_conf()
load_redis(env['redis'])
load_mongodb(env['mongodb'])

LOG_PATH = env['log']['path']
LOG_LEVEL = env['log']['level']
LOG_PREFIX = env['server_name']
