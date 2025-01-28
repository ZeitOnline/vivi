import zope.interface

import zeit.retresco.interfaces


class IReach(zope.interface.Interface):
    def get_ranking(service, facet=None, **kw):
        """Retrieve ranked content from reach.zeit.de.

        :service: views, comments, subscriptions, social
        :facet: must be 'facebook' when service is 'social',
        for historical reasons (there also used to be google plus and twitter)

        See the reach documentation for further supported parameters.
        """


class IReachContent(zeit.cms.interfaces.ICMSContent):
    pass


class IKPI(zeit.cms.content.interfaces.IKPI):
    """reach results only contain a single kpi metric, namely the one that
    was requested. This doesn't fully match the IKPI semantics (which say
    clients can access any kpi they want), so we declare a subclass interface.
    """

    score = zope.schema.Int(default=0, readonly=True)
