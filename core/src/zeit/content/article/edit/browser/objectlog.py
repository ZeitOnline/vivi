import zeit.cms.interfaces


class ObjectLog:
    @property
    def repository_content(self):
        return zeit.cms.interfaces.ICMSContent(self.context.uniqueId, None)
