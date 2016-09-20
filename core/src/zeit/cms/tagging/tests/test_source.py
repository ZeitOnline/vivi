from mock import Mock
import gocept.testing.assertion
import unittest
import zope.schema


class TestLocationSource(unittest.TestCase,
                         gocept.testing.assertion.Exceptions):
    """Testing ..source.LocationSource."""

    def test_it_validates_each_value(self):
        from ..source import locationSource
        choice = zope.schema.Choice(title=u'title', source=locationSource)
        choice = choice.bind(Mock())
        with self.assertNothingRaised():
            choice.validate(u'Paris')
