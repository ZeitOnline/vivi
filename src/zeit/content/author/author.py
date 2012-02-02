# Copyright (c) 2010-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.type
import zeit.content.author.interfaces
import zeit.find.search
import zeit.workflow.interfaces
import zope.interface


class Author(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(zeit.content.author.interfaces.IAuthor,
                              zeit.cms.interfaces.IAsset)

    default_template = (
        u'<author xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        u'</author>')

    title = zeit.cms.content.property.ObjectPathProperty('.title')
    firstname = zeit.cms.content.property.ObjectPathProperty('.firstname')
    lastname = zeit.cms.content.property.ObjectPathProperty('.lastname')
    email = zeit.cms.content.property.ObjectPathProperty('.email')
    vgwortid = zeit.cms.content.property.ObjectPathProperty('.vgwortid')
    vgwortcode = zeit.cms.content.property.ObjectPathProperty('.vgwortcode')

    display_name = zeit.cms.content.property.ObjectPathProperty(
        '.display_name')
    entered_display_name = zeit.cms.content.property.ObjectPathProperty(
        '.entered_display_name')

    status = zeit.cms.content.property.ObjectPathProperty('.status')

    @property
    def exists(self):
        query = zeit.find.search.query(
            fulltext='%s %s' % (self.firstname, self.lastname),
            types=('author',))
        return bool(zeit.find.search.search(query).hits)


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
    if obj.entered_display_name:
        obj.display_name = obj.entered_display_name
    else:
        obj.display_name = u'%s %s' % (obj.firstname, obj.lastname)


# Note: This is needed by zeit.vgwort, among others.
# zeit.vgwort.report uses the fact that the references to author objects are
# copied to the freetext 'author' webdav property to filter out which content
# objects to report.
@grokcore.component.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def update_author_freetext(obj, event):
    if event.descriptions:
        for description in event.descriptions:
            if (description.interface ==
                zeit.cms.content.interfaces.ICommonMetadata and
                'author_references' in description.attributes):
                ref_names = [x.display_name for x in obj.author_references]
                obj.authors = ref_names


class Dependencies(grokcore.component.Adapter):

    grokcore.component.context(
        zeit.cms.content.interfaces.ICommonMetadata)
    grokcore.component.name('zeit.content.author')
    grokcore.component.implements(
        zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        return self.context.author_references


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata,
    name='zeit.content.author')
@grokcore.component.implementer(
    zeit.cms.relation.interfaces.IReferenceProvider)
def references(context):
    return context.author_references
