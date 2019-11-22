import grokcore.component as grok
import zeit.cms.browser.listing
import zope.publisher.interfaces


@grok.implementer(zeit.cms.browser.interfaces.IListRepresentation)
class AuthorListRepresentation(
        grok.MultiAdapter,
        zeit.cms.browser.listing.BaseListRepresentation):

    grok.context(
        zeit.content.author.interfaces.IAuthor,
        zope.publisher.interfaces.IPublicationRequest)

    ressort = page = volume = year = author = u''

    @property
    def title(self):
        try:
            return self.context.display_name
        except Exception:
            return u'%s %s' % (self.context.firstname, self.context.lastname)

    @property
    def searchableText(self):
        return self.title
