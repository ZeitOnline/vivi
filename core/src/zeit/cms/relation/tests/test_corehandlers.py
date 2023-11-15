from unittest import mock
import transaction
import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.cms.related.interfaces
import zeit.cms.relation.corehandlers


class CorehandlerTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        from zeit.cms.testcontenttype.testcontenttype import ExampleContentType

        super().setUp()

        self.repository['parent'] = ExampleContentType()
        self.repository['reference'] = ExampleContentType()

        reference = self.repository['reference']
        related = zeit.cms.related.interfaces.IRelatedContent(reference)
        related.related = (self.repository['parent'],)
        self.repository['reference'] = reference

    def test_update_referencing_objects_is_not_updating_recursively(self):
        delay = 'z3c.celery.celery.TransactionAwareTask.delay'
        with mock.patch(delay) as delay:
            zeit.cms.relation.corehandlers.update_referencing_objects(self.repository['parent'])
            transaction.commit()

        self.assertEqual(0, len(delay.call_args_list))
