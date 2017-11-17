import grokcore.component
import lxml.objectify
import zeit.content.video.interfaces
import zeit.solr.interfaces


class Index(object):

    grokcore.component.implements(zeit.solr.interfaces.IIndex)

    interface = zeit.content.video.interfaces.IVideo

    def process(self, value, node):
        child_node = lxml.objectify.E.field(value, name=self.solr)
        lxml.objectify.deannotate(child_node)
        node.append(child_node)

    @property
    def solr(self):
        return getattr(self.__class__, 'grokcore.component.directive.name')


class BannerIndex(Index, grokcore.component.GlobalUtility):

    grokcore.component.name('banner')
    attribute = 'banner'


class BannerIDIndex(Index, grokcore.component.GlobalUtility):

    grokcore.component.name('banner-id')
    attribute = 'banner_id'
