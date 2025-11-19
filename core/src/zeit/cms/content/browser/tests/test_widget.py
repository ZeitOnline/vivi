import lxml.etree
import zope.interface
import zope.publisher.browser

import zeit.cms.content.browser.widget
import zeit.cms.content.field
import zeit.cms.content.property
import zeit.cms.testing


class IContent(zope.interface.Interface):
    xml = zeit.cms.content.field.XMLTree()


@zope.interface.implementer(IContent)
class Content:
    xml = lxml.etree.fromstring('<art/><?foo?>')
    snippet = zeit.cms.content.property.Structure('.title')


class XMLSourceEditWidgetTest(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        self.content = Content()
        self.request = zope.publisher.browser.TestRequest()
        self.field = IContent['xml'].bind(self.content)
        self.widget = zeit.cms.content.browser.widget.XMLTreeWidget(self.field, self.request)

    def test_serializes_xml_to_and_from_string(self):
        self.widget.setRenderedValue(self.content.xml)
        self.assertEqual('<art/>\r\n<?foo?>\r\n', self.widget._getFormValue())
        self.assertIsInstance(self.widget._toFieldValue('<foo/>'), lxml.etree.Element)

    def test_invalid_xml_raises(self):
        with self.assertRaises(zope.formlib.interfaces.ConversionError) as info:
            self.widget._toFieldValue('<ed')
            self.assertIn(
                "Couldn't find end of Start Tag ed line 1, line 1, column 4", str(info.exception)
            )

    def test_edit_subtree(self):
        tree = lxml.etree.fromstring('<a><b/><editme><c/></editme></a>')
        self.content.xml = tree.find('editme')
        self.widget.setRenderedValue(self.content.xml)
        self.assertEqual('<editme>\r\n  <c/>\r\n</editme>\r\n', self.widget._getFormValue())

    def test_displaywidget(self):
        widget = zeit.cms.content.browser.widget.XMLTreeDisplayWidget(self.field, self.request)
        widget.setRenderedValue(lxml.etree.fromstring('<a><b/></a>'))
        self.assertIn(
            '<div class="pygments"><pre><span></span><span class="nt">&lt;a&gt;</span>', widget()
        )


class PermissiveDropdownTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_displays_value_even_if_not_present_in_source(self):
        b = self.browser
        b.open('/repository/testcontent/@@checkout')
        self.content = zeit.cms.interfaces.ICMSWCContent('http://xml.zeit.de/testcontent')
        self.content.title = 'required title'
        self.content.ressort = 'Nonexistent'
        b.reload()

        self.assertEqual(['Obsolete value Nonexistent'], b.getControl('Ressort').displayValue)

        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        self.assertEqual('Nonexistent', self.content.ressort)
