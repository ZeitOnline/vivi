from zeit.cms.interfaces import ICMSContent
from zeit.contentquery.interfaces import IConfiguration
import lxml.objectify
import zeit.cms.content.property
import zope.component
import zope.interface


class CustomQueryProperty:
    """Returns a query for a area/module that uses content queries."""

    def __init__(self, mapping=None):
        self.mapping = mapping

    def __get__(self, context, class_):
        """ Allows value mapping via dictionary."""
        if not hasattr(context.xml, 'query'):
            return ()
        result = []
        for condition in context.xml.query.getchildren():
            typ = condition.get('type')
            if typ in self.mapping:
                typ = self.mapping[typ]
            operator = condition.get('operator')
            if not operator:  # BBB
                operator = 'eq'
            value = self._converter(context, typ).fromProperty(str(condition))
            field = IConfiguration['query'].value_type.type_interface[typ]
            if zope.schema.interfaces.ICollection.providedBy(field):
                value = value[0]
            # CombinationWidget needs items to be flattened
            if not isinstance(value, tuple):
                value = (value,)
            result.append((typ, operator) + value)
        return tuple(result)

    def __set__(self, context, value):
        try:
            context.xml.remove(context.xml.query)
        except AttributeError:
            pass

        if not value:
            return

        E = lxml.objectify.E
        query = E.query()
        for item in value:
            typ, operator, val = self._serialize_query_item(context, item)
            query.append(E.condition(val, type=typ, operator=operator))
        context.xml.append(query)

    def _serialize_query_item(self, context, item):
        typ = item[0]
        operator = item[1]
        field = IConfiguration['query'].value_type.type_interface[typ]

        if len(item) > 3:
            value = item[2:]
        else:
            value = item[2]
        if zope.schema.interfaces.ICollection.providedBy(field):
            value = field._type((value,))  # tuple(already_tuple) is a no-op
        value = self._converter(context, typ).toProperty(value)

        return typ, operator, value

    def _converter(self, context, selector):
        field = IConfiguration['query'].value_type.type_interface[selector]
        field = field.bind(ICMSContent(context))
        props = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTIES
        return zope.component.getMultiAdapter(
            (field, props),
            zeit.cms.content.interfaces.IDAVPropertyConverter)


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

    start = 0  # Extension point for zeit.web to do pagination
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
    query = CustomQueryProperty()

    # automatic_type=rss-feed
    rss_feed = zeit.cms.content.property.DAVConverterWrapper(
        zeit.cms.content.property.ObjectPathAttributeProperty('.', 'rss_feed'),
        IConfiguration['rss_feed'])
