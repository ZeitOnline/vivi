from zeit.cms.i18n import MessageFactory as _
from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.cms.tagging.interfaces
import zope.component


class Suggest(object):

    @property
    def show_more(self):
        if self.ressort_keywords:
            return _('More suggestions...')
        else:
            return _('All Google News keywords...')

    @property
    def show_less(self):
        return _('Show less')

    @cachedproperty
    def topics(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.ICurrentTopics)

    @cachedproperty
    def ressort_keywords(self):
        return self.topics(self.context.ressort)

    @cachedproperty
    def all_keywords(self):
        return self.topics()

    @cachedproperty
    def headlines(self):
        return self.topics.headlines
