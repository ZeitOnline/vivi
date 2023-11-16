import zc.form.field
import zc.form.interfaces
import zope.schema.interfaces


class DynamicCombination(zc.form.field.Combination):
    def __init__(self, type_field, type_interface, *fields, **kw):
        self.type_field = type_field
        self.type_field.__name__ = 'combination_00'
        self.fields = (type_field,) + fields
        self.type_interface = type_interface
        super(zc.form.field.Combination, self).__init__(**kw)

    def generate_fields(self, selector):
        result = list(self.fields[1:])
        field = self.type_interface[selector]
        if zope.schema.interfaces.ICollection.providedBy(field):
            field = field.value_type
        if zc.form.interfaces.ICombinationField.providedBy(field):
            result.extend(field.fields)
        else:
            result.append(field)
        result = [x.bind(self.context) for x in result]
        for ix, field in enumerate(result):
            field.__name__ = 'combination_%02d' % (ix + 1)
        return result

    def _validate(self, value):
        # XXX I hope we can get away with no validation here, since all input
        # happens through widgets and so should be valid anyway. Otherwise we
        # have to synthesize fields here too, like DynamicCombinationWidget.
        pass
