# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import zope.app.form.browser.widget
import zope.app.form.browser.itemswidgets
import zope.app.pagetemplate.viewpagetemplatefile

import zeit.cms.repository.interfaces


TEMPLATE = u"""\
<div id="%(name)s">
    <input class="object-reference" type="hidden"
        name="%(name)s" value="%(value)s" />
    <span class="object-reference">%(value)s</span>
</div>
<script>new DropWidget("%(name)s");</script>
"""


class DropObjectWidget(zope.app.form.browser.widget.SimpleInputWidget):

    _missing = u"Objekt hier fallen lassen."

    def __call__(self):
        return TEMPLATE % {
            'name': self.name,
            'value': self._getFormValue(),
        }

    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value
        return self.repository.getContent(input)

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        return value.uniqueId

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class ObjectSequenceWidget(zope.app.form.browser.widget.SimpleInputWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'sequencewidget.pt')

    def __init__(self, context, field, request):
        super(ObjectSequenceWidget, self).__init__(context, request)
        self.field = field

    def __call__(self):
        return self.template()

    def hasInput(self):
        return self.name + '.count' in self.request.form

    def _getFormInput(self):
        count = int(self.request.get(self.name + '.count'))
        result = []
        for idx in range(count):
            result.append(self.request.get('%s.%s' % (self.name, idx)))
        return result

    def _toFieldValue(self, value):
        return tuple(self.repository.getContent(unique_id)
                     for unique_id in value)

    def _toFormValue(self, value):
        result = []
        for obj in value:
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                title = obj.uniqueId
            else:
                title = list_repr.title
            result.append(
                {'uniqueId': obj.uniqueId, 'title': title})
        return result

    @property
    def marker(self):
        count = len(self._getFormValue())
        return ('<input type="hidden" id="%s.count" name="%s.count" value="%d" />'
                % (self.name, self.name, count))

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
