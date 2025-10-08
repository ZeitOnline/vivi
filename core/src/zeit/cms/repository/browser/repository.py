import grokcore.component as grok
import zope.cachedescriptors.property
import zope.component
import zope.i18n
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

    def expanded(self, obj):
        if self.request.form.get('autoexpand-tree'):
            url = self.getUrl(obj)
            if self.selected(url):
                return True
        return super().expanded(obj)


class RedirectToObjectWithUniqueId(zeit.cms.browser.view.Base):
    def __call__(self, unique_id, view=''):
        obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
        if obj is None:
            msg = _("The object '${id}' could not be found.", mapping={'id': unique_id})
            return '<div class="error">%s</div>' % zope.i18n.translate(msg, context=self.request)
        self.request.response.setHeader('Cache-Control', 'no-cache')
        self.redirect(self.url(obj, view), status=301)
        return ''
