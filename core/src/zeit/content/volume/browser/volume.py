import grokcore.component as grok
import zope.publisher.interfaces

import zeit.cms.browser.listing


@grok.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class VolumeListRepresentation(grok.MultiAdapter, zeit.cms.browser.listing.BaseListRepresentation):
    grok.adapts(
        zeit.content.volume.interfaces.IVolume, zope.publisher.interfaces.IPublicationRequest
    )

    ressort = page = author = ''

    @property
    def volume(self):
        return self.context.volume

    @property
    def year(self):
        return self.context.year

    @property
    def title(self):
        volume = self.context
        return '%s %s/%s' % (volume.product.title, volume.year, volume.volume)

    @property
    def searchableText(self):
        return self.title
