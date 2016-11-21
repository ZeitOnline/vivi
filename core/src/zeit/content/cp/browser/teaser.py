from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.content.browser.commonmetadata
import zeit.cms.content.browser.form
import zeit.content.cp.interfaces
import zope.component
import zope.formlib.form


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


class ListRepresentation(
        zeit.cms.content.browser.commonmetadata.
        CommonMetadataListRepresentation):

    zope.component.adapts(zeit.content.cp.interfaces.ITeaser,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.context.teaserTitle


class FormBase(object):

    form_fields = (
        zeit.cms.content.browser.form.CommonMetadataFormBase.form_fields +
        zope.formlib.form.FormFields(
            zeit.content.cp.interfaces.ITeaser).select('original_content'))


class EditForm(FormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _("Edit teaser")


class DisplayForm(FormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _("View teaser")
