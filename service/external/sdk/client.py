from lib_util.client.client import BaseClient


class SDKClient(BaseClient):
    def __init__(self):
        from .const import NAME
        super().__init__(NAME)
