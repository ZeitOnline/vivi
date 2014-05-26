# coding: utf-8
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import lxml.etree
import zeit.content.article.testing
import zeit.push.cp
import zeit.push.testing
import zeit.workflow.testing


class StaticArticlePublisherTest(zeit.push.testing.TestCase):

    def test_sets_first_paragraph_and_publishes(self):
        self.repository['foo'] = zeit.content.article.testing.create_article()
        self.assertEqual(
            None, ISemanticChange(self.repository['foo']).last_semantic_change)
        publisher = zeit.push.cp.StaticArticlePublisher(
            'http://xml.zeit.de/foo')
        publisher.send('mytext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish()
        article = self.repository['foo']
        self.assertEqual(True, IPublishInfo(article).published)
        self.assertNotEqual(
            None, ISemanticChange(article).last_semantic_change)
        self.assertEllipsis(
            '<p...><a href="http://zeit.de/foo">mytext</a></p>',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))

    def test_regression_handles_unicode(self):
        self.repository['foo'] = zeit.content.article.testing.create_article()
        self.assertEqual(
            None, ISemanticChange(self.repository['foo']).last_semantic_change)
        publisher = zeit.push.cp.StaticArticlePublisher(
            'http://xml.zeit.de/foo')
        publisher.send(u'mütext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish()
        article = self.repository['foo']
        self.assertEllipsis(
            '...m&#252;text...',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))
