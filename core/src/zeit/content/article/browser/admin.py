import grokcore.component as grok

import zeit.cms.admin.interfaces
import zeit.content.article.interfaces


@grok.adapter(zeit.content.article.interfaces.IArticle, name='zeit.content.article')
@grok.implementer(zeit.cms.admin.interfaces.IAdditionalFieldsCO)
def additional_fields_co(context):
    return (zeit.content.article.interfaces.IArticle, ['has_audio', 'avoid_create_summary'])
