from unittest import mock
import zope.interface

import zeit.simplecast.interfaces


@zope.interface.implementer(zeit.simplecast.interfaces.ISimplecast)
class MockSimplecast(mock.Mock):
    pass
