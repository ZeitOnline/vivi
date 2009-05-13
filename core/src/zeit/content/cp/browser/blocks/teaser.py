# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.browser.view
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent


class TeaserBlockViewletManager(
    zeit.content.cp.browser.blocks.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(TeaserBlockViewletManager, self).css_class
        if self.context.referenced_cp is None:
            autopilot = 'autopilot-not-possible'
        elif self.context.autopilot:
            autopilot = 'autopilot-on'
        else:
            autopilot = 'autopilot-off'
        return '%s %s' % (classes, autopilot)


class EditProperties(zope.formlib.form.SubPageEditForm):

    layout_prefix = 'teaser'
    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.edit-properties.pt')

    interface = zeit.content.cp.interfaces.ITeaserBlock

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ITeaserBlock).select(
        'title', 'referenced_cp', 'autopilot')


    @property
    def form(self):
        return super(EditProperties, self).template

    @property
    def layouts(self):
        source = self.interface['layout'].source(self.context)
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)

        result = []
        for layout in source:
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


class Drop(zeit.content.cp.browser.view.Action):
    """Drop a content object on a teaserblock."""

    uniqueId = zeit.content.cp.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
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


class ChangeLayout(zeit.content.cp.browser.view.Action):
    """Change the layout of a teaserblock."""

    interface = zeit.content.cp.interfaces.ITeaserBlock

    layout_id = zeit.content.cp.browser.view.Form('id')

    def update(self):
        layout = zope.component.getMultiAdapter(
            (self.interface['layout'].source(self.context),
             self.request), zope.browser.interfaces.ITerms).getValue(
                 self.layout_id)
        self.context.layout = layout
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal('after-reload', 'added', self.context.__name__)


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'


class ToggleAutopilot(zeit.content.cp.browser.view.Action):

    to = zeit.content.cp.browser.view.Form('to')

    def update(self):
        self.context.autopilot = (True if self.to == 'on' else False)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))


class UpdateOrder(zeit.content.cp.browser.view.Action):

    keys = zeit.content.cp.browser.view.Form('keys', json=True)

    def update(self):
        self.context.autopilot = False
        self.context.updateOrder(self.keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))
