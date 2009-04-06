# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.cp.interfaces
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.component
import zope.formlib.form


class TeaserEdit(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'form.teaser.edit.pt')

    form_fields = zope.formlib.form.FormFields(
        zeit.cms.syndication.interfaces.IFeed)

    @property
    def form(self):
        return super(TeaserEdit, self).template


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
        # XXX make sure the change is propagated to the cp
        self.context.insert(0, content)

    @property
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
