import zeit.retresco.interfaces
import zope.interface


class IReach(zope.interface.Interface):

    def get_comments():
        """Retrieve a ranking of most commented articles"""

    def get_score():
        """Return a ranking of highest buzz-scoring articles"""

    def get_trend():
        """Return a ranking of highest buzz-trending articles"""

    def get_social():
        """Get a ranking of articles trending on social platforms"""

    def get_views():
        """Output a ranking of articles with top view counts"""

    def get_buzz():
        """Collect a buzz summary for an article by uniqueId"""


# XXX We probably should abstract ITMSContent into something like
# zeit.cms.something.ISearchResultProxyPerformanceHelper
class IReachContent(zeit.retresco.interfaces.ITMSContent):
    pass


class IKPI(zeit.cms.content.interfaces.IKPI):
    """reach results only contain a single kpi metric, namely the one that
    was requested. This doesn't fully match the IKPI semantics (which say
    clients can access any kpi they want), so we declare a subclass interface.
    """

    score = zope.schema.Int(default=0, readonly=True)
