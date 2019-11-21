import persistent
import zope.container.btree
import zope.container.contained
import zope.container.interfaces
import zeit.cms.content.sources
import zeit.cms.retractlog.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.workflow.interfaces
import zope.component


class RetractLog(zope.container.btree.BTreeContainer):
    """Insert retract jobs for multiple ICMSContent objects."""

    zope.interface.implements(zeit.cms.retractlog.interfaces.IRetractLog)


class Job(zope.container.contained.Contained,
          persistent.Persistent):
    """A list of ICMSContent URLs, which were or will be retracted."""

    zope.interface.implements(zeit.cms.retractlog.interfaces.IJob)

    def __init__(self):
        super(Job, self).__init__()
        self.urls_text = ''
        self.urls = []
        self.invalid = []
        self.unknown = []
        self.title = ''

    def start(self):
        publish = zeit.cms.workflow.interfaces.IPublish(
            zope.component.getUtility(
                zeit.cms.repository.interfaces.IRepository))
        publish.retract_multiple(self.urls)
