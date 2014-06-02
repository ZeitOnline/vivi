# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.cms.content.browser.commonmetadata
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zope.app.pagetemplate
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent


class ItemTraverser(object):

    zope.component.adapts(
        zeit.content.cp.interfaces.ITeaserBlock,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer)
    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        index = int(name)
        teaser = zope.component.queryMultiAdapter(
            (self.context, index), zeit.content.cp.interfaces.IXMLTeaser)
        if teaser is None:
            raise zope.publisher.interfaces.NotFound(
                self.context, name, self.request)
        return teaser


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

    def _is_not_teaser(self, action):
        return not self.context.free_teaser

    @zope.formlib.form.action(
        _('Apply for article'), name='apply_in_article',
        condition=_is_not_teaser)
    def apply_in_article(self, action, data):
        # TODO: adapt fails
        content = zeit.cms.interfaces.ICMSContent(self.context.uniqueId)
        with zeit.cms.checkout.helper.checked_out(content) as co:
            # XXX if co is None
            self._apply(co, data)

    @zope.formlib.form.action(
        _('Apply only for this page'), name='apply_locally')
    def apply_locally(self, action, data):
        self._apply(self.context, data)
        self.context.free_teaser = True

    def _apply(self, context, data):
        self.adapters = {}
        changed = zope.formlib.form.applyChanges(
            context, self.form_fields, data, self.adapters)
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(context))
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
