import grokcore.component as grok
import zeit.content.article.interfaces
import zeit.cms.admin.interfaces


@grok.adapter(zeit.content.article.interfaces.IArticle, name='zeit.content.article')
@grok.implementer(zeit.cms.admin.interfaces.IAdditionalFieldsCO)
def additional_fields_co(context):
    return (zeit.content.article.interfaces.IArticle, ['has_audio'])
