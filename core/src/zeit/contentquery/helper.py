import zeit.cms.content.property
from zeit.contentquery.interfaces import IConfiguration
import lxml.etree
import lxml.objectify
import six
import zeit.content.cp.interfaces
import zeit.contentquery.interfaces
import zope.component


class AutomaticTypeHelper(object):
    """Returns a referenced CP for AutomaticArea's parent Area and Topicboxes.
    """
    mapping = None

    def __get__(self, context, class_):
        if context._automatic_type in self.mapping:
            return self.mapping[context._automatic_type]
        return context._automatic_type

    def __set__(self, context, value):
        context._automatic_type = value


class CountHelper(object):
    """Returns a Count of teasers for the CP AutomaticArea
       and article's topicbox
    """
    def __get__(self, context, class_):
        return context._count

    def __set__(self, context, value):
        context._count = value
        if context.count_helper_tasks:
            context.count_helper_tasks()


class QueryHelper(object):
    """Returns a query for AutomaticArea's parent Area and Topicboxes.
    """

    def __get__(self, context, class_):
        """ Returns query
        """
        if not hasattr(context.xml, 'query'):
            return ()
        result = []
        for condition in context.xml.query.getchildren():
            typ = condition.get('type')
            if typ == 'Channel':  # BBB
                typ = 'channels'
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
        """ Sets values for query
        """
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
        field = field.bind(context.doc_iface(context))
        props = zeit.cms.content.property.DAVConverterWrapper.DUMMY_PROPERTIES
        return zope.component.getMultiAdapter(
            (field, props),
            zeit.cms.content.interfaces.IDAVPropertyConverter)


class ReferencedCenterpageHelper(object):
    """Returns a referenced CP for AutomaticArea's parent Area and Topicboxes.
    """

    def __get__(self, context, class_):
        return context._referenced_cp

    def __set__(self, context, value):
        # It is still possible to build larger circles (e.g A->C->A)
        # but a sane user should not ignore the errormessage shown in the
        # cp-editor and preview.
        # Checking for larger circles is not reasonable here.
        ref = zeit.content.cp.interfaces.ICenterPage
        if value.uniqueId == ref(context).uniqueId:
            raise ValueError("A centerpage can't reference itself!")
        context._referenced_cp = value
