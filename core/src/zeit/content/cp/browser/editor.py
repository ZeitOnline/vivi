from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.browser.view
import zeit.cms.workingcopy.browser.workingcopy
import zeit.edit.browser.view
import zope.interface
import zope.lifecycleevent
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


class Migrate(zeit.cms.workingcopy.browser.workingcopy.DeleteFromWorkingcopy):

    current_iface = zeit.content.cp.interfaces.ICP2015
    other_iface = zeit.content.cp.interfaces.ICP2009

    def __call__(self):
        if self.request.method != 'POST':
            return super(Migrate, self).__call__()
        if 'migrate' in self.request.form:
            # alsoProvides does not work with proxies
            context = zope.security.proxy.getObject(self.context)
            zope.interface.alsoProvides(context, self.current_iface)
            zope.interface.noLongerProvides(context, self.other_iface)
            return self.request.response.redirect(
                zope.traversing.browser.absoluteURL(
                    self.context, self.request))
        elif 'cancel' in self.request.form:
            self.delete()
            return self.request.response.redirect(
                self.next_url(self.context.__parent__))

    @property
    def content_type(self):
        for iface in [self.other_iface, self.current_iface]:
            if iface.providedBy(self.context):
                return iface.__name__


class ToggleBooleanBase(zeit.edit.browser.view.Action):

    to = zeit.edit.browser.view.Form('to')
    attribute = NotImplemented

    @property
    def target(self):
        return self.context

    def update(self):
        setattr(self.target, self.attribute,
                (True if self.to == 'on' else False))
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.reload()


class ToggleMenuItem(zeit.cms.browser.view.Base):

    attribute = NotImplemented

    @property
    def target(self):
        return self.context

    @property
    def toggle_url(self):
        on_off = 'off' if getattr(self.target, self.attribute) else 'on'
        return self.url('@@toggle-{}?to={}'.format(self.attribute, on_off))


class ToggleVisibleMenuItem(ToggleMenuItem):

    attribute = 'visible'


class ToggleVisible(ToggleBooleanBase):

    attribute = 'visible'
