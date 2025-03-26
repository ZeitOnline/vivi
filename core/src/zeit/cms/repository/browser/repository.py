import hashlib

import grokcore.component as grok
import zope.cachedescriptors.property
import zope.component
import zope.i18n
import zope.publisher.interfaces
import zope.viewlet.viewlet

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.browser.tree
import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


class Repository:
    def __call__(self):
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)


@grok.adapter(zeit.cms.repository.interfaces.IRepository)
@grok.implementer(zeit.cms.browser.interfaces.IAdditionalLayer)
def layer_for_repository(context):
    return zeit.cms.browser.interfaces.IRepositoryLayer


@grok.adapter(
    zeit.cms.repository.interfaces.IRepository, zope.publisher.interfaces.IPublisherRequest
)
@grok.implementer(zope.publisher.interfaces.IPublishTraverse)
class Traverser(grok.MultiAdapter):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        """Do not traverse into individual folders, instead resolve the desired
        content object in a single operation."""
        stack = request._traversal_stack
        path = [name]
        i = len(stack) - 1
        while i >= 0:
            item = stack[i]
            if item[:1] in '@+':  # see zope.app.publication.ZopePublication:traverseName
                break
            path.append(item)
            request._traversed_names.append(item)
            stack.pop(i)
            i -= 1
        try:
            return self.context.getContent('http://xml.zeit.de/' + '/'.join(path))
        except KeyError:
            raise zope.publisher.interfaces.NotFound(self.context, name)


class HTMLTree(zope.viewlet.viewlet.ViewletBase, zeit.cms.browser.view.Base):
    """view class for navtree"""

    def render(self):
        return self.index()

    @zope.cachedescriptors.property.Lazy
    def tree_view(self):
        return zope.component.getMultiAdapter((self.repository, self.request), name='tree.html')

    @property
    def tree_url(self):
        preferences = zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(self.request.principal)
        )
        hash_ = hashlib.md5(usedforsecurity=False)
        for container in preferences.get_hidden_containers():
            hash_.update(container.encode('utf-8'))
        hash_.update('TREE'.encode('utf-8'))
        for container in sorted(self.tree_view.treeState):
            hash_.update(container.encode('utf-8'))
        return '%s/++noop++%s/@@tree.html' % (self.url(self.repository), hash_.hexdigest())

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        """repository representing the root of the tree"""
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)


class Tree(zeit.cms.browser.tree.Tree):
    """Repository Tree"""

    root_name = 'Repository'
    key = __module__ + '.Tree'

    def __call__(self):
        response = self.request.response
        response.setHeader('Cache-Control', 'private; max-age=360')
        return super().__call__()

    def listContainer(self, container):
        for obj in sorted(container.values(), key=zeit.cms.content.interfaces.IContentSortKey):
            if not zeit.cms.repository.interfaces.ICollection.providedBy(obj):
                continue
            if self.preferences.is_hidden(obj) and not self.selected(self.getUrl(obj)):
                continue
            yield obj

    @zope.cachedescriptors.property.Lazy
    def root(self):
        """repository representing the root of the tree"""
        return zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)

    def isRoot(self, container):
        return zeit.cms.repository.interfaces.IRepository.providedBy(container)

    def getUniqueId(self, object):
        if self.isRoot(object):
            return None
        return object.uniqueId

    def selected(self, url):
        view_url = self.request.get('view_url')
        if not view_url:
            view_url = self.request.getURL()

        application_url = self.request.getApplicationURL()
        view_path = view_url[len(application_url) :].split('/')
        path = url[len(application_url) :].split('/')

        while view_path[-1].startswith('@@'):
            view_path.pop()

        if path > view_path:
            return False

        return view_path[: len(path)] == path

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(self.request.principal)
        )

    def expanded(self, obj):
        if self.request.form.get('autoexpand-tree'):
            url = self.getUrl(obj)
            if self.selected(url):
                return True
        return super().expanded(obj)


class HiddenCollections(zeit.cms.browser.view.Base):
    def hide_collection(self):
        self.add_to_preference()
        self.send_message(
            _(
                '"${name}" is now hidden from the navigation tree.',
                mapping={'name': self.context.__name__},
            )
        )
        return self.redirect()

    def show_collection(self):
        self.remove_from_preference()
        self.send_message(
            _(
                '"${name}" is now shown in the navigation tree.',
                mapping={'name': self.context.__name__},
            )
        )
        return self.redirect()

    def redirect(self):
        self.request.response.redirect(self.url(self.context))

    def add_to_preference(self):
        self.preferences.hide_container(self.context)

    def remove_from_preference(self):
        self.preferences.show_container(self.context)

    @property
    def hidden(self):
        return self.preferences.is_hidden(self.context)

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zeit.cms.repository.interfaces.IUserPreferences(
            zeit.cms.workingcopy.interfaces.IWorkingcopy(self.request.principal)
        )


class RedirectToObjectWithUniqueId(zeit.cms.browser.view.Base):
    def __call__(self, unique_id, view=None):
        obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
        if obj is None:
            msg = _("The object '${id}' could not be found.", mapping={'id': unique_id})
            return '<div class="error">%s</div>' % zope.i18n.translate(msg, context=self.request)
        self.request.response.setHeader('Cache-Control', 'no-cache')
        self.redirect(self.url(obj, view), status=301)
        return ''
