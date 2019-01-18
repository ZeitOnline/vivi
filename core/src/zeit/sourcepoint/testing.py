import contextlib
import datetime
import mock
import plone.testing
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zope.component


product_config = """\
<product-config zeit.sourcepoint>
  api-token mytoken
  url http://example.com
  javascript-folder http://xml.zeit.de/sourcepoint/
</product-config>
"""

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'testing.zcml', product_config=product_config +
    zeit.cms.testing.cms_product_config)


class Layer(plone.testing.Layer):

    defaultBases = (ZCML_LAYER,)

    def testSetUp(self):
        with zeit.cms.testing.site(self['functional_setup'].getRootFolder()):
            repository = zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository)
            repository['sourcepoint'] = zeit.cms.repository.folder.Folder()

LAYER = Layer()


original = datetime.datetime


class FreezeMeta(type):

    def __instancecheck__(self, instance):
        if type(instance) == original or type(instance) == Freeze:
            return True


class Freeze(datetime.datetime):

    __metaclass__ = FreezeMeta

    @classmethod
    def freeze(cls, val):
        cls.frozen = val

    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            if cls.frozen.tzinfo is None:
                # https://docs.python.org/2/library/datetime.html says,
                # the result is equivalent to tz.fromutc(
                #   datetime.utcnow().replace(tzinfo=tz)).
                return tz.fromutc(cls.frozen.replace(tzinfo=tz))
            else:
                return cls.frozen.astimezone(tz)
        return cls.frozen

    @classmethod
    def today(cls, tz=None):
        return Freeze.now(tz)

    @classmethod
    def delta(cls, timedelta=None, **kwargs):
        """ Moves time fwd/bwd by the delta"""
        if not timedelta:
            timedelta = datetime.timedelta(**kwargs)
        cls.frozen += timedelta


@contextlib.contextmanager
def clock(dt=None):
    if dt is None:
        dt = original.utcnow()
    with mock.patch('datetime.datetime', Freeze):
        Freeze.freeze(dt)
        yield Freeze
