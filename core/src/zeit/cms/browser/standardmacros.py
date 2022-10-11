import zeit.cms.browser
import zeit.cms.browser.interfaces
import zeit.cms.browser.resources
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zope.app.appsetup.product
import zope.app.basicskin.standardmacros
import zope.component
import zope.location.interfaces
import zope.security.proxy
import pkg_resources


class StandardMacros(zope.app.basicskin.standardmacros.StandardMacros):

    macro_pages = ('main_template',)

    @property
    def context_title(self):
        title = ''
        list_repr = zope.component.queryMultiAdapter(
            (self.context, self.request),
            zeit.cms.browser.interfaces.IListRepresentation)
        if list_repr is not None:
            title = list_repr.title
        if not title:
            title = self.context.__name__
        if not title and zope.location.interfaces.ISite.providedBy(
                self.context):
            title = '/'
        if not title:
            title = str(self.context)
        return title

    @property
    def type_declaration(self):
        no_type = type(
            'NoTypeDeclaration', (object,), dict(type_identifier='unknown'))
        return zeit.cms.interfaces.ITypeDeclaration(self.context, no_type)

    @property
    def context_location(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(self.context):
            return 'workingcopy'
        elif zeit.cms.repository.interfaces.IRepositoryContent.providedBy(
                self.context):
            return 'repository'
        else:
            return 'unknown'

    @property
    def section(self):
        section = zeit.cms.section.interfaces.ISection(self.context, None)
        if section is None:
            return 'unknown'
        return section.__name__

    def require_resources(self):
        zeit.cms.browser.resources.backend.need()

    @property
    def environment(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        return config['environment']

    @property
    def vivi_version(self):
        if pkg_resources.get_distribution('vivi.core'):
            return pkg_resources.get_distribution('vivi.core').version
        return 'version not found'
