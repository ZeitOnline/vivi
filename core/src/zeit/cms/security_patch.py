# https://github.com/zopefoundation/zope.security/issues/26
import abc
import zope.security.proxy


class ClassProxy(object):
    pass


def instancecheck_with_zope_proxy(cls, instance):
    if issubclass(type(instance), zope.security.proxy.Proxy):
        instance = ClassProxy()
        instance.__class__ = zope.security.proxy.getObject(instance).__class__
    return original_check(cls, instance)


original_check = abc.ABCMeta.__instancecheck__
abc.ABCMeta.__instancecheck__ = instancecheck_with_zope_proxy
