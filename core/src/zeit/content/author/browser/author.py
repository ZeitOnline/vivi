import grokcore.component as grok
import zeit.cms.browser.listing
import zope.publisher.interfaces


@grok.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class AuthorListRepresentation(grok.MultiAdapter, zeit.cms.browser.listing.BaseListRepresentation):
    grok.adapts(
        zeit.content.author.interfaces.IAuthor, zope.publisher.interfaces.IPublicationRequest
    )

    ressort = page = volume = year = author = ''

    @property
    def title(self):
        try:
            return self.context.display_name
        except Exception:
            return '%s %s' % (self.context.firstname, self.context.lastname)

    @property
    def searchableText(self):
        return self.title
