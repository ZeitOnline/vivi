import zeit.cms.content.property
import lxml.etree
import lxml.objectify
import six
import zeit.content.cp.interfaces
import zeit.contentquery.interfaces
import zope.component
from zeit.cms.interfaces import ICMSContent
from zeit.contentquery.interfaces import IConfiguration


class QueryHelper:
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
            value = self._converter(context, typ).fromProperty(
                six.text_type(condition))
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
