import grokcore.component.testing
import zope.component
import zope.configuration.config
import zope.interface

import zeit.cms.interfaces
import zeit.cms.testing
import zeit.cms.type


class ITestInterface(zope.interface.Interface):
    pass


class Declaration(zeit.cms.type.TypeDeclaration):
    interface = ITestInterface


class TestTypeDeclaration(zeit.cms.testing.ZeitCmsTestCase):
    def test_adapt_to_declaration(self):
        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        type_decl = zeit.cms.interfaces.ITypeDeclaration(content)
        self.assertEqual('testcontenttype', type_decl.type)

    def test_lookup_by_type(self):
        type_decl = zope.component.getUtility(
            zeit.cms.interfaces.ITypeDeclaration, name='testcontenttype'
        )
        self.assertEqual(
            zeit.cms.testcontenttype.testcontenttype.ExampleContentType, type_decl.factory
        )


class TestTypeIdentifier(zeit.cms.testing.ZeitCmsTestCase):
    def test_defaults_to_type(self):
        decl = zeit.cms.type.TypeDeclaration()
        decl.type = 'foo'
        self.assertEqual('foo', decl.type_identifier)
        decl.type = 'bar'
        self.assertEqual('bar', decl.type_identifier)

    def test_no_type_generates(self):
        # XXX https://github.com/pytest-dev/pytest/issues/5147
        from zeit.cms.tests.test_typegrokker import ITestInterface

        decl = zeit.cms.type.TypeDeclaration()
        decl.interface = zeit.cms.interfaces.ICMSContent
        self.assertEqual('zeit.cms.interfaces.ICMSContent', decl.type_identifier)
        decl.interface = ITestInterface
        self.assertEqual('zeit.cms.tests.test_typegrokker.ITestInterface', decl.type_identifier)

    def test_type_annotation_uses_type_identifier(self):
        # XXX https://github.com/pytest-dev/pytest/issues/5147
        from zeit.cms.tests.test_typegrokker import Declaration, ITestInterface

        grokcore.component.testing.grok_component('Declaration', Declaration)
        self.assertEqual(
            'zeit.cms.tests.test_typegrokker.ITestInterface',
            ITestInterface.getTaggedValue('zeit.cms.type'),
        )

    def test_type_identifier_conflict(self):
        self.assertRaises(
            zope.configuration.config.ConfigurationConflictError,
            grokcore.component.testing.grok,
            'zeit.cms.tests.conflicting_types',
        )
