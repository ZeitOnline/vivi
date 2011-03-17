# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.edit.browser.block
import zeit.edit.browser.view
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.cachedescriptors.property
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent


COLUMN_ID = 'column://'


class TeaserBlockViewletManager(
    zeit.edit.browser.block.BlockViewletManager):

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

    form_fields = ()
    close = False

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

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.close = True
        return super(EditProperties, self).handle_edit_action.success(data)


class AutoPilotEditProperties(EditProperties):

    interface = zeit.content.cp.interfaces.IAutoPilotTeaserBlock

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.IAutoPilotTeaserBlock).select(
            'referenced_cp', 'autopilot', 'hide_dupes')





class Display(zeit.cms.browser.view.Base):

    @property
    def css_class(self):
        css = ['teaser-contents action-content-droppable']
        layout = self.context.layout
        if layout is not None:
            css.append(layout.id)
        return ' '.join(css)

    def update(self):
        self.image = None
        teasers = []
        for i, content in enumerate(self.context):
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None:
                # XXX warn? Actually such a content shouldn't be here in the
                # first place. We'll see.
                continue
            texts = []
            for name in ('supertitle', 'teaserTitle', 'teaserText'):
                texts.append(dict(css_class=name,
                                  content=getattr(metadata, name)))
            teasers.append(dict(
                texts=texts,
                uniqueId=content.uniqueId))
            if i == 0:
                self.image = self.get_image(content)

        columns = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
        idx = 0
        self.columns = []
        for amount in columns:
            self.columns.append(teasers[idx:idx+amount])
            idx += amount

    def get_image(self, content):
        layout = self.context.layout
        if layout is None:
            return
        if not layout.image_pattern:
            return
        images = zeit.content.image.interfaces.IImages(content, None)
        if images is None:
            preview = zope.component.queryMultiAdapter(
                (content, self.request), name='preview')
            if preview:
                return self.url(preview)
            return
        if not images.images:
            return
        image = images.images[0]
        if zeit.content.image.interfaces.IImageGroup.providedBy(image):
            for name in image:
                if layout.image_pattern in name:
                    return self.url(image[name])
        else:
            return self.url(image)


class AutoPilotDisplay(Display):

    @property
    def autopilot_toggle_url(self):
        on_off = 'off' if self.context.autopilot else 'on'
        return self.url('@@toggle-autopilot?to=' + on_off)


class Drop(zeit.edit.browser.view.Action):
    """Drop a content object on a teaserblock."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')
    index = zeit.edit.browser.view.Form('index', json=True, default=0)

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.insert(self.index, content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))


class AutoPilotDrop(Drop):
    """Drop a content object on a teaserblock."""

    def update(self):
        if self.context.autopilot:
            self.context.autopilot = False
        super(AutoPilotDrop, self).update()


class EditContents(zeit.cms.browser.view.Base):
    """Edit the teaser list."""

    @zope.cachedescriptors.property.Lazy
    def teasers(self):
        teasers = []
        for content in self.context:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            locking_indicator = None
            url = None
            if metadata is None:
                editable = False
                title = content.uniqueId
            else:
                editable = True
                title = metadata.teaserTitle
                try:
                    url = self.url(content)
                except TypeError:
                    # For example, IXMLTeaser cannot be viewed that way.
                    pass
            teasers.append(dict(
                css_class='edit-bar teaser',
                deletable=True,
                editable=editable,
                teaserTitle=title,
                uniqueId=content.uniqueId,
                url=url,
                viewable=bool(url),
            ))

        columns = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
        if len(columns) == 2:
            left = columns[0]
            teasers.insert(left, dict(
                css_class='edit-bar column-separator',
                deletable=False,
                editable=False,
                teaserTitle=_('^ Left | Right v'),
                uniqueId=COLUMN_ID,
                viewable=False,
            ))

        return teasers


class ChangeLayout(zeit.edit.browser.view.Action):
    """Change the layout of a teaserblock."""

    interface = zeit.content.cp.interfaces.ITeaserBlock

    layout_id = zeit.edit.browser.view.Form('id')

    def update(self):
        layout = zope.component.getMultiAdapter(
            (self.interface['layout'].source(self.context),
             self.request), zope.browser.interfaces.ITerms).getValue(
                 self.layout_id)
        self.context.layout = layout
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal('before-reload', 'deleted', self.context.__name__)
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))
        self.signal('after-reload', 'added', self.context.__name__)


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'


class ToggleAutopilot(zeit.edit.browser.view.Action):

    to = zeit.edit.browser.view.Form('to')

    def update(self):
        self.context.autopilot = (True if self.to == 'on' else False)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal_context_reload()


class UpdateOrder(zeit.edit.browser.view.Action):

    keys = zeit.edit.browser.view.Form('keys', json=True)

    def update(self):
        keys = self.keys
        try:
            left = keys.index(COLUMN_ID)
        except ValueError:
            left = None
        else:
            del keys[left]
            cols = zeit.content.cp.interfaces.ITeaserBlockColumns(self.context)
            cols[0] = left
        self.context.updateOrder(keys)
        zope.event.notify(
            zope.lifecycleevent.ObjectModifiedEvent(self.context))


class AutoPilotUpdateOrder(UpdateOrder):

    def update(self):
        self.context.autopilot = False
        super(AutoPilotUpdateOrder, self).update()


class Delete(zeit.edit.browser.view.Action):
    """Delete item from TeaserBlock."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.context.remove(content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))
        self.signal(
            None, 'reload', self.context.__name__, self.url('@@contents'))


class Countings(object):

    @zope.cachedescriptors.property.Lazy
    def countings(self):
        try:
            item = iter(self.context).next()
        except StopIteration:
            pass
        else:
            return zeit.cms.content.interfaces.IAccessCounter(item, None)

    @property
    def today(self):
        if self.countings is not None:
            return self.countings.hits or 0

    @property
    def lifetime(self):
        if self.countings is not None:
            return self.countings.total_hits or 0

    @property
    def url(self):
        if self.countings is not None:
            try:
                return self.countings.detail_url
            except AttributeError:
                pass
