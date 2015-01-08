from zeit.cms.i18n import MessageFactory as _
import UserDict
import gocept.lxml.interfaces
import grokcore.component as grok
import pkg_resources
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.type
import zeit.edit.container
import zeit.edit.interfaces
import zeit.newsletter.interfaces
import zope.component
import zope.interface


BODY_NAME = 'newsletter_body'


class Newsletter(zeit.cms.content.xmlsupport.XMLContentBase,
                 UserDict.DictMixin):

    zope.interface.implements(zeit.newsletter.interfaces.INewsletter)

    default_template = pkg_resources.resource_string(__name__, 'template.xml')

    subject = zeit.cms.content.property.ObjectPathProperty(
        '.head.subject', zeit.newsletter.interfaces.INewsletter['subject'])

    def keys(self):
        return [BODY_NAME]

    def __getitem__(self, key):
        if key == BODY_NAME:
            area = zope.component.getMultiAdapter(
                (self, self.xml.body),
                zeit.edit.interfaces.IArea,
                name=key)
            return zope.container.contained.contained(area, self, key)
        raise KeyError(key)

    @property
    def body(self):
        return self[BODY_NAME]

    def send(self):
        self._send()
        category = zeit.newsletter.interfaces.INewsletterCategory(self)
        category.last_created = zope.dublincore.interfaces.IDCTimes(
            self).created

    def send_test(self, to):
        self._send(to)

    def _send(self, to=None):
        category = zeit.newsletter.interfaces.INewsletterCategory(self)
        renderer = zope.component.getUtility(
            zeit.newsletter.interfaces.IRenderer)
        rendered = renderer(self)
        optivo = zope.component.getUtility(zeit.optivo.interfaces.IOptivo)
        if to is None:
            optivo.send(
                category.mandant, category.recipientlist,
                self.subject, rendered['html'], rendered['text'])
        else:
            optivo.test(
                category.mandant, category.recipientlist_test,
                to, u'[test] ' + self.subject,
                rendered['html'], rendered['text'])


class NewsletterType(zeit.cms.type.XMLContentTypeDeclaration):

    factory = Newsletter
    interface = zeit.newsletter.interfaces.INewsletter
    type = 'newsletter'
    title = _('Daily Newsletter')  # multiple categories are not supported yet


@grok.adapter(zeit.newsletter.interfaces.INewsletter)
@grok.implementer(zeit.newsletter.interfaces.INewsletterCategory)
def category_for_newsletter(context):
    if zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
        context = zeit.cms.interfaces.ICMSContent(context.uniqueId)
    candidate = context.__parent__
    while candidate:
        if zeit.newsletter.interfaces.INewsletterCategory.providedBy(
                candidate):
            return candidate
        candidate = candidate.__parent__


class Body(zeit.edit.container.TypeOnAttributeContainer,
           grok.MultiAdapter):

    __name__ = BODY_NAME

    grok.implements(zeit.newsletter.interfaces.IBody)
    grok.provides(zeit.newsletter.interfaces.IBody)
    grok.adapts(
        zeit.newsletter.interfaces.INewsletter,
        gocept.lxml.interfaces.IObjectified)
    grok.name(BODY_NAME)

    def values(self):
        # We re-implement values() so it works without keys(), since those are
        # not present in the repository, but since e.g. zeit.frontend is only
        # interested in the values, anyway, this works out alright.
        result = []
        for node in self.xml.iterchildren():
            result.append(self._get_element_for_node(node))
        return result


class Group(zeit.edit.container.TypeOnAttributeContainer,
            grok.MultiAdapter):

    grok.implements(zeit.newsletter.interfaces.IGroup)
    grok.provides(zeit.newsletter.interfaces.IGroup)
    grok.adapts(
        zeit.newsletter.interfaces.IBody,
        gocept.lxml.interfaces.IObjectified)
    grok.name('group')

    title = zeit.cms.content.property.ObjectPathProperty(
        '.head.title', zeit.newsletter.interfaces.IGroup['title'])

    def values(self):
        # We re-implement values() so it works without keys(), since those are
        # not present in the repository, but since e.g. zeit.frontend is only
        # interested in the values, anyway, this works out alright.
        result = []
        for node in self.xml.xpath('container'):
            result.append(self._get_element_for_node(node))
        return result


zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IBody, 'group', _('Group'),
    tag_name='region')


class Teaser(zeit.edit.block.SimpleElement):

    area = zeit.newsletter.interfaces.IGroup
    grok.implements(zeit.newsletter.interfaces.ITeaser)
    type = 'teaser'

    reference = zeit.cms.content.property.SingleResource(
        '.block', xml_reference_name='related', attributes=('href',))


zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IGroup, 'teaser', _('Teaser'))


class AdvertisementBase(object):

    area = zeit.newsletter.interfaces.IBody
    type = NotImplemented

    @property
    def category(self):
        nl = zeit.newsletter.interfaces.INewsletter(self)
        return zeit.newsletter.interfaces.INewsletterCategory(nl)

    @property
    def position(self):
        return self.type.replace('advertisement-', '')

    @property
    def href(self):
        return getattr(self.category, 'ad_%s_href' % self.position)

    @property
    def title(self):
        return getattr(self.category, 'ad_%s_title' % self.position)

    @property
    def text(self):
        return getattr(self.category, 'ad_%s_text' % self.position)

    @property
    def image(self):
        return getattr(self.category, 'ad_%s_image' % self.position)


class MiddleAdvertisement(zeit.edit.block.SimpleElement, AdvertisementBase):

    # XXX Putting implements on AdvertisementBase breaks during grokking, why?
    grok.implements(zeit.newsletter.interfaces.IAdvertisement)
    type = 'advertisement-middle'


class ThisWeeksAdvertisement(zeit.edit.block.SimpleElement, AdvertisementBase):

    # XXX Putting implements on AdvertisementBase breaks during grokking, why?
    grok.implements(zeit.newsletter.interfaces.IAdvertisement)
    type = 'advertisement-thisweeks'


class BottomAdvertisement(zeit.edit.block.SimpleElement, AdvertisementBase):

    grok.implements(zeit.newsletter.interfaces.IAdvertisement)
    type = 'advertisement-bottom'


zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IBody, 'advertisement-middle',
    _('Advertisement'))
zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IBody, 'advertisement-thisweeks',
    _('Advertisement'))
zeit.edit.block.register_element_factory(
    zeit.newsletter.interfaces.IBody, 'advertisement-bottom',
    _('Advertisement'))


@grok.adapter(zeit.edit.interfaces.IElement)
@grok.implementer(zeit.newsletter.interfaces.INewsletter)
def newsletter_for_element(context):
    return zeit.newsletter.interfaces.INewsletter(
        getattr(context, '__parent__', None), None)
