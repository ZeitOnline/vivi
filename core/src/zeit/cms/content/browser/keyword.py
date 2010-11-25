# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.tree
import zeit.cms.browser.widget
import zeit.cms.content.keyword
import zope.app.form.browser.widget
import zope.app.pagetemplate.viewpagetemplatefile
import zope.cachedescriptors.property


class Tree(zeit.cms.browser.tree.Tree):

    key = 'zeit.cms.content.keyword'
    root_name = 'root'

    def __call__(self):
        return self.index()

    @zope.cachedescriptors.property.Lazy
    def root(self):
        return zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords).root

    def isRoot(self, container):
        return container == self.root

    def getUniqueId(self, object):
        return object.code

    def selected(self, url):
        return False

    def getUrl(self, obj):
        return 'keyword://%s/%s' % (obj.code, obj.label)

    def getId(self, obj):
        return obj.code

    def getTitle(self, obj):
        return obj.label

    def listContainer(self, container):
        return container.narrower

    def expandable(self, obj):
        return bool(obj.narrower)

    def suggest_email(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        address = cms_config['suggest-keyword-email-address']
        subject = zope.i18n.translate(
            _('New keyword'), context=self.request)
        return 'mailto:%s?subject=%s' % (address, subject)

    def suggest_name(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.cms')
        return cms_config['suggest-keyword-real-name']


class KeywordsWidget(zeit.cms.browser.widget.MultiObjectSequenceWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-widget.pt')

    def _toFieldValue(self, value):
        keywords = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        return tuple(keywords[code] for code in value if code in keywords)

    def _toFormValue(self, value):
        return value


class KeywordsDisplayWidget(
    zeit.cms.browser.widget.MultiObjectSequenceDisplayWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-display-widget.pt')

    def _toFormValue(self, value):
        return value


class TypeaheadSearch(object):

    def __call__(self):
        self.request.response.setHeader('Cache-Control', 'max-age=3600');
        return self.index()

    def search(self, searchterm=None):
        if searchterm is None:
            return
        keywords = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        return sorted(keywords.find_keywords(searchterm),
                      key=lambda x: x.label)
