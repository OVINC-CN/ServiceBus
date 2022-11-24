import datetime
import os
import random
import time
import uuid
from distutils.util import strtobool as _strtobool
from hashlib import md5
from itertools import chain

from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest


def uniq_id() -> str:
    """
    Create Uniq ID
    """

    m = md5()
    m.update(str(int(time.time() * 1000)).encode())
    time_str = str(m.hexdigest())
    uniq = str(uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex)
    return f"{time_str}{uniq}"


def get_auth_token(uid: str, timeout: int = None) -> str:
    """
    Create Auth Token
    """

    uniq = uniq_id()
    in_use = cache.get(uniq)
    if in_use is None:
        timeout = timeout or settings.SESSION_COOKIE_AGE
        cache.set(uniq, uid, timeout)
        return uniq
    return get_auth_token(uid)


def simple_uniq_id(length: int) -> str:
    """
    Create Simple Uniq ID
    """

    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    random.seed(uniq_id())
    uniq = ""
    i = 0
    while i < length:
        i += 1
        uniq += base[random.randint(0, len(base) - 1)]
    return uniq


def num_code(length: int) -> str:
    """
    Create Number Code
    """

    random.seed(uniq_id())
    uniq = ""
    i = 0
    while i < length:
        i += 1
        uniq += str(random.randint(0, 9))
    return uniq


def get_ip(request: WSGIRequest) -> str:
    """
    Get IP from Request
    """

    if request.META.get("HTTP_X_REAL_IP"):
        return request.META.get("HTTP_X_REAL_IP")
    if request.META.get("HTTP_X_FORWARDED_FOR"):
        return request.META.get("HTTP_X_FORWARDED_FOR").replace(" ", "").split(",")[0]
    if request.META.get("HTTP_X_FORWARD_FOR"):
        return request.META.get("HTTP_X_FORWARD_FOR").replace(" ", "").split(",")[0]
    return request.META.get("REMOTE_ADDR")


def field_handler(data) -> any:
    """
    Handler Date/Datetime Field Data
    """

    if isinstance(data, datetime.datetime):
        return data.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(data, datetime.date):
        return data.strftime("%Y-%m-%d")
    else:
        return data


def model_to_dict(instance, fields=None, exclude=None) -> dict:
    """
    Trans Model Data to Json
    """

    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = field_handler(f.value_from_object(instance))
    return data


def getenv_or_raise(key: str) -> str:
    """
    Force Get Env
    """

    val = os.getenv(key)
    if val is None:
        raise Exception(f"Env Not Set, Key [{key}]")
    return val


def strtobool(val):
    """
    Trans Str to Bool
    """

    return bool(_strtobool(str(val)))
