import time
from lib_config.log.log import logger


if __name__ == '__main__':
    from task.ss_goods_ids import task
    while True:
        try:
            task()
            logger.info("task ok")
            print("task ok")
        except Exception as e:
            logger.error("task err {}".format(e))

        time.sleep(5)
