from zeit.contentquery.helper import QueryHelper
from zeit.contentquery.interfaces import IConfiguration
import zeit.cms.content.property
import zope.interface


@zope.interface.implementer(IConfiguration)
class Configuration:

    # Subclasses probably will need to override this, to specify their matching
    # schema field, since usually the available type values differ.
    _automatic_type = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'automatic_type', IConfiguration['automatic_type'])

    _automatic_type_bbb = {}

    @property
    def automatic_type(self):
        bbb = self._automatic_type_bbb.get(self._automatic_type)
        return bbb or self._automatic_type

    @automatic_type.setter
    def automatic_type(self, value):
        self._automatic_type = value

    hide_dupes = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'hide-dupes', IConfiguration['hide_dupes'], use_default=True)

    existing_teasers = NotImplemented

    count = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'count', IConfiguration['count'])

    # automatic_type=centerpage
    _referenced_cp = zeit.cms.content.property.SingleResource('.referenced_cp')

    @property
    def referenced_cp(self):
        return self._referenced_cp

    @referenced_cp.setter
    def referenced_cp(self, value):
        self._referenced_cp = value

    for name, default in {
            # automatic_type=topicpage
            'referenced_topicpage': False,
            'topicpage_filter': False,
            'topicpage_order': False,
            # automatic_type=related-topics
            'related_topicpage': False,
            # automatic_type=custom
            'query_order': True,
            # automatic_type=elasticsearch-query
            'elasticsearch_raw_query': False,
            'elasticsearch_raw_order': True,
            'is_complete_query': True,
            }.items():
        locals()[name] = zeit.cms.content.property.ObjectPathProperty(
            '.%s' % name, IConfiguration[name], use_default=default)

    # automatic_type=custom
    query = QueryHelper()

    # automatic_type=rss-feed
    rss_feed = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'rss_feed'),
        IConfiguration['rss_feed'])
