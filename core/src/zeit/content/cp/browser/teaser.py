# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.component
import zope.event
import zope.formlib.form
import zope.lifecycleevent
from zeit.content.cp.i18n import MessageFactory as _


class TeaserListBlockEdit(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'teaser.block-edit.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.syndication.interfaces.IFeed)

    @property
    def form(self):
        return super(TeaserListBlockEdit, self).template


class TeaserList(zeit.cms.browser.view.Base):

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


class TeaserDrop(object):

    def __call__(self, uniqueId):
        # XXX error handling
        content = self.repository.getContent(uniqueId)
        self.context.insert(0, content)
        zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
            self.context))


    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)


class TeaserListEdit(TeaserList):
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
        'teaser.edit.pt')

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


@zope.component.adapter(zeit.cms.content.interfaces.ICommonMetadata)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def teaserEditViewName(context):
    return 'edit-teaser.html'
