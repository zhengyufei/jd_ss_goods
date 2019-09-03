from .. import env, LOG_LEVEL, LOG_PATH, LOG_PREFIX


def _handlers(flag):
    return {
        'level': LOG_LEVEL,
        'class': "logging.handlers.WatchedFileHandler",
        'filename': LOG_PATH + LOG_PREFIX + ".{}.log".format(flag),
        'formatter': "simple",
        'encoding': 'utf8',
    }


def _loggers(flag):
    return {
        'handlers': [flag],
        'level': LOG_LEVEL
    }


def _add_server_log(tmp, flag):
    tmp['handlers'][flag] = _handlers(flag)
    tmp['loggers'][flag] = _loggers(flag)


def func_log():
    logging = {
        'version': 1,
        'incremental': False,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': "%(levelname)s %(asctime)s %(pathname)s %(lineno)d \
%(funcName)s \"%(message)s\""
            },
            'simple': {
                'format': "%(levelname)s %(asctime)s \"%(message)s\""
            },
            'raw': {
                'format': "%(asctime)s %(message)s"
            },
        },
        'handlers': {
            'app': {
                'level': LOG_LEVEL,
                'class': "logging.handlers.WatchedFileHandler",
                'filename': LOG_PATH + LOG_PREFIX + ".log",
                'formatter': "verbose",
                'encoding': 'utf8',
            },
            'app_err': {
                'level': "ERROR",
                'class': "logging.handlers.WatchedFileHandler",
                'filename': LOG_PATH + LOG_PREFIX + ".err.log",
                'formatter': "verbose",
                'encoding': 'utf8',
            },
        },
        'loggers': {
            'app': {
                'handlers': ["app", "app_err"],
                'level': LOG_LEVEL,
                'propagate': False
            },
            'app_err': {
                'handlers': ["app", "app_err"],
                'level': LOG_LEVEL,
                'propagate': False
            },
        }
    }

    return logging


LOGGING = func_log()


def get_logger(ll):
    for k in env['client'].keys():
        ll.append(k)

    import logging.config
    for v in ll:
        _add_server_log(LOGGING, v)
    logging.config.dictConfig(LOGGING)
    return logging


logging = get_logger([])
logger = logging.getLogger("app")
