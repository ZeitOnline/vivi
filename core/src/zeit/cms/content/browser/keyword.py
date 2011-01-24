# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.tree
import zeit.cms.browser.widget
import zeit.cms.content.keyword
import zope.app.form.browser.widget
import zope.app.pagetemplate.viewpagetemplatefile
import zope.cachedescriptors.property



class KeywordsWidget(zeit.cms.browser.widget.MultiObjectSequenceWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-widget.pt')

    def __init__(self, context, field, schema, request):
        # XXX make the tests pass. This widget is going to vanish soon (#8374)
        super(KeywordsWidget, self).__init__(context, None, request)

    def _toFieldValue(self, value):
        keywords = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        return tuple(keywords[code] for code in value if code in keywords)

    def _toFormValue(self, value):
        return value


class KeywordsDisplayWidget(
    zeit.cms.browser.widget.MultiObjectSequenceDisplayWidget):

    def __init__(self, context, field, schema, request):
        # XXX make the tests pass. This widget is going to vanish soon (#8374)
        super(KeywordsDisplayWidget, self).__init__(context, None, request)

    def get_value(self, value):
        return value
