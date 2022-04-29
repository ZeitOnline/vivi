from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zope.formlib.form


class FeedFormBase:
    pass


class AddForm(FeedFormBase, zeit.cms.browser.form.AddForm):

    title = _("Add Channel")
    factory = zeit.cms.syndication.feed.Feed

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.cms.syndication.interfaces.IFeed))


class EditForm(FeedFormBase, zeit.cms.browser.form.EditForm):

    title = _("Edit Channel")

    form_fields = zope.formlib.form.Fields(
        zeit.cms.syndication.interfaces.IFeed,
        render_context=True)
