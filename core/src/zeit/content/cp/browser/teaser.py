# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.cms.content.browser.commonmetadata
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zope.app.pagetemplate
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent


class CheckoutContent(object):

    def __call__(self, uniqueId):
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        checked_out = manager.checkout()
        self.request.response.redirect(
            '%s/++item++%s/edit-teaser.html' % (
            zope.traversing.browser.absoluteURL(self.context, self.request),
            checked_out.__name__))


class TeaserBlockProxyItem(object):

    zope.interface.implements(zeit.cms.content.interfaces.ICommonMetadata,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        return getattr(self.context, name)

    def __setattr__(self, name, value):
        if name in ['context', '__name__', '__parent__']:
            object.__setattr__(self, name, value)
        else:
            setattr(self.context, name, value)

    def get_proxied_object(self):
        return self.context


@zope.component.adapter(TeaserBlockProxyItem)
@zope.interface.implementer(zeit.cms.checkout.interfaces.ICheckinManager)
def checkin_manager_for_proxy(proxy):
    return zeit.cms.checkout.interfaces.ICheckinManager(
        proxy.get_proxied_object())


class ItemTraverser(object):

    zope.component.adapts(
        zeit.content.cp.interfaces.ITeaserBlock,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer)
    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(
            self.request.principal)

        try:
            return zope.location.location.located(
                TeaserBlockProxyItem(wc[name]), self.context, name)
        except KeyError:
            raise zope.publisher.interfaces.NotFound(
                self.context, name, self.request)


class EditTeaser(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.edit.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'supertitle', 'teaserTitle', 'teaserText')
    close = False

    def __call__(self, *args, **kw):
        return super(EditTeaser, self).__call__(*args, **kw)

    @property
    def form(self):
        return super(EditTeaser, self).template

    def _is_teaser(self, action):
        return zeit.content.cp.interfaces.ITeaser.providedBy(
            self.context.get_proxied_object())

    def _is_not_teaser(self, action):
        return not self._is_teaser(action)

    @zope.formlib.form.action(_('Apply for article'), name='apply',
                              condition=_is_not_teaser)
    def apply(self, action, data):
        self._apply(data)

    @zope.formlib.form.action(
        _('Apply only for this page'), condition=_is_teaser)
    def apply_in_teaser(self, action, data):
        self._apply(data)

    def _apply(self, data):
        changed = zope.formlib.form.applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(
                    self.context.get_proxied_object()))
            manager = zeit.cms.checkout.interfaces.ICheckinManager(
                self.context)
            manager.checkin()
            self.close = True

    @zope.formlib.form.action(
        _('Apply only for this page'), condition=_is_not_teaser)
    def apply_local(self, action, data):
        teaser = zeit.content.cp.interfaces.ITeaser(self.context)
        changed = zope.formlib.form.applyChanges(
            teaser, self.form_fields, data)
        if not changed:
            return

        folder = zeit.cms.interfaces.ICMSContent(
            self.context.uniqueId).__parent__
        name = zope.container.interfaces.INameChooser(
            folder).chooseName(self.context.__name__, teaser)

        # Delete the original_content from the working copy.
        del self.context.get_proxied_object().__parent__[self.context.__name__]
        folder[name] = teaser
        teaser = folder[name]
        teaser_list = self.context.__parent__
        teaser_list.insert(teaser_list.getPosition(self.context), teaser)
        teaser_list.remove(self.context)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(teaser_list))
        self.close = True


class ListRepresentation(
    zeit.cms.content.browser.commonmetadata.CommonMetadataListRepresentation):

    zope.component.adapts(zeit.content.cp.interfaces.ITeaser,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.context.teaserTitle


class FormBase(object):

    form_fields = (
        zeit.cms.content.browser.form.CommonMetadataFormBase.form_fields.omit(
            'automaticMetadataUpdateDisabled')
        + zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ITeaser).select('original_content'))


class EditForm(FormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _("Edit teaser")


class DisplayForm(FormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View teaser")
