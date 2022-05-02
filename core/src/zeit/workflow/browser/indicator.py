from zeit.cms.i18n import MessageFactory as _
import xml.sax.saxutils
import zeit.workflow
import zope.app.form.browser.interfaces
import zope.component
import zope.i18n
import zope.viewlet.viewlet


class ContentStatus(zope.viewlet.viewlet.ViewletBase):
    """Indicate whether an object is published or not."""

    def update(self):
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(
            self.context, None)

    def render(self):
        if self.workflow is None:
            return ''

        states = []

        for name in ('edited', 'corrected'):
            field = zeit.workflow.interfaces.IContentWorkflow[name]
            value = field.query(self.workflow)
            if value is None:
                value = False
            terms = zope.component.getMultiAdapter(
                (field.vocabulary, self.request),
                zope.app.form.browser.interfaces.ITerms)
            term = terms.getTerm(value)
            value_title = term.title

            short_title = zope.i18n.translate(field.title,
                                              context=self.request)[0]
            long_title = zope.i18n.translate(
                _('${title}: ${state}',
                  mapping=dict(title=field.title, state=value_title)),
                context=self.request)

            class_ = self.get_class(value)

            states.append('<span title=%s class="content-status %s">'
                          '%s</span>' %
                          (xml.sax.saxutils.quoteattr(long_title), class_,
                           xml.sax.saxutils.escape(short_title)))

        return '\n'.join(states)

    def get_class(self, value):
        if not value:
            return 'state-no'
        if value is zeit.workflow.interfaces.NotNecessary:
            return 'state-notnecessary'
        return 'state-yes'


class AssetStatus(zope.viewlet.viewlet.ViewletBase):

    def render(self):
        return ''
