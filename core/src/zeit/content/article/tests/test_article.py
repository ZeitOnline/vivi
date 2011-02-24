# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.testing
import zeit.edit.rule
import zeit.workflow.interfaces
import zope.component


class WorkflowTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(WorkflowTest, self).setUp()
        self.article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        self.info = zeit.cms.workflow.interfaces.IPublishInfo(self.article)
        self.cwf = zeit.workflow.interfaces.IContentWorkflow(self.article)

        sm = zope.component.getSiteManager()
        self.orig_validator = sm.adapters.lookup(
            (zeit.content.article.interfaces.IArticle,),
            zeit.edit.interfaces.IValidator)

        self.validator = mock.Mock()
        zope.component.provideAdapter(
            self.validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)

    def tearDown(self):
        zope.component.getSiteManager().unregisterAdapter(
            required=(zeit.content.article.interfaces.IArticle,),
            provided=zeit.edit.interfaces.IValidator)
        zope.component.provideAdapter(
            self.orig_validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)
        super(WorkflowTest, self).tearDown()

    def test_not_urgent_cannot_publish(self):
        self.assertFalse(self.cwf.urgent)
        self.assertFalse(self.info.can_publish())
        self.assertFalse(self.validator.called)

    def test_validation_passes_can_publish(self):
        self.cwf.urgent = True
        self.validator().status = None
        self.assertTrue(self.info.can_publish())
        self.validator.assert_called_with(self.article)

    def test_validation_fails_cannot_publish(self):
        self.cwf.urgent = True
        self.validator().status = zeit.edit.rule.ERROR
        self.assertFalse(self.info.can_publish())
        self.validator.assert_called_with(self.article)
