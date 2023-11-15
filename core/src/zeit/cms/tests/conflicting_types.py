import zeit.cms.type
import zope.interface


class ITestInterface(zope.interface.Interface):
    pass


class Decl1(zeit.cms.type.TypeDeclaration):
    type = 'foo'
    interface = ITestInterface


class Decl2(zeit.cms.type.TypeDeclaration):
    type = 'foo'
    interface = ITestInterface
