# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component.testing
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.cms.type
import zope.configuration.config
import zope.interface

class ITestInterface(zope.interface.Interface):
    pass


class Declaration(zeit.cms.type.TypeDeclaration):

    interface = ITestInterface


class TestTypeDeclaration(zeit.cms.testing.FunctionalTestCase):

    def test_adapt_to_declaration(self):
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/politik.feed')
        type_decl = zeit.cms.interfaces.ITypeDeclaration(content)
        self.assertEquals('channel', type_decl.type)


class TestTypeIdentifier(zeit.cms.testing.FunctionalTestCase):

    def test_defaults_to_type(self):
        decl = zeit.cms.type.TypeDeclaration()
        decl.type = u'foo'
        self.assertEquals(u'foo', decl.type_identifier)
        decl.type = u'bar'
        self.assertEquals(u'bar', decl.type_identifier)

    def test_no_type_generates(self):
        decl = zeit.cms.type.TypeDeclaration()
        decl.interface = zeit.cms.interfaces.ICMSContent
        self.assertEquals(u'zeit.cms.interfaces.ICMSContent',
                          decl.type_identifier)
        decl.interface = ITestInterface
        self.assertEquals(u'zeit.cms.tests.test_typegrokker.ITestInterface',
                          decl.type_identifier)

    def test_type_annotation_uses_type_identifier(self):
        grokcore.component.testing.grok_component('Declaration', Declaration)
        self.assertEquals(u'zeit.cms.tests.test_typegrokker.ITestInterface',
                          ITestInterface.getTaggedValue('zeit.cms.type'))

    def test_type_identifier_conflict(self):
        self.assertRaises(
            zope.configuration.config.ConfigurationConflictError,
            grokcore.component.testing.grok,
            'zeit.cms.tests.conflicting_types')
