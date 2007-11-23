# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.cachedescriptors.property

import zope.app.form.browser.widget
import zope.app.pagetemplate.viewpagetemplatefile

import zeit.cms.browser.tree
import zeit.cms.content.keyword
import zeit.cms.browser.widget


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


class KeywordsWidget(zeit.cms.browser.widget.MultiObjectSequenceWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-widget.pt')

    def _toFieldValue(self, value):
        keywords = zope.component.getUtility(
            zeit.cms.content.interfaces.IKeywords)
        return tuple(keywords[code] for code in value)

    def _toFormValue(self, value):
        return value


class KeywordsDisplayWidget(
    zeit.cms.browser.widget.MultiObjectSequenceDisplayWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-display-widget.pt')

    def _toFormValue(self, value):
        return value
