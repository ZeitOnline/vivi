from zeit.cms.checkout.helper import checked_out
from zeit.cms.workflow.interfaces import IPublish
from zeit.content.cp.centerpage import CenterPage
from zeit.content.cp.interfaces import ICP2009, ICP2015
import pkg_resources
import pyramid_dogpile_cache2
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.workflow.testing
import zope.interface


class MigrateTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def test_new_cp_provides_current_interface(self):
        self.repository['cp'] = CenterPage()
        with checked_out(self.repository['cp']):
            pass
        self.assertTrue(ICP2015.providedBy(self.repository['cp']))

    def test_publish_does_not_cycle_mismatched_cp(self):
        # Clear rules cache so we get the empty ruleset, so we can publish.
        pyramid_dogpile_cache2.clear()
        zope.app.appsetup.product.getProductConfiguration(
            'zeit.edit')['rules-url'] = 'file://%s' % (
                pkg_resources.resource_filename(
                    'zeit.content.cp.tests.fixtures', 'empty_rules.py'))

        self.repository['cp'] = CenterPage()
        with checked_out(self.repository['cp']) as cp:
            zope.interface.noLongerProvides(cp, ICP2015)
            zope.interface.alsoProvides(cp, ICP2009)
        before_publish = zeit.cms.workflow.interfaces.IModified(
            self.repository['cp']).date_last_checkout
        IPublish(self.repository['cp']).publish()
        zeit.workflow.testing.run_publish()
        after_publish = zeit.cms.workflow.interfaces.IModified(
            self.repository['cp']).date_last_checkout
        self.assertEqual(before_publish, after_publish)
