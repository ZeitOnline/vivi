from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.interfaces import IAuthor
import UserDict
import grokcore.component as grok
import lxml.objectify
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
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
        'summary',
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

    favourite_content = zeit.cms.content.reference.MultiResource(
        '.favourites.reference', 'related')

    favourite_topics = zeit.cms.content.reference.MultiResource(
        '.topics.reference', 'related')

    @property
    def exists(self):
        query = zeit.find.search.query(
            fulltext='%s %s' % (self.firstname, self.lastname),
            types=('author',))
        return bool(zeit.find.search.search(query).hits)

    @property
    def bio_questions(self):
        return zeit.content.author.interfaces.IBiographyQuestions(self)


class AuthorType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Author
    interface = zeit.content.author.interfaces.IAuthor
    type = 'author'
    title = _('Author')
    addform = 'zeit.content.author.add_contextfree'


@grok.subscribe(
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
@grok.subscribe(
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


class Dependencies(grok.Adapter):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('zeit.content.author')
    grok.implements(zeit.workflow.interfaces.IPublicationDependencies)

    def __init__(self, context):
        self.context = context

    def get_dependencies(self):
        return [x.target for x in self.context.authorships]


@grok.adapter(
    zeit.cms.content.interfaces.ICommonMetadata,
    name='zeit.content.author')
@grok.implementer(
    zeit.cms.relation.interfaces.IReferenceProvider)
def references(context):
    return [x.target for x in context.authorships]


@grok.adapter(
    zeit.content.author.interfaces.IAuthor,
    zeit.cms.content.interfaces.IContentAdder)
@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
def author_location(type_, adder):
    return zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)


class BiographyQuestions(
        grok.Adapter,
        UserDict.DictMixin,
        zeit.cms.content.xmlsupport.Persistent):

    grok.context(zeit.content.author.interfaces.IAuthor)
    grok.implements(zeit.content.author.interfaces.IBiographyQuestions)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'xml', zope.security.proxy.getObject(
            context.xml))
        object.__setattr__(self, '__parent__', context)

    def __getitem__(self, key):
        node = self.xml.xpath('//question[@id="%s"]' % key)
        return Question(
            key, self.title(key), unicode(node[0]) if node else None)

    def __setitem__(self, key, value):
        node = self.xml.xpath('//question[@id="%s"]' % key)
        if node:
            self.xml.remove(node[0])
        if value:
            node = lxml.objectify.E.question(value, id=key)
            lxml.objectify.deannotate(node[0], cleanup_namespaces=True)
            self.xml.append(node)
        super(BiographyQuestions, self).__setattr__('_p_changed', True)

    def keys(self):
        return list(zeit.content.author.interfaces.BIOGRAPHY_QUESTIONS(self))

    def title(self, key):
        return zeit.content.author.interfaces.BIOGRAPHY_QUESTIONS(
            self).title(key)

    # Attribute-style access to answers is meant only for zope.formlib.
    # XXX Why does this work without an explicit security declaration?

    def __getattr__(self, key):
        return self.get(key).answer

    def __setattr__(self, key, value):
        self[key] = value


class Question(object):

    zope.interface.implements(zeit.content.author.interfaces.IQuestion)

    def __init__(self, id, title, answer):
        self.id = id
        self.title = title
        self.answer = answer
