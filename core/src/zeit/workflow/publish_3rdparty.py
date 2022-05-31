import grokcore.component as grok


import zeit.cms.content.interfaces
import zeit.workflow.interfaces


@grok.implementer(zeit.workflow.interfaces.IPublisherData)
class Comments(grok.Adapter):

    grok.context(zeit.cms.content.interfaces.ICommonMetadata)
    grok.name('comments')

    def json(self):
        meta = zeit.cms.content.interfaces.ICommonMetadata(self.context)
        uuid = zeit.cms.content.interfaces.IUUID(self.context)
        return {
            'comments_allowed': meta.commentsAllowed,
            'pre_moderated': meta.commentsPremoderate,
            'type': 'commentsection',
            'uuid': uuid.shortened,
            'unique_id': self.context.uniqueId,
            'visible': meta.commentSectionEnable}
