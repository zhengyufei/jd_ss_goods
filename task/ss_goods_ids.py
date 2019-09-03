import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from service.local.shop import get_all_ss_shop_ids
from lib_util.client.client import BaseException
from lib_config.log.log import logger
from lib_config.redis.redis import get_redis
from service.external.sdk.service import ss_sku_ids, ss_sku_infos


REDIS_PREFIX = 'jd_ss_goods:shop:goods_ids:'
R = get_redis('ss')


def task():
    shop_ids = get_all_ss_shop_ids()
    for shop_id in shop_ids:
        _ss_goods_ids(shop_id)


def _get_key(shop_id):
    return REDIS_PREFIX + str(shop_id)


def _ss_goods_ids(shop_id):
    old_redis_total = 0
    index = 0
    n = 0
    err_n = 0
    key = _get_key(shop_id)
    cur_ids = set(int(v) for v in R.smembers(key))
    diff = set()
    # 查询既是乱序又要翻页,n控制次数,index控制偏移
    while True:
        tmp = _ss_goods_ids2(shop_id, index, cur_ids, diff)
        # 连续3次sdk错误break
        if type(tmp) is str:
            err_n += 1
            logger.info("{}: error {}".format(shop_id, tmp))
            if err_n >= 3:
                break
            else:
                continue
        else:
            err_n = 0

        b, total, cur_ids, diff = tmp
        old_total = len(cur_ids)

        if diff:
            _update_es(shop_id, diff)
            R.sadd(key, *list(diff))
            cur_ids |= diff
            diff = set()

        if b:
            logger.info("{}: success, {}".format(shop_id, total))
            break
        else:
            logger.info("{}: retry, {} {}".format(shop_id, total, old_total))

        if old_total == old_redis_total:
            n += 1
        else:
            n = 0
            old_redis_total = old_total

        if n >= 3:
            n = 0
            index += 100 if index + 100 < total else 0


def _ss_goods_ids2(shop_id, index, cur_ids, diff):
    shop_id = str(shop_id)

    try:
        total, ids = ss_sku_ids(shop_id, index)
    except BaseException as e:
        logger.error(e)
        return str(e)

    if index > total:
        return "index > total {}".format(total)

    ids = set(ids)
    diff |= (ids - cur_ids)
    cur_ids |= diff
    redis_total = len(cur_ids)

    return total <= redis_total, total, cur_ids, diff


def _update_es(shop_id, diff):
    ids = list(diff)
    l = len(ids)
    for i in range(0, l, 10):
        sub_ids = [str(v) for v in ids[i:(i+10)]]
        try:
            total, infos = ss_sku_infos(shop_id, sub_ids)
        except BaseException as e:
            logger.error(e)
            raise e

        # actions = []
        es = Elasticsearch()
        for doc in infos:
            goods_id = int(doc['goods_id'])
            doc['shop_id'] = str(shop_id)
            doc['timestamp'] = datetime.datetime.now()
            try:
                res = es.index(index="jd-ss-goods", doc_type=str(shop_id), id=goods_id, body=doc)
                print(res['result'])
            except Exception as e:
                print(e)

            # todo test bulk
            # action = {
            #     "_index": "test-index",
            #     "_type": "jd-ss-goods",
            #     "_id": goods_id,
            #     "_source": doc
            # }
            # # 形成一个长度与查询结果数量相等的列表
            # actions.append(action)

        #helpers.bulk(es, actions)
