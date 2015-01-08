import z3c.flashmessage.interfaces
import zeit.cms.browser
import zeit.cms.browser.interfaces
import zeit.cms.browser.resources
import zeit.cms.checkout.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zope.app.basicskin.standardmacros
import zope.component
import zope.location.interfaces
import zope.security.proxy


class StandardMacros(zope.app.basicskin.standardmacros.StandardMacros):

    macro_pages = ('main_template',)

    def messages(self):
        receiver = zope.component.getUtility(
            z3c.flashmessage.interfaces.IMessageReceiver)
        return list(receiver.receive())

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
        if (not title
            and zope.location.interfaces.ISite.providedBy(self.context)):
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
        for iface in zope.interface.providedBy(section):
            if issubclass(zope.security.proxy.getObject(iface),
                          zeit.cms.section.interfaces.ISection):
                return iface.__name__
        return 'unknown'

    def require_resources(self):
        zeit.cms.browser.resources.backend.need()
