# flake8: noqa
applicable(is_area and area == 'teaser-mosaic' and position == 2)
error_unless(layout == 'dmr', 'Die zweite Teaserleiste muss ein DMR sein')

applicable(is_area and area == 'lead')
warning_unless(count > 6,
               'In der Aufmacherfläche sollen mehr als 6 Teaserblöcke stehen')
error_unless(count > 2,
             'In der Aufmacherfläche müssen mehr als 2 Teaserblöcke stehen')


applicable('article' in globals() and article and is_block)
import zope.schema
import zope.interface
error_msg = f'Validierungsfehler in {context.type} verhindert Veröffentlichung'
invalid = zope.schema.getValidationErrors(list(zope.interface.providedBy(context))[0], context)
invalid_msg = ''
for i in invalid:
    field, err = i
    invalid_msg += f'Feld: {field}, Meldung: {err.doc()}'
error_msg = f'Validierungsfehler in {context.type} verhindert Veröffentlichung! {invalid_msg}'
error_if(invalid, error_msg)
