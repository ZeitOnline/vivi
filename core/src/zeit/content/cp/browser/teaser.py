# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent
import zope.security.proxy
import zope.viewlet.manager
from zeit.content.cp.i18n import MessageFactory as _


class TeaserListViewletManager(
    zope.viewlet.manager.WeightOrderedViewletManager):

    @property
    def css_class(self):
        if self.context.referenced_cp is None:
            autopilot = 'autopilot-not-possible'
        elif self.context.autopilot:
            autopilot = 'autopilot-on'
        else:
            autopilot = 'autopilot-off'
        return ' '.join(['block', 'type-' + self.context.type, autopilot])


class EditProperties(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.edit-properties.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ITeaserList).select(
        'title', 'referenced_cp', 'autopilot')

    @property
    def form(self):
        return super(EditProperties, self).template

    @property
    def layouts(self):
        terms = zope.component.getMultiAdapter(
            (zeit.content.cp.interfaces.ITeaserList['layout'].source,
             self.request), zope.browser.interfaces.ITerms)

        result = []
        for layout in zeit.content.cp.interfaces.ITeaserList['layout'].source:
            css_class = [layout.id]
            if layout == self.context.layout:
                css_class.append('selected')
            result.append(dict(
                css_class=' '.join(css_class),
                title=layout.title,
                token=terms.getTerm(layout).token,
            ))
        return result


class Display(zeit.cms.browser.view.Base):

    @property
    def css_class(self):
        css = ['action-content-droppable']
        layout = self.context.layout
        if layout is not None:
            css.append(layout.id)
        return ' '.join(css)

    @property
    def autopilot_toggle_url(self):
        on_off = 'off' if self.context.autopilot else 'on'
        return self.url('@@toggle-autopilot?to=' + on_off)

    def update(self):
        self.teasers = []
        for i, content in enumerate(self.context):
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None:
                # XXX warn? Actually such a content shouldn't be here in the
                # first place. We'll see.
                continue
            texts = []
            for name in ('supertitle', 'teaserTitle', 'teaserText',
                         'shortTeaserTitle', 'shortTeaserText'):
                texts.append(dict(css_class=name,
                                  content=getattr(metadata, name)))
            image = None
            if i == 0:
                image = self.get_image(content)
            self.teasers.append(dict(
                image=image,
                texts=texts))

    def get_image(self, content):
        layout = self.context.layout
        if layout is None:
            return
        images = zeit.content.image.interfaces.IImages(content, None)
        if images is None:
            return
        if not images.images:
            return
        image_group = images.images[0]
        for name in image_group:
            if layout.image_pattern in name:
                return image_group[name]

class Drop(object):

    def __call__(self, uniqueId):
        # XXX error handling
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        if self.context.autopilot:
            self.context.autopilot = False
        self.context.insert(0, content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))



class EditContents(Display):
    """Edit the teaser list."""

    def teasers(self):
        teasers = []
        for content in self.context:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None:
                # XXX warn? Actually such a content shouldn't be here in the
                # first place. We'll see.
                continue
            editable = zeit.cms.checkout.interfaces.ICheckoutManager(
                content).canCheckout
            teasers.append(dict(
                content=content,
                editable=editable,
                metadata=metadata,
                uniqueId=content.uniqueId,
                url=self.url(content),
            ))

        return teasers


class Delete(object):

    def __call__(self, uniqueId):
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        self.context.remove(content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))


class CheckoutContent(object):

    def __call__(self, uniqueId):
        content = zeit.cms.interfaces.ICMSContent(uniqueId)
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(content)
        checked_out = manager.checkout()
        self.request.response.redirect(
            '%s/++item++%s/edit-teaser.html' % (
            zope.traversing.browser.absoluteURL(self.context, self.request),
            checked_out.__name__))


class TeaserListProxyItem(object):

    zope.interface.implements(zeit.cms.content.interfaces.ICommonMetadata,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        return getattr(self.context, name)

    def __setattr__(self, name, value):
        if name in ['context', '__name__', '__parent__']:
            object.__setattr__(self, name, value)
        else:
            setattr(self.context, name, value)

    def get_proxied_object(self):
        return self.context


@zope.component.adapter(TeaserListProxyItem)
@zope.interface.implementer(zeit.cms.checkout.interfaces.ICheckinManager)
def checkout_manager_for_proxy(proxy):
    return zeit.cms.checkout.interfaces.ICheckinManager(
        proxy.get_proxied_object())


class ItemTraverser(object):

    zope.component.adapts(
        zeit.content.cp.interfaces.ITeaserList,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer)
    zope.interface.implements(zope.traversing.interfaces.ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        wc = zeit.cms.workingcopy.interfaces.IWorkingcopy(
            self.request.principal)

        try:
            return zope.location.location.located(
                TeaserListProxyItem(wc[name]), self.context, name)
        except KeyError:
            raise zope.publisher.interfaces.NotFound(
                self.context, name, self.request)


class EditTeaser(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.edit-teaser.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'supertitle', 'teaserTitle', 'teaserText',
            'shortTeaserTitle', 'shortTeaserText')
    close = False

    def __call__(self, *args, **kw):
        return super(EditTeaser, self).__call__(*args, **kw)

    @property
    def form(self):
        return super(EditTeaser, self).template

    @zope.formlib.form.action(_('Apply for article'), name='apply')
    def apply(self, action, data):
        changed = zope.formlib.form.applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            manager = zeit.cms.checkout.interfaces.ICheckinManager(
                self.context)
            manager.checkin()
            self.close = True

    def _is_not_teaser(self, action):
        return not zeit.content.cp.interfaces.ITeaser.providedBy(
            self.context.get_proxied_object())

    @zope.formlib.form.action(
        _('Apply only for this page'), condition=_is_not_teaser)
    def apply_local(self, action, data):
        teaser = zeit.content.cp.interfaces.ITeaser(self.context)

        folder = zeit.cms.interfaces.ICMSContent(
            self.context.uniqueId).__parent__
        name = zope.container.interfaces.INameChooser(
            folder).chooseName(self.context.__name__, teaser)

        # Delete the original_content from the working copy.
        del self.context.get_proxied_object().__parent__[self.context.__name__]

        # Don't cache the adapter lookups because we want to apply changes to
        # another object.
        self.adapters.clear()
        changed = zope.formlib.form.applyChanges(
            teaser, self.form_fields, data, self.adapters)
        if changed:
            folder[name] = teaser
            teaser_list = self.context.__parent__
            teaser_list.insert(teaser_list.getPosition(self.context), teaser)
            teaser_list.remove(self.context)
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(teaser_list))
            self.close = True


class ChangeLayout(object):

    def __call__(self, id):
        layout = zope.component.getMultiAdapter(
            (zeit.content.cp.interfaces.ITeaserList['layout'].source,
             self.request), zope.browser.interfaces.ITerms).getValue(id)
        self.context.layout = layout
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'


class ToggleAutopilot(object):

    def __call__(self, to):
        self.context.autopilot = (True if to == 'on' else False)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
