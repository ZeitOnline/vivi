# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import lxml.etree
import transaction
import zeit.content.article.testing
import zeit.push.banner
import zeit.push.testing
import zeit.workflow.testing
import zope.security.management


class StaticArticlePublisherTest(zeit.push.testing.TestCase):

    def setUp(self):
        super(StaticArticlePublisherTest, self).setUp()
        self.repository['foo'] = zeit.content.article.testing.create_article()
        self.publisher = zeit.push.banner.StaticArticlePublisher(
            'http://xml.zeit.de/foo')

    def test_sets_first_paragraph_and_publishes(self):
        self.publisher.send('mytext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish(
            zeit.cms.workflow.interfaces.PRIORITY_HIGH)
        article = self.repository['foo']
        self.assertEqual(True, IPublishInfo(article).published)
        self.assertEllipsis(
            '<p...><a href="http://zeit.de/foo">mytext</a></p>',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))

    def test_updates_last_semantic_change(self):
        before = ISemanticChange(self.repository['foo']).last_semantic_change
        self.publisher.send('mytext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish(
            zeit.cms.workflow.interfaces.PRIORITY_HIGH)
        after = ISemanticChange(self.repository['foo']).last_semantic_change
        self.assertGreater(after, before)

    def test_regression_handles_unicode(self):
        self.publisher.send(u'mütext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish(
            zeit.cms.workflow.interfaces.PRIORITY_HIGH)
        article = self.repository['foo']
        self.assertEllipsis(
            '...m&#252;text...',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))

    def test_checked_out_already_deletes_from_workingcopy_first(self):
        ICheckoutManager(self.repository['foo']).checkout()
        self.publisher.send('mytext', 'http://zeit.de/foo')

    def test_checked_out_by_somebody_else_steals_lock_first(self):
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('other')
        ICheckoutManager(self.repository['foo']).checkout()
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.user')
        self.publisher.send('mytext', 'http://zeit.de/foo')

    def test_disables_message_config_only_on_commit(self):
        content = self.repository['testcontent']
        with checked_out(content) as co:
            push = zeit.push.interfaces.IPushMessages(co)
            push.short_text = u'banner'
            push.set({'type': 'homepage'}, enabled=True)
        push = zeit.push.interfaces.IPushMessages(content)
        push.messages[0].send()
        transaction.abort()
        self.assertEqual(True, push.get(type='homepage')['enabled'])
        push.messages[0].send()
        transaction.commit()
        self.assertEqual(False, push.get(type='homepage')['enabled'])
