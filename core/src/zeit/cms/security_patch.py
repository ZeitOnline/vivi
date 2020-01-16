import abc
import collections.abc
import zope.security.checker
import zope.security.proxy


# <https://github.com/zopefoundation/zope.security/issues/26>
class ClassProxy(object):
    pass


def instancecheck_with_zope_proxy(cls, instance):
    if issubclass(type(instance), zope.security.proxy.Proxy):
        instance = ClassProxy()
        instance.__class__ = zope.security.proxy.getObject(instance).__class__
    return abc.ABCMeta._old___instancecheck__(cls, instance)


class DummyMapping(collections.abc.Mapping):

    def __getitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


mydict = DummyMapping()

# <https://github.com/zopefoundation/zope.security/issues/66>
zope.security.checker.BasicTypes[
    type(mydict.keys())] = zope.security.checker.NoProxy
zope.security.checker.BasicTypes[
    type(mydict.values())] = zope.security.checker.NoProxy
zope.security.checker.BasicTypes[
    type(mydict.items())] = zope.security.checker.NoProxy
