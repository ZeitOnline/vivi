from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.interfaces import IAuthor
import grokcore
import zeit.cms.content.interfaces
import zeit.cms.content.reference
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
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

    for name in [
        'biography',
        'display_name',
        'email',
        'entered_display_name',
        'external',
        'facebook',
        'firstname',
        'instagram',
        'lastname',
        'status',
        'title',
        'twitter',
        'vgwortcode',
        'vgwortid',
    ]:
        locals()[name] = ObjectPathProperty('.%s' % name, IAuthor[name])

    community_profile = zeit.cms.content.property.ObjectPathProperty(
        '.communityprofile')

    image_group = zeit.cms.content.reference.SingleResource(
        '.image_group', 'image')

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
    addform = 'zeit.content.author.add_contextfree'


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
                    'authorships' in description.attributes):
                ref_names = [x.target.display_name for x in obj.authorships]
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
        return [x.target for x in self.context.authorships]


@grokcore.component.adapter(
    zeit.cms.content.interfaces.ICommonMetadata,
    name='zeit.content.author')
@grokcore.component.implementer(
    zeit.cms.relation.interfaces.IReferenceProvider)
def references(context):
    return [x.target for x in context.authorships]


@grokcore.component.adapter(
    zeit.content.author.interfaces.IAuthor,
    zeit.cms.content.interfaces.IContentAdder)
@grokcore.component.implementer(zeit.cms.content.interfaces.IAddLocation)
def author_location(type_, adder):
    return zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
