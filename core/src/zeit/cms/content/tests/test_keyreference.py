import zope.app.keyreference.interfaces

from zeit.cms.checkout.helper import checked_out
import zeit.cms.repository.interfaces
import zeit.cms.testing


class KeyReferenceTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_uses_target_id_for_renameable_content(self):
        with checked_out(self.repository['testcontent']) as co:
            rn = zeit.cms.repository.interfaces.IAutomaticallyRenameable(co)
            rn.renameable = True
            rn.rename_to = 'changed'
            ref = zope.app.keyreference.interfaces.IKeyReference(co)
            self.assertEqual('http://xml.zeit.de/changed', ref.referenced_object)
