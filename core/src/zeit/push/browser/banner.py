import zeit.content.article.interfaces
import zeit.push.interfaces
import zope.component


class Retract:

    @property
    def banner(self):
        return zope.component.getUtility(
            zeit.push.interfaces.IBanner).xml_banner

    @property
    def banner_matches(self):
        breaking = zeit.content.article.interfaces.IBreakingNews(
            self.context, None)
        if breaking is None:
            return False
        return breaking.banner_matches()
