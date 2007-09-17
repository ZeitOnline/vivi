# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import sys

import iso8601
import gocept.lxml.interfaces

import zope.component
import zope.event
import zope.schema.interfaces

import zc.sourcefactory.interfaces

import zeit.cms.interfaces
import zeit.cms.content.interfaces


logger = logging.getLogger('zeit.cms.content.dav')


class DAVProperty(object):
    """WebDAV properties."""

    def __init__(self, field, namespace, name):
        self.field = field
        self.namespace = namespace
        self.name = name

    def __get__(self, instance, class_):
        __traceback_info = (instance, )
        if instance is None:
            return self
        properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        dav_value = properties.get((self.name, self.namespace))
        if dav_value is None:
            value = self.field.default
        else:
            field = self.field.bind(instance)
            __traceback_info__ = (instance, field,
                                  field.__name__, dav_value)
            try:
                value = zeit.cms.content.interfaces.IFromProperty(
                    field).fromProperty(dav_value)
            except (ValueError, zope.schema.ValidationError), e:
                value = self.field.default
                logger.warning("Could not parse DAV property value %r for "
                               "%s.%s [%s: %s]. Using default %r instead" % (
                                   dav_value, instance.__class__.__name__,
                                   self.name, e.__class__.__name__, e, value))

        return value

    def __set__(self, instance, value):
        read_properties = zeit.cms.interfaces.IWebDAVReadProperties(instance)
        write_properties = zeit.cms.interfaces.IWebDAVWriteProperties(instance)
        field = self.field.bind(instance)
        dav_value = zeit.cms.content.interfaces.IToProperty(field).toProperty(
            value)
        old_value = read_properties.get((self.name, self.namespace))
        write_properties[(self.name, self.namespace)] = dav_value
        zope.event.notify(zeit.cms.content.interfaces.DAVPropertyChangedEvent(
            instance, self.namespace, self.name, old_value, dav_value))


class UnicodeProperty(object):

    zope.interface.implements(zeit.cms.content.interfaces.IFromProperty,
                              zeit.cms.content.interfaces.IToProperty)
    zope.component.adapts(zope.schema.interfaces.IFromUnicode)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        # Convert to unicode. We need to do that because lxml puts out an
        # ascii-str when the value has only 7bit characters. While this is an
        # optimisation in lxml we *need* a unicode here. If the value contains
        # 8 bit chars this is supposed to break.
        value = unicode(value)
        return self.context.fromUnicode(value)

    def toProperty(self, value):
        return unicode(value)


class ChoiceProperty(object):

    zope.interface.implements(zeit.cms.content.interfaces.IFromProperty,
                              zeit.cms.content.interfaces.IToProperty)
    zope.component.adapts(zope.schema.interfaces.IChoice)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        for possible_value in self.context.vocabulary:
            if zeit.cms.content.interfaces.IDAVToken(possible_value) == value:
                return possible_value
        # XXX what to do here?
        raise ValueError(value)

    def toProperty(self, value):
        return zeit.cms.content.interfaces.IDAVToken(value)


class BoolProperty(object):

    zope.interface.implements(zeit.cms.content.interfaces.IFromProperty,
                              zeit.cms.content.interfaces.IToProperty)
    zope.component.adapts(zope.schema.interfaces.IBool)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        if value.lower() in ('yes', 'true'):
            return True
        return False

    def toProperty(self, value):
        if value:
            return 'yes'
        return 'no'


class DatetimeProperty(object):

    zope.interface.implements(zeit.cms.content.interfaces.IFromProperty,
                              zeit.cms.content.interfaces.IToProperty)
    zope.component.adapts(zope.schema.interfaces.IDatetime)

    def __init__(self, context):
        self.context = context

    def fromProperty(self, value):
        if not value:
            return None
        try:
            return iso8601.parse_date(value)
        except iso8601.ParseError:
            return None

    def toProperty(self, value):
        if value is None:
            return u''
        return value.isoformat()


def mapProperties(interface, namespace, names):
    vars = sys._getframe(1).f_locals
    for name in names:
        field = interface[name]
        mapProperty(field, namespace, name, vars)


def mapProperty(field, namespace, name=None, vars=None):
    if vars is None:
        vars = sys._getframe(1).f_locals

    if name is None:
        name = field.__name__

    vars[name] = DAVProperty(field, namespace, name)
