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
            class_ = 'selected' if layout == self.context.layout else ''
            result.append(dict(token=terms.getTerm(layout).token,
                               title=layout.title, class_=class_))
        return result


class Display(zeit.cms.browser.view.Base):

    @property
    def css_class(self):
        layout = 'topthema'  # XXX
        return ' '.join(['teaser-list', layout, 'action-content-droppable'])

    @property
    def autopilot_toggle_url(self):
        on_off = 'off' if self.context.autopilot else 'on'
        return self.url('@@toggle-autopilot?to=' + on_off)

    def update(self):
        self.teasers = []
        for content in self.context:
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
            images = zeit.content.image.interfaces.IImages(content, None)
            if images is None or not images.images:
                image = None
            else:
                image = images.images[0]
            self.teasers.append(dict(
                image=image,
                texts=texts))


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


class EditTeaser(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.edit-teaser.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'supertitle', 'teaserTitle', 'teaserText',
            'shortTeaserTitle', 'shortTeaserText')
    close = False

    @property
    def form(self):
        return super(EditTeaser, self).template

    @zope.formlib.form.action(_('Apply'))
    def apply(self, action, data):
        changed = zope.formlib.form.applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            manager = zeit.cms.checkout.interfaces.ICheckinManager(
                self.context)
            manager.checkin()
            self.close = True


class ChangeLayout(object):
    def __call__(self, id):
        layout = zope.component.getMultiAdapter(
            (zeit.content.cp.interfaces.ITeaserList['layout'].source,
             self.request), zope.browser.interfaces.ITerms).getValue(id)
        self.context.layout = layout


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'


class ToggleAutopilot(object):

    def __call__(self, to):
        self.context.autopilot = (True if to == 'on' else False)
