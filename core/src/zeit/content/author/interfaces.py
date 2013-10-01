# coding: utf-8
# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import re
import zeit.cms.content.sources
import zope.interface
import zope.schema


class StatusSource(zeit.cms.content.sources.SimpleFixedValueSource):

    values = (u'Print', u'Online', u'Reader')


class InvalidCode(zope.schema.ValidationError):
    __doc__ = _('Code contains invalid characters')


valid_vgwortcode_regex = re.compile(r'^[A-Za-z]+$').match


def valid_vgwortcode(value):
    if not valid_vgwortcode_regex(value):
        raise InvalidCode(value)
    return True


class IAuthor(zope.interface.Interface):

    title = zope.schema.TextLine(title=_('Title'), required=False)
    firstname = zope.schema.TextLine(title=_('Firstname'))
    lastname = zope.schema.TextLine(title=_('Lastname'))
    email = zope.schema.TextLine(title=_('Email address'), required=False)
    vgwortid = zope.schema.Int(
        title=_('VG-Wort ID'),
        required=False,
        # see messageService.wsdl:cardNumberType
        min=10, max=9999999)

    vgwortcode = zope.schema.TextLine(
        title=_('VG-Wort Code'), required=False,
        constraint=valid_vgwortcode)

    display_name = zope.interface.Attribute(
        'The computed display name. Default is "firstname lastname",'
        ' a user entered value takes precedence.')
    entered_display_name = zope.schema.TextLine(
        title=_('Display name'),
        required=False,
        description=_(u"Default: 'Firstname Lastname'"))

    community_profile = zope.schema.TextLine(
        title=_('Community-Profile URL'), required=False)

    status = zope.schema.Choice(
        title=_(u'Redaktionszugehörigkeit'),
        source=StatusSource())

    external = zope.schema.Bool(
        title=_(u'External?'))
