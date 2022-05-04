from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.connector.sqlmigrate import migrate
import grokcore.component.zcml
import lxml.etree
import zeit.cms.testing
import zope.configuration.config


NS = 'http://namespaces.zeit.de/CMS/'


class SQLMigrate(zeit.cms.testing.ZeitCmsTestCase):

    def setUp(self):
        super().setUp()
        grokcore.component.zcml.do_grok(
            'zeit.connector.sqlmigrate',
            zope.configuration.config.ConfigurationMachine())

    def test_ignores_unmigrateable_content(self):
        res = self.repository.connector['http://xml.zeit.de/online/']
        with self.assertNothingRaised():
            res = migrate(res)

    def test_scalar_fields(self):
        content = ExampleContentType()
        content.title = 'foo'
        self.repository['foo'] = content
        res = self.repository.connector['http://xml.zeit.de/foo']
        res = migrate(res)
        props = res.properties
        # data was migrated to properties
        self.assertEqual('foo', props[('title', NS + 'document')])
        # other properties are preserved
        self.assertEqual('testcontenttype', props[('type', NS + 'meta')])
        # data was removed from XML
        body = lxml.etree.parse(res.data)
        self.assertFalse(body.xpath('//body/title'))

    def test_references(self):
        content = ExampleContentType()
        IRelatedContent(content).related = [self.repository['testcontent']]
        self.repository['foo'] = content
        res = self.repository.connector['http://xml.zeit.de/foo']
        res = migrate(res)
        props = res.properties
        self.assertEllipsis(
            '<val><head...'
            '<reference...href="http://xml.zeit.de/testcontent"...',
            props[('related', NS + 'document')])
        body = lxml.etree.parse(res.data)
        self.assertFalse(body.xpath('//reference'))
