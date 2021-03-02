from zeit.cms.content.property import ObjectPathProperty
from zeit.contentquery.interfaces import IConfiguration
import lxml.etree
import lxml.objectify
import six
import zeit.contentquery.interfaces
import zope.component


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
            value = context._converter(typ).fromProperty(
                six.text_type(condition))
            field = zeit.content.cp.interfaces.IArea[
                'query'].value_type.type_interface[typ]
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
            typ, operator, val = context._serialize_query_item(item)
            query.append(E.condition(val, type=typ, operator=operator))
        context.xml.append(query)


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
        if value.uniqueId == ref(self).uniqueId:
            raise ValueError("A centerpage can't reference itself!")
        context._referenced_cp = value
