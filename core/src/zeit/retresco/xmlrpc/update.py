import logging
import zeit.retresco.update
import zope.app.publisher.xmlrpc


log = logging.getLogger(__name__)


class Update(zope.app.publisher.xmlrpc.XMLRPCView):

    def update_tms(self, uniqueId):
        log.info(u"%s triggered TMS index update for '%s'" %
                 (self.request.principal.id, uniqueId))
        try:
            content = zeit.cms.interfaces.ICMSContent(uniqueId)
        except TypeError:
            log.warning(
                u'%s does not exist anymore, should be deleted from TMS',
                uniqueId)
            return
        zeit.retresco.update.index(content, enrich=True)
