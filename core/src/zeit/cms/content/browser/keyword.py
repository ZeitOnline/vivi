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

    @zope.cachedescriptors.property.Lazy
    def root(self):
        return zeit.cms.content.keyword.keyword_root_factory()

    def isRoot(self, container):
        return container == self.root

    def getUniqueId(self, object):
        return object.code

    def selected(self, url):
        return False

    def getUrl(self, obj):
        return ''

    def getId(self, obj):
        return obj.code

    def getTitle(self, obj):
        return obj.label

    def listContainer(self, container):
        return container.narrower


class KeywordsWidget(zeit.cms.browser.widget.ObjectSequenceWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'keyword-widget.pt')

    def _toFieldValue(self, value):
        # XXX
        return tuple(self.repository.getContent(unique_id)
                     for unique_id in value)

    def _toFormValue(self, value):
        return value
