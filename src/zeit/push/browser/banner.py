from zeit.cms.interfaces import ICMSContent
import zeit.content.article.interfaces
import zeit.push.interfaces
import zope.component


class Retract(object):

    @property
    def homepage(self):
        notifier = zope.component.getUtility(
            zeit.push.interfaces.IPushNotifier, name='homepage')
        return ICMSContent(notifier.uniqueId)

    @property
    def banner_matches(self):
        breaking = zeit.content.article.interfaces.IBreakingNews(
            self.context, None)
        if breaking is None:
            return False
        return breaking.banner_matches(self.homepage)
