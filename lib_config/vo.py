from datetime import *
from json import JSONEncoder, JSONDecoder, loads
from importlib import import_module
from collections import OrderedDict
from .const import UTC8_ZONE

from bson import ObjectId


class CommonVO(object):

    def __init__(self, mo, **kwargs):
        if kwargs and mo is not None:
            mo = dict(mo, **kwargs)

        self.mo = mo

    def __call__(self, handler):
        return self._copy_mo(handler)

    def __setitem__(self, key, value):
        if self.mo is not None:
            self.mo[key] = value

    def __getitem__(self, key, default=None):
        return self.mo.get(key, default) if self.mo else default

    def __contains__(self, key):
        return key in self.mo if self.mo else False

    def _copy_mo(self, handler, include_fields=None, exclude_fields=None):
        if self.mo is None:
            return None

        fields = (set(include_fields or self.mo.keys()) - set(exclude_fields or []))

        is_inner_vo = handler and handler.get_argument("inner_vo", False)
        if is_inner_vo:
            vo = {k: v for k, v in self.mo.items() if k in fields}
            return encode_vo(call_vo(vo, handler))

        vo = {(k if k != '_id' else 'id'): v for k, v in self.mo.items() if k in fields}

        return to_json_type(call_vo(vo, handler))


class CommonBeijingVO(CommonVO):

    def _copy_mo(self, handler, include_fields=None, exclude_fields=None):
        if self.mo is None:
            return None

        fields = (set(include_fields or self.mo.keys()) - set(exclude_fields or []))
        is_inner_vo = handler and handler.get_argument("inner_vo", False)
        if is_inner_vo:
            vo = {k: v for k, v in self.mo.items() if k in fields}
            return encode_vo(call_vo(vo, handler))

        vo = {(k if k != '_id' else 'id'): v for k, v in self.mo.items() if k in fields}
        return to_json_type(call_vo(vo, handler), show_tz=timezone(timedelta(hours=8)))


def call_vo(vo, handler):
    if isinstance(vo, CommonVO):
        return vo(handler)
    elif isinstance(vo, list):
        return [call_vo(v, handler) for v in vo]
    elif isinstance(vo, tuple):
        return tuple(call_vo(v, handler) for v in vo)
    elif isinstance(vo, dict):
        return {k: call_vo(v, handler) for k, v in vo.items()}
    else:
        return vo


class CommonEncoder(JSONEncoder):

    def encode(self, o):
        return super().encode(encode_vo(o))


def encode_vo(o):
    if isinstance(o, CommonVO):
        return {
            '$vo:v1:{}:{}'.format(
                o.__class__.__module__, o.__class__.__name__):
            encode_vo(o.mo)
        }
    elif isinstance(o, datetime):
        return {'$date': o.timestamp()}
    elif isinstance(o, ObjectId):
        return {'$oid': str(o)}
    elif isinstance(o, list) or isinstance(o, tuple) or isinstance(o, set):
        return [encode_vo(v) for v in o]
    elif isinstance(o, dict):
        return {k: encode_vo(v) for k, v in o.items()}
    else:
        return o


class CommonDecoder(JSONDecoder):

    def decode(self, s):
        return decode_vo(super().decode(s))


def decode_vo(o, **kwargs):
    if isinstance(o, list):
        return [decode_vo(v, **kwargs) for v in o]
    elif isinstance(o, dict):
        if len(o) == 1:
            k, v = list(o.items())[0]
            if isinstance(k, str) and k.startswith('$vo:'):
                _, _, module, cls = k.split(':')
                cls = getattr(import_module(module), cls.replace('VOV2', 'VO'))
                o = cls.__new__(cls)
                o.mo = decode_vo(v, **kwargs)
                return o
            elif isinstance(k, str) and k == '$date':
                return datetime.fromtimestamp(v, tz=kwargs.get("tz", UTC8_ZONE))
            elif isinstance(k, str) and k == '$oid':
                return ObjectId(v)
        return {k: decode_vo(v, **kwargs) for k, v in o.items()}
    else:
        return o


def to_json_type(data, **kwargs):
    """
    kwargs {
        "reserve_none": false,
        "show_tz": timezone(),
        "convert_id": false,
    }
    """
    if isinstance(data, (list, tuple, set)):
        return [to_json_type(v, **kwargs) for v in data if v is not None or kwargs.get("reserve_none")]
    elif isinstance(data, dict):
        if isinstance(data, OrderedDict):
            return to_json_type(list(data.items()), **kwargs)
        else:
            return {to_json_type(k, **kwargs): to_json_type(v, **kwargs) for k, v in data.items()
                    if v is not None or kwargs.get("reserve_none")}
    elif isinstance(data, datetime):
        if kwargs.get("show_tz") and data.tzinfo:
            data = data.astimezone(tz=kwargs["show_tz"])
        return data.strftime("%Y-%m-%d %H:%M:%S.%f")
    elif isinstance(data, date):
        return data.strftime("%Y-%m-%d")
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        if kwargs.get("convert_id") and data == "_id":
            return "id"
        return data


def load_inner_vo_data(text):
    return decode_vo(loads(text))
