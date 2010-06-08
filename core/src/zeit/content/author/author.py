# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.author.interfaces
import zope.interface


class Author(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.author.interfaces.IAuthor,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = (
        u'<author xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        u'</author>')

    title = zeit.cms.content.property.ObjectPathProperty('.title')
    firstname = zeit.cms.content.property.ObjectPathProperty('.firstname')
    lastname = zeit.cms.content.property.ObjectPathProperty('.lastname')
    vgwortid = zeit.cms.content.property.ObjectPathProperty('.vgwortid')

    display_name = zeit.cms.content.property.ObjectPathProperty(
        '.entered_display_name')
    computed_display_name = zeit.cms.content.property.ObjectPathProperty(
        '.display_name')


class AuthorType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Author
    interface = zeit.content.author.interfaces.IAuthor
    type = 'author'
    title = _('Author')
    addform = zeit.cms.type.SKIP_ADD


@grokcore.component.subscribe(
    zeit.content.author.interfaces.IAuthor,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def update_display_name(obj, event):
    if obj.display_name:
        obj.computed_display_name = obj.display_name
    else:
        obj.computed_display_name = u'%s %s' % (obj.firstname, obj.lastname)
