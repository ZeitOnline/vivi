from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import zeit.cms.browser.form
import zeit.edit.browser.form
import zope.formlib.form
import zope.interface


class Container(zeit.edit.browser.form.FoldableFormGroup):

    title = _('Social media')


# XXX Replace with XMLSource, see VIV-389
class TwitterAccountSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = ['Wissen', 'Politik']


class IAccounts(zope.interface.Interface):

    facebook = zope.schema.Bool(title=_('Enable Facebook'))
    google = zope.schema.Bool(title=_('Enable Google Plus'))
    twitter = zope.schema.Bool(title=_('Enable Twitter'))
    twitter_ressort = zope.schema.Choice(
        title=_('Additional Twitter'), source=TwitterAccountSource(),
        required=False)


class Social(zeit.edit.browser.form.InlineForm,
             zeit.cms.browser.form.CharlimitMixin):

    legend = _('')
    prefix = 'social'
    undo_description = _('edit social media')
    form_fields = (
        zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('long_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('facebook', 'google')
        + zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('short_text')
        + zope.formlib.form.FormFields(
            IAccounts).select('twitter', 'twitter_ressort')
        + zope.formlib.form.FormFields(
            zeit.push.interfaces.IPushMessages).select('enabled')
    )

    def setUpWidgets(self, *args, **kw):
        super(Social, self).setUpWidgets(*args, **kw)
        self.set_charlimit('short_text')


class Accounts(grok.Adapter):

    grok.context(zeit.cms.interfaces.ICMSContent)
    grok.implements(IAccounts)

    def __init__(self, context):
        self.context = context
        # XXX Reading is not yet implemented; writing will happen in the Form.
        self.facebook = False
        self.google = False
        self.twitter = False
        self.twitter_ressort = None
