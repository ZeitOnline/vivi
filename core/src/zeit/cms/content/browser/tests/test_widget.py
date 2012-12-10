# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import lxml.objectify
import unittest
import zeit.cms.content.browser.widget
import zeit.cms.content.field
import zope.interface
import zope.publisher.browser


class IContent(zope.interface.Interface):

    xml = zeit.cms.content.field.XMLTree()


class Content(object):

    zope.interface.implements(IContent)
    document = lxml.objectify.XML('<root><foo bar="baz"/></root>')

    @property
    def xml(self):
        return self.document.foo


class XMLTreeWidget(unittest.TestCase,
                    zeit.cms.testing.BrowserAssertions):

    def test_puts_attributes_in_hidden_field_for_form(self):
        request = zope.publisher.browser.TestRequest()
        content = Content()
        field = IContent['xml'].bind(content)
        widget = zeit.cms.content.browser.widget.XMLTreeWidget(field, request)
        widget.setRenderedValue(content.xml)
        self.assertEllipsis(
            '...<textarea...>&lt;foo/&gt;\r\n</textarea>'
            '...value="bar=baz"...', widget())

    def test_preserves_attributes_of_context(self):
        request = zope.publisher.browser.TestRequest()
        content = Content()
        field = IContent['xml'].bind(content)
        widget = zeit.cms.content.browser.widget.XMLTreeWidget(field, request)
        request.form[widget.name] = '<foo/>'
        request.form[widget.attributes_name] = 'bar=baz'
        self.assertEqual(
            '<foo bar="baz"/>', lxml.etree.tostring(widget.getInputValue()))
