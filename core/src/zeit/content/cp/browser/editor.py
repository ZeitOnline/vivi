from zeit.content.cp.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.interface
import zope.security.proxy
import zope.traversing.browser


class Editor(object):

    title = _('Edit centerpage')

    def validate(self, area):
        validation_class, validation_messages = (
            zeit.edit.browser.view.validate(area))
        css_class = ['editable-area']
        if validation_class:
            css_class.append(validation_class)
        css_class = ' '.join(css_class)
        return dict(class_=css_class, messages=validation_messages)


class Migrate(object):

    current_iface = zeit.content.cp.interfaces.ICP2015
    other_iface = zeit.content.cp.interfaces.ICP2009

    def __call__(self):
        if self.request.method == 'POST' and 'migrate' in self.request.form:
            # alsoProvides does not work with proxies
            context = zope.security.proxy.getObject(self.context)
            zope.interface.alsoProvides(context, self.current_iface)
            zope.interface.noLongerProvides(context, self.other_iface)
            return self.request.response.redirect(
                zope.traversing.browser.absoluteURL(
                    self.context, self.request))
        return super(Migrate, self).__call__()

    @property
    def content_type(self):
        for iface in [self.other_iface, self.current_iface]:
            if iface.providedBy(self.context):
                return iface.__name__
