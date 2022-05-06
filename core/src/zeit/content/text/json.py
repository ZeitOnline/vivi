from zeit.cms.i18n import MessageFactory as _

import grokcore.component as grok

import commentjson
import jsonschema
import logging
import openapi_schema_validator
import requests
import yaml

import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.text.interfaces
import zeit.content.text.text
import zope.interface

log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.content.text.interfaces.IJSON)
class JSON(zeit.content.text.text.Text):

    @property
    def data(self):
        return commentjson.loads(self.text)


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
        ('schema_url', 'field_name')
    )

    def _valid_field_name(self, schema):
        try:
            return schema['components']['schemas'][self.field_name]
        except KeyError:
            log.error('Field name is not provided by schema ', exc_info=True)

    def _get(self):
        try:
            response = requests.get(self.schema_url)
            schema = yaml.safe_load(response.text)
            ref_resolver = jsonschema.validators.RefResolver.from_schema(
                schema)
            return schema, ref_resolver
        except requests.exceptions.RequestException as err:
            status = getattr(err.response, 'status_code', None)
            log.warning(
                '%s returned %s', self.schema_url, status, exc_info=True)

    def validate(self):
        schema, ref_resolver = self._get()
        if schema and self._valid_field_name(schema):
            openapi_schema_validator.validate(
                self.context.data,
                schema['components']['schemas'][self.field_name],
                resolver=ref_resolver)


@grok.subscribe(
    zeit.content.text.interfaces.IJSON,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def validate_after_checkin(context, event):
    validation = zeit.content.text.interfaces.IValidationSchema(context)
    if validation.schema_url and validation.field_name:
        validation.validate()
