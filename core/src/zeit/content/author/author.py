from requests.exceptions import RequestException
from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.i18n import MessageFactory as _
from zeit.content.author.interfaces import IAuthor
import UserDict
import grokcore.component as grok
import lxml.objectify
import requests
import urllib
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.related.related
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.content.author.interfaces
import zeit.find.interfaces
import zeit.workflow.dependency
import zope.interface
import zope.security.proxy


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
        'sso_connect',
        'ssoid',
        'enable_followpush',
        'enable_feedback',
        'entered_display_name',
        'external',
        'facebook',
        'firstname',
        'honorar_id',
        'instagram',
        'initials',
        'lastname',
        'occupation',
        'show_letterbox_link',
        'status',
        'summary',
        'title',
        'topiclink_label_1',
        'topiclink_label_2',
        'topiclink_label_3',
        'topiclink_url_1',
        'topiclink_url_2',
        'topiclink_url_3',
        'twitter',
        'vgwortcode',
        'vgwortid',
    ]:
        locals()[name] = ObjectPathProperty('.%s' % name, IAuthor[name])

    community_profile = zeit.cms.content.property.ObjectPathProperty(
        '.communityprofile')

    favourite_content = zeit.cms.content.reference.MultiResource(
        '.favourites.reference', 'related')

    @property
    def exists(self):
        elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
        return bool(elastic.search({'query': {'bool': {'filter': [
            {'term': {'doc_type': 'author'}},
            {'term': {'payload.xml.firstname': self.firstname}},
            {'term': {'payload.xml.lastname': self.lastname}},
        ]}}}).hits)

    @property
    def bio_questions(self):
        return zeit.content.author.interfaces.IBiographyQuestions(self)

    @property
    def image_group(self):
        # BBB Deprecated in favor of a separate images adapter
        return zeit.content.image.interfaces.IImages(self).image


class AuthorType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Author
    interface = zeit.content.author.interfaces.IAuthor
    type = 'author'
    title = _('Author')
    addform = 'zeit.content.author.add_contextfree'


class AuthorImages(zeit.cms.related.related.RelatedBase):

    zope.component.adapts(zeit.content.author.interfaces.IAuthor)
    zope.interface.implements(zeit.content.image.interfaces.IImages)

    image = zeit.cms.content.reference.SingleResource('.image_group', 'image')

    fill_color = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.image_group', 'fill_color',
        zeit.content.image.interfaces.IImages['fill_color'])


@grok.subscribe(
    zeit.content.author.interfaces.IAuthor,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def update_display_name(obj, event):
    if obj.entered_display_name:
        obj.display_name = obj.entered_display_name
    else:
        obj.display_name = u'%s %s' % (obj.firstname, obj.lastname)


@grok.subscribe(
    zeit.content.author.interfaces.IAuthor,
    zeit.cms.repository.interfaces.IBeforeObjectAddEvent)
def set_ssoid(obj, event):
    if obj.email and obj.sso_connect:
        ssoid = request_acs(obj.email)
        if ssoid:
            obj.ssoid = ssoid
    else:
        obj.ssoid = None


@grok.subscribe(
    zeit.content.author.interfaces.IAuthor,
    zope.lifecycleevent.IObjectModifiedEvent)
def update_ssoid(context, event):
    for desc in event.descriptions:
        if (desc.interface is zeit.cms.content.interfaces.ICommonMetadata and
                'sso_connect' or 'email' in desc.attributes):
            if context.sso_connect and context.email:
                ssoid = request_acs(context.email)
                if ssoid:
                    context.ssoid = ssoid
            else:
                context.ssoid = None
            break


def request_acs(email):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.author')
    url = config['sso-api-url'] + '/users/' + urllib.quote(
        email.encode('utf8'))
    auth = (config['sso-user'], config['sso-password'])
    try:
        r = requests.get(url, auth=auth)
        r.raise_for_status()
        return r.json().get('id', None)
    except RequestException:
        return None


# Note: This is needed by the publisher and zeit.vgwort, among others.
# Publisher only indexes the freetext field at the moment.
# zeit.vgwort.report uses the fact that the references to author objects are
# copied to the freetext 'author' webdav property to filter out which content
# objects to report.
def update_author_freetext(content):
    content.authors = [x.target.display_name for x in content.authorships]


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def update_freetext_on_change(context, event):
    if event.descriptions:
        for description in event.descriptions:
            if (issubclass(description.interface,
                zeit.cms.content.interfaces.ICommonMetadata) and
                    'authorships' in description.attributes):
                update_author_freetext(context)


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.interfaces.IObjectCreatedEvent)
def update_freetext_on_add(context, event):
    # ObjectCopied inherits from ObjectCreated
    if zeit.cms.repository.interfaces.IRepositoryContent.providedBy(context):
        return
    update_author_freetext(context)


class Dependencies(zeit.workflow.dependency.DependencyBase):
    """When content is published, make sure that all author objects
    referenced by it are also available to the published content.
    """

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('zeit.content.author')

    def get_dependencies(self):
        result = []
        for ref in self.context.authorships:
            author = ref.target
            if not zeit.cms.workflow.interfaces.IPublishInfo(author).published:
                result.append(author)
        return result


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


@grok.implementer(zeit.content.author.interfaces.IBiographyQuestions)
class BiographyQuestions(
        grok.Adapter,
        UserDict.DictMixin,
        zeit.cms.content.xmlsupport.Persistent):

    grok.context(zeit.content.author.interfaces.IAuthor)

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
    # This works without an explicit security declaration, since we are not
    # security-wrapped ourselves, only our context is, and we bypass that for
    # XML access.

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
