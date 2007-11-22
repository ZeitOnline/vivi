# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface
import zope.schema

import zope.app.form.browser.interfaces
import zope.app.form.browser.widget
import zope.app.form.browser.itemswidgets
import zope.app.pagetemplate.viewpagetemplatefile

import zeit.cms.repository.interfaces


class ObjectReferenceWidget(zope.app.form.browser.widget.SimpleInputWidget):

    _missing = u""
    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'object-reference-widget.pt')

    def __call__(self):
        return self.template()

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


@zope.component.adapter(
    zope.schema.interfaces.ITuple,
    zope.schema.interfaces.IObject,
    zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zope.app.form.interfaces.IInputWidget)
def objectWidgetMultiplexer(context, field, request):
    return zope.component.getMultiAdapter(
        (context, field, field.schema, request),
        zope.app.form.interfaces.IInputWidget)


@zope.component.adapter(
    zope.schema.interfaces.ITuple,
    zope.schema.interfaces.IObject,
    zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zope.app.form.interfaces.IDisplayWidget)
def objectDisplayWidgetMultiplexer(context, field, request):
    return zope.component.getMultiAdapter(
        (context, field, field.schema, request),
        zope.app.form.interfaces.IDisplayWidget)


class ObjectSequenceWidgetBase(object):

    def _toFormValue(self, value):
        result = []
        for obj in value:
            list_repr = zope.component.queryMultiAdapter(
                (obj, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                title = obj.uniqueId
                url = None
            else:
                title = list_repr.title
                url = list_repr.url
            result.append(
                {'uniqueId': obj.uniqueId,
                 'title': title,
                 'url': url})
        return result


class ObjectSequenceWidget(
    ObjectSequenceWidgetBase,
    zope.app.form.browser.widget.SimpleInputWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'objectsequence-edit-widget.pt')

    def __init__(self, context, field, schema, request):
        super(ObjectSequenceWidget, self).__init__(context, request)
        self.field = field
        self.schema = schema

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

    @property
    def marker(self):
        count = len(self._getFormValue())
        return ('<input type="hidden" id="%s.count" name="%s.count" value="%d" />'
                % (self.name, self.name, count))

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class ObjectSequenceDisplayWidget(
    ObjectSequenceWidgetBase,
    zope.app.form.browser.widget.DisplayWidget):

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        'objectsequence-display-widget.pt')

    def __init__(self, context, field, schema, request):
        super(ObjectSequenceDisplayWidget, self).__init__(context, request)
        self.field = field
        self.schema = schema

    def __call__(self):
        return self.template()

    def get_values(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        return self._toFormValue(value)
