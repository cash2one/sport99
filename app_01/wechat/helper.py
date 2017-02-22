# -*-coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import types

# python版本
PY2 = sys.version_info[0] == 2

_always_safe = (b'abcdefghijklmnopqrstuvwxyz'
                b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-+')

# 判断系统版本，如果2.＊版本，字符编码unicode，迭代方式，还有将字符转化为本地字符编码的to_native()方法
if PY2:
    text_type = unicode  # text_type 是全局的
    iteritems = lambda d, *args, **kwargs: d.iteritems(*args, **kwargs)

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.encode(charset, errors)
else:
    text_type = str
    iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))

    def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
        if x is None or isinstance(x, str):
            return x
        return x.decode(charset, errors)


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.
    If strings_only is True, don't convert (some) non-string-like objects.
    将字符串转成字节
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                                           errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def get_encoding(html=None, headers=None):
    """网页的编码
    """
    try:
        import chardet
        if html:
            encoding = chardet.detect(html).get('encoding')
            return encoding
    except ImportError:
        pass
    if headers:
        content_type = headers.get('content-type')
        try:
            encoding = content_type.split(' ')[1].split('=')[1]
            return encoding
        except IndexError:
            pass


def iter_multi_items(mapping):
    """
    以生成器的方式迭代字典
    Iterates over the items of a mapping yielding keys and values
    without dropping any from more complex structures.
    """   
    if isinstance(mapping, dict):
        for key, value in iteritems(mapping):
            if isinstance(value, (tuple, list)):
                for v in value:
                    yield key, v
            else:
                yield key, value
    else:
        for item in mapping:
            yield item


def url_quote(string, charset='utf-8', errors='strict', safe='/:', unsafe=''):
    """
    URL encode a single string with a given encoding.
    """
    if not isinstance(string, (text_type, bytes, bytearray)):
        string = text_type(string)
    if isinstance(string, text_type):
        string = string.encode(charset, errors)
    if isinstance(safe, text_type):
        safe = safe.encode(charset, errors)
    if isinstance(unsafe, text_type):
        unsafe = unsafe.encode(charset, errors)
    safe = frozenset(bytearray(safe) + _always_safe) - frozenset(bytearray(unsafe))
    rv = bytearray()
    for char in bytearray(string):
        if char in safe:
            rv.append(char)
        else:
            rv.extend(('%%%02X' % char).encode('ascii'))
    return to_native(bytes(rv))


def url_quote_plus(string, charset='utf-8', errors='strict', safe=''):
    return url_quote(string, charset, errors, safe + ' ', '+').replace(' ', '+')


def url_params_encode_str(obj, charset='utf-8', sort=False, key=None, separator=b'&'):
    # 编码url 参数
    iterable = iter_multi_items(obj)
    if sort:
        iterable = sorted(iterable, key=key)
    params = []
    for key, value in iterable:
        if value is None:
            continue
        if not isinstance(key, bytes):
            key = text_type(key).encode(charset)
        if not isinstance(value, bytes):
            value = text_type(value).encode(charset)
        params.append(url_quote_plus(key) + '=' + url_quote_plus(value))

    separator = to_native(separator, 'ascii')
    return separator.join(params)


