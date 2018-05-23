import zc.form.field
import zeit.cms.content.interfaces
import zope.schema.interfaces


class DynamicCombination(zc.form.field.Combination):

    def __init__(self, type_field, **kw):
        self.type_field = type_field
        self.type_field.__name__ = "combination_00"
        self.fields = (type_field,)
        super(zc.form.field.Combination, self).__init__(**kw)

    def generate_fields(self, selector):
        fields = []
        # XXX generalize, but how? Is single interface source helpful, or
        # would we need a wholesale mapping function?
        field = zeit.cms.content.interfaces.ICommonMetadata[selector]
        if zope.schema.interfaces.ICollection.providedBy(field):
            fields.extend(field.value_type.fields)
        else:
            fields.append(field)
        fields = [x.bind(self.context) for x in fields]
        for ix, field in enumerate(fields):
            field.__name__ = "combination_%02d" % (ix + 1)
        return fields

    def _validate(self, value):
        # XXX I hope we can get away with no validation here, since all input
        # happens through widgets and so should be valid anyway. Otherwise we
        # have to synthesize fields here too, like DynamicCombinationWidget.
        pass
