import collections.abc
import urllib.parse

from requests.exceptions import RequestException
import grokcore.component as grok
import lxml.builder
import requests
import zope.interface
import zope.lifecycleevent
import zope.security.proxy

from zeit.cms.content.property import ObjectPathProperty
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import META_SCHEMA_NS
from zeit.connector.search import SearchVar
from zeit.content.author.interfaces import IAuthor
import zeit.cms.config
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.cms.related.related
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.cms.workflow.dependency
import zeit.content.author.interfaces
import zeit.content.image.imagereference
import zeit.find.interfaces


AUTHOR_NS = 'http://namespaces.zeit.de/CMS/author'
TYPE = SearchVar('type', META_SCHEMA_NS)
FIRSTNAME = SearchVar('firstname', AUTHOR_NS)
LASTNAME = SearchVar('lastname', AUTHOR_NS)
HDOK_ID = SearchVar('hdok_id', AUTHOR_NS)


@zope.interface.implementer(zeit.content.author.interfaces.IAuthor, zeit.cms.interfaces.IAsset)
class Author(zeit.cms.content.xmlsupport.XMLContentBase):
    default_template = '<author></author>'

    for name in [
        'additional_contact_title',
        'additional_contact_content',
        'biography',
        'email',
        'sso_connect',
        'enable_followpush',
        'enable_feedback',
        'facebook',
        'instagram',
        'jabber',
        'occupation',
        'pgp',
        'show_letterbox_link',
        'signal',
        'summary',
        'threema',
        'title',
        'topiclink_label_1',
        'topiclink_label_2',
        'topiclink_label_3',
        'topiclink_url_1',
        'topiclink_url_2',
        'topiclink_url_3',
        'twitter',
        'website',
    ]:
        locals()[name] = ObjectPathProperty(f'.{name}', IAuthor[name])

    for name in [
        'firstname',
        'lastname',
        'initials',
        'ssoid',
    ]:
        locals()[name] = ObjectPathProperty(
            f'.{name}', IAuthor[name], dav_ns=AUTHOR_NS, dav_name=name, dav_toggle='wcm_26'
        )

    # BBB Diverging xpaths are for existing bodies, remove after WCM-26 is launched.
    for name, xpath in [
        ('department', 'status'),
        ('hdok_id', 'honorar_id'),
        ('vgwort_id', 'vgwortid'),
        ('vgwort_code', 'vgwortcode'),
    ]:
        locals()[name] = ObjectPathProperty(
            f'.{xpath}', IAuthor[name], dav_ns=AUTHOR_NS, dav_name=name, dav_toggle='wcm_26'
        )
    del locals()['name']
    del locals()['xpath']

    @property
    def display_name(self):
        if self._display_name:
            return self._display_name
        else:
            return f'{self.firstname} {self.lastname}'

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    _display_name = ObjectPathProperty(
        '.display_name',
        IAuthor['display_name'],
        dav_ns=AUTHOR_NS,
        dav_name='display_name',
        dav_toggle='wcm_26',
    )

    favourite_content = zeit.cms.content.reference.MultiResource('.favourites.reference', 'related')

    @classmethod
    def exists(cls, firstname, lastname):
        if FEATURE_TOGGLES.find('xmlproperty_read_wcm_26'):
            connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
            result = list(
                connector.search(
                    [TYPE, FIRSTNAME, LASTNAME],
                    (TYPE == 'author') & (FIRSTNAME == firstname) & (LASTNAME == lastname),
                )
            )
            return bool(result)
        else:
            elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
            return bool(
                elastic.search(
                    {
                        'query': {
                            'bool': {
                                'filter': [
                                    {'term': {'doc_type': 'author'}},
                                    {'term': {'payload.xml.firstname': firstname}},
                                    {'term': {'payload.xml.lastname': lastname}},
                                ]
                            }
                        }
                    }
                ).hits
            )

    @classmethod
    def find_by_hdok_id(cls, hdok_id):
        if FEATURE_TOGGLES.find('xmlproperty_read_wcm_26'):
            connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
            result = list(
                connector.search(
                    [TYPE, HDOK_ID],
                    (TYPE == 'author') & (HDOK_ID == hdok_id),
                )
            )
            return result[0] if result else None
        else:
            elastic = zope.component.getUtility(zeit.find.interfaces.ICMSSearch)
            result = elastic.search(
                {
                    'query': {
                        'bool': {
                            'filter': [
                                {'term': {'doc_type': 'author'}},
                                # BBB for existing indexed documents.
                                {'term': {'payload.xml.honorar_id': hdok_id}},
                            ]
                        }
                    },
                    '_source': ['url', 'payload.xml'],
                }
            )
            return None if not result.hits else result[0]

    @property
    def bio_questions(self):
        return zeit.content.author.interfaces.IBiographyQuestions(self)


