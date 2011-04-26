# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zope.interface
import zope.schema


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

    display_name = zope.interface.Attribute(
        'The computed display name. Default is "firstname lastname",'
        ' a user entered value takes precedence.')
    entered_display_name = zope.schema.TextLine(
        title=_('Display name'),
        required=False,
        description=_(u"Default: 'Firstname Lastname'"))
