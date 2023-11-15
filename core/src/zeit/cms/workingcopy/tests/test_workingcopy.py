from zeit.cms.workingcopy.interfaces import IWorkingcopy
import zeit.cms.testing
import zope.component
import zope.security.management


class AdapterTests(zeit.cms.testing.ZeitCmsTestCase):
    def test_adapting_none_should_return_current_principals_wc(self):
        wc = IWorkingcopy(None)
        self.assertEqual('zope.user', wc.__name__)

    def test_no_interaction_should_return_none(self):
        zope.security.management.endInteraction()
        wc = zope.component.queryAdapter(None, zeit.cms.workingcopy.interfaces.IWorkingcopy)
        self.assertEqual(None, wc)
