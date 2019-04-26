from zeit.content.article.edit.interfaces import IBreakingNewsBody
import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.push.banner


class BreakingNews(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.context(zeit.content.article.interfaces.IArticle)
    grok.implements(zeit.content.article.interfaces.IBreakingNews)

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.IBreakingNews,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('is_breaking',))

    # XXX IBreakingNews is supposed to be a specialized IArticle, so we should
    # proxy all attributes we don't have to self.context, but that's hard to do
    # generically without creating infloops, so we list the proxied attributes
    # manually (compare the AddForm in .browser.breaking).

    @property
    def title(self):
        return self.context.title

    @title.setter
    def title(self, value):
        self.context.title = value

    def banner_matches(self):
        return self.context == zeit.push.banner.get_breaking_news_article()


@grok.adapter(BreakingNews)
@grok.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webdav_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
