# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Workflow indicators."""

import xml.sax.saxutils

import zope.component
import zope.dublincore.interfaces
import zope.i18n
import zope.viewlet.viewlet
import zope.app.form.browser.interfaces

import zeit.workflow
from zeit.cms.i18n import MessageFactory as _


class ContentStatus(zope.viewlet.viewlet.ViewletBase):
    """Indicate whether an object is published or not."""

    def update(self):
        self.workflow = zeit.workflow.interfaces.IContentWorkflow(
            self.context, None)

    def render(self):
        if self.workflow is None:
            return u''

        states = []

        for name in ('edited', 'corrected', 'refined', 'images_added'):
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

            states.append(u'<span title=%s class="content-status %s">'
                          u'%s</span>' %
                          (xml.sax.saxutils.quoteattr(long_title), class_,
                           xml.sax.saxutils.escape(short_title)))

        return u'\n'.join(states)

    def get_class(self, value):
        if not value:
            return 'state-no'
        if value is zeit.workflow.interfaces.NotNecessary:
            return 'state-notnecessary'
        return 'state-yes'


class AssetStatus(zope.viewlet.viewlet.ViewletBase):

    def render(self):
        return u''
