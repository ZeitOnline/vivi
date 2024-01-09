import lxml.objectify
import z3c.traverser.interfaces
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.publisher.interfaces
import zope.security.proxy

import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.content.article.interfaces


@zope.component.adapter(zeit.content.article.interfaces.IArticle)
@zope.interface.implementer(
    zeit.content.article.interfaces.IBookRecensionContainer, zope.location.interfaces.ILocation
)
class BookRecensionContainer(zeit.cms.content.xmlsupport.Persistent):
    def __init__(self, context):
        self.context = context
        self.__name__ = 'recensions'
        # set parent last so we don't trigger a write
        self.__parent__ = context

    def __getitem__(self, index):
        return self._create_recension(index, self.entries[index])

    def __iter__(self):
        for index, node in enumerate(self.entries):
            yield self._create_recension(index, node)

    def __len__(self):
        return len(self.entries)

    def append(self, recension):
        xml_repr = zeit.cms.content.interfaces.IXMLRepresentation(recension)
        self.xml['body'].append(xml_repr.xml)
        self._p_changed = True
        zope.event.notify(zope.lifecycleevent.ObjectAddedEvent(recension, self, recension.__name__))

    def remove(self, name):
        prefix, count = name.split()
        if prefix != self.__name__:
            raise KeyError('Invalid name: %r' % name)
        count = int(count)
        recension = self.entries[count]
        self.xml['body'].remove(recension)
        self._p_changed = True
        zope.event.notify(zope.lifecycleevent.ObjectRemovedEvent(recension, self, name))

    @property
    def entries(self):
        return lxml.objectify.ObjectPath('.body.{http://namespaces.zeit.de/bibinfo}entry').find(
            self.xml, ()
        )

    @property
    def xml(self):
        return zope.security.proxy.removeSecurityProxy(self.context.xml)

    def _create_recension(self, index, node):
        recension = BookRecension()
        recension.xml = node
        recension_classes = '%s %s' % (self.__name__, str(index))
        recension = zope.location.location.located(recension, self, recension_classes)
        # located() sets __parent__ first, so it has triggered a false write
        recension._p_changed = False
        return recension


@zope.interface.implementer(
    zeit.content.article.interfaces.IBookRecension, zope.location.interfaces.ILocation
)
class BookRecension(
    zeit.cms.content.xmlsupport.XMLRepresentationBase, zeit.cms.content.xmlsupport.Persistent
):
    """Information about a book in a recension."""

    default_template = (
        '<entry xmlns="http://namespaces.zeit.de/bibinfo" '
        'xmlns:py="http://codespeak.net/lxml/objectify/pytype" />'
    )

    authors = zeit.cms.content.property.SimpleMultiProperty('.auth-info.author')
    title = zeit.cms.content.property.ObjectPathProperty('.title')
    genre = zeit.cms.content.property.ObjectPathProperty('.genre')
    info = zeit.cms.content.property.ObjectPathProperty('.info')
    category = zeit.cms.content.property.ObjectPathProperty('.category')
    age_limit = zeit.cms.content.property.ObjectPathProperty('.agelimit')
    original_language = zeit.cms.content.property.ObjectPathProperty('.original_language')
    translator = zeit.cms.content.property.ObjectPathProperty('.translator')
    publisher = zeit.cms.content.property.ObjectPathProperty('.edition.publisher')
    location = zeit.cms.content.property.ObjectPathProperty('.edition.location')
    year = zeit.cms.content.property.ObjectPathProperty('.edition.year')
    media_type = zeit.cms.content.property.ObjectPathProperty('.edition.mediatype')
    pages = zeit.cms.content.property.ObjectPathProperty('.edition.pages')
    price = zeit.cms.content.property.ObjectPathProperty(
        '.edition.price', zeit.content.article.interfaces.IBookRecension['price']
    )

    raw_data = 'Wird noch nicht eingelesen.'  # XXX

    __parent__ = None
    __name__ = None


@zope.interface.implementer(z3c.traverser.interfaces.IPluggableTraverser)
class RecensionContainerTraverser:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        recensions = zeit.content.article.interfaces.IBookRecensionContainer(self.context)
        if name in recensions.__name__:  # XXX Is 'in' really what's meant?
            return recensions
        raise zope.publisher.interfaces.NotFound(self.context, name, request)


@zope.interface.implementer(z3c.traverser.interfaces.IPluggableTraverser)
class RecensionTraverser:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            index = int(name.split(' ')[1])
        except ValueError:
            pass
        else:
            try:
                return self.context[index]
            except IndexError:
                pass

        raise zope.publisher.interfaces.NotFound(self.context, name, request)


@zope.component.adapter(
    zeit.content.article.interfaces.IBookRecension, zope.lifecycleevent.IObjectAddedEvent
)
def set_has_recension(context, event):
    # XXX Recension does not provide ILocation, so we fudge a little to get to
    # the article
    article = event.newParent.__parent__
    article.has_recensions = True
