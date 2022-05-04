from zeit.cms.i18n import MessageFactory as _

import commentjson
import grokcore.component as grok
import jsonschema.validators
import openapi_schema_validator

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface


@zope.interface.implementer(zeit.content.text.interfaces.IJSON)
class JSON(zeit.content.text.text.Text):

    @property
    def data(self):
        return commentjson.loads(self.text)

    def validate_data(self):
        validation = zeit.content.text.interfaces.IValidationSchema(self)
        if validation.json_schema:
            schema = commentjson.loads(validation.json_schema)
            rooted_schemas = {
                'components': {
                    'schemas': schema}}
            ref_resolver = jsonschema.validators.RefResolver.from_schema(
                rooted_schemas)
            openapi_schema_validator.validate(
                self.data,
                schema[validation.field],
                resolver=ref_resolver)


class JSONType(zeit.content.text.text.TextType):

    interface = zeit.content.text.interfaces.IJSON
    type = 'json'
    title = _('JSON file')
    factory = JSON
    addform = zeit.cms.type.SKIP_ADD


@zope.interface.implementer(
    zeit.content.text.interfaces.IValidationSchema)
class ValidationSchema(zeit.cms.content.dav.DAVPropertiesAdapter):

    zeit.cms.content.dav.mapProperties(
        zeit.content.text.interfaces.IValidationSchema,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('json_schema', 'field')
    )


@grok.subscribe(
    zeit.content.text.interfaces.IJSON,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def validate_after_checkin(context, event):
    validation = zeit.content.text.interfaces.IValidationSchema(context)
    if validation.json_schema and validation.field:
        context.validate_data()