class AuthorType(zeit.cms.type.XMLContentTypeDeclaration):
    factory = Author
    interface = zeit.content.author.interfaces.IAuthor
    type = 'author'
    title = _('Author')
    addform = 'zeit.content.author.lookup'


@zope.component.adapter(zeit.content.author.interfaces.IAuthor)
@zope.interface.implementer(zeit.content.image.interfaces.IImages)
class AuthorImages(zeit.content.image.imagereference.ImagesAdapter):
    _image = zeit.cms.content.reference.SingleReferenceProperty('.image_group', 'image')


@grok.subscribe(
    zeit.content.author.interfaces.IAuthor, zeit.cms.repository.interfaces.IBeforeObjectAddEvent
)
def set_ssoid(obj, event):
    if obj.email and obj.sso_connect:
        ssoid = request_acs(obj.email)
        if ssoid:
            obj.ssoid = ssoid
    else:
        obj.ssoid = None


@grok.subscribe(zeit.content.author.interfaces.IAuthor, zope.lifecycleevent.IObjectModifiedEvent)
def update_ssoid(context, event):
    for desc in event.descriptions:
        if (
            desc.interface is zeit.cms.content.interfaces.ICommonMetadata
            and 'sso_connect'
            or 'email' in desc.attributes
        ):
            if context.sso_connect and context.email:
                ssoid = request_acs(context.email)
                if ssoid:
                    context.ssoid = ssoid
            else:
                context.ssoid = None
            break


def request_acs(email):
    config = zeit.cms.config.package('zeit.content.author')
    url = config['sso-api-url'] + '/users/' + urllib.parse.quote(email.encode('utf8'))
    auth = (config['sso-user'], config['sso-password'])
    try:
        r = requests.get(url, auth=auth)
        r.raise_for_status()
        return r.json().get('id', None)
    except RequestException:
        return None


@grok.subscribe(
    zeit.content.author.interfaces.IAuthor, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def create_honorar_on_checkin(context, event):
    if event.publishing:  # Prevent creating hdok entries during retract.
        return
    _create_honorar_entry(context)


@grok.subscribe(zeit.content.author.interfaces.IAuthor, zope.lifecycleevent.IObjectCreatedEvent)
def create_honorar_on_add(context, event):
    _create_honorar_entry(context)


def _create_honorar_entry(author):
    if author.hdok_id:
        return
    api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
    author.hdok_id = api.create(
        {
            'vorname': author.firstname,
            'nachname': author.lastname,
            'anlageAssetId': author.uniqueId,
        }
    )


class Dependencies(zeit.cms.workflow.dependency.DependencyBase):
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


@grok.adapter(zeit.content.author.interfaces.IAuthor, zeit.cms.content.interfaces.IContentAdder)
@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
def author_location(type_, adder):
    return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)


@grok.implementer(zeit.content.author.interfaces.IBiographyQuestions)
class BiographyQuestions(
    grok.Adapter, collections.abc.MutableMapping, zeit.cms.content.xmlsupport.Persistent
):
    grok.context(zeit.content.author.interfaces.IAuthor)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)
        object.__setattr__(self, 'xml', zope.security.proxy.getObject(context.xml))
        object.__setattr__(self, '__parent__', context)

    def __getitem__(self, key):
        node = self.xml.xpath(f'//question[@id="{key}"]')
        return Question(key, self.title(key), node[0].text if node else None)

    def __setitem__(self, key, value):
        node = self.xml.xpath(f'//question[@id="{key}"]')
        if node:
            self.xml.remove(node[0])
        if value:
            node = lxml.builder.E.question(value, id=key)
            self.xml.append(node)
        super().__setattr__('_p_changed', True)

    def keys(self):
        return list(zeit.content.author.interfaces.BIOGRAPHY_QUESTIONS(self))

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        raise NotImplementedError()

    def title(self, key):
        return zeit.content.author.interfaces.BIOGRAPHY_QUESTIONS(self).title(key)

    # Attribute-style access to answers is meant only for zope.formlib.
    # This works without an explicit security declaration, since we are not
    # security-wrapped ourselves, only our context is, and we bypass that for
    # XML access.

    def __getattr__(self, key):
        return self.get(key).answer

    def __setattr__(self, key, value):
        self[key] = value


@zope.interface.implementer(zeit.content.author.interfaces.IQuestion)
class Question:
    def __init__(self, id, title, answer):
        self.id = id
        self.title = title
        self.answer = answer
