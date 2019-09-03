from model.mongo.model import ShopModel


def get_all_ss_shop_ids():
    shops = ShopModel().find({'jd_type': 'SS'})

    return [v['_id'] for v in shops]
