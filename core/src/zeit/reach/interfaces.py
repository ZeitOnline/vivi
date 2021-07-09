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
