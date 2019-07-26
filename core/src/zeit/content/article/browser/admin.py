import zeit.content.article.interfaces
import zeit.cms.admin.interfaces
import zope.interface


@zope.interface.implementer(zeit.cms.admin.interfaces.IAdditionalFieldsCO)
def additional_fields_co():
    return (zeit.content.article.interfaces.IArticle, ['has_audio'])
