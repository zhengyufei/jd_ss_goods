from .client import SDKClient


client = SDKClient()


@SDKClient.decorator_retry(client)
def ss_sku_ids(shop_id, index=0):
    data = client.get("/sdk/goods/ss_sku_ids", {"shop_id": shop_id, "index": index})
    SDKClient.raise_error(client, data)
    return data.get('total', 0), data.get("sku_ids", [])


@SDKClient.decorator_retry(client)
def ss_sku_infos(shop_id, ids):
    tmp = ",".join([str(v) for v in ids])
    data = client.get("/sdk/goods/ss_sku_infos", {"shop_id": shop_id, "ids": tmp})
    SDKClient.raise_error(client, data)
    return data.get('total', 0), data.get("results", [])
