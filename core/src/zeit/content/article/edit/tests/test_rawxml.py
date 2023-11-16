import lxml
import unittest
import zeit.cms.testing
import zeit.content.article.testing
import zope.schema


class RawXMLTest(unittest.TestCase):
    def test_root_tag_must_be_raw(self):
        from zeit.content.article.edit.interfaces import IRawXML
        import lxml.objectify

        field = IRawXML['xml']
        with self.assertRaises(zope.schema.ValidationError) as e:
            field.validate(lxml.objectify.E.foo())
            self.assertIn('The root element must be <raw>', str(e.exception))
        field.validate(lxml.objectify.E.raw())


class TestFactory(zeit.content.article.testing.FunctionalTestCase):
    def test_factory_should_create_raw_node(self):
        import zeit.content.article.article
        import zeit.content.article.edit.interfaces
        import zeit.edit.interfaces
        import zope.component

        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.body)
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, 'raw')
        self.assertEqual('Raw XML block', factory.title)
        div = factory()
        self.assertTrue(zeit.content.article.edit.interfaces.IRawXML.providedBy(div))
        self.assertEqual('raw', div.xml.tag)
        self.assertEllipsis('<raw...>\n\n</raw>', zeit.cms.testing.xmltotext(div.xml))

    def test_stores_consent_info_in_xml(self):
        article = zeit.content.article.article.Article()
        body = zeit.content.article.edit.body.EditableBody(article, article.xml.body)
        factory = zope.component.getAdapter(body, zeit.edit.interfaces.IElementFactory, 'raw')
        module = factory()
        info = zeit.cmp.interfaces.IConsentInfo(module)
        info.has_thirdparty = True
        info.thirdparty_vendors = ['Twitter', 'Facebook']
        self.assertEqual(True, info.has_thirdparty)
        self.assertEqual(('Twitter', 'Facebook'), info.thirdparty_vendors)
        self.assertEllipsis(
            '<...has_thirdparty="yes"' ' thirdparty_vendors="Twitter;Facebook"...',
            lxml.etree.tostring(module.xml, encoding=str),
        )
