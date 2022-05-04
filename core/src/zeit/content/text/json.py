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

    def get_schema(self):
        info = zeit.content.text.interfaces.IValidationSchema(self)
        try:
            response = requests.get(info.schema_url)  # yaml schema file expected
            schema = yaml.safe_load(response.text)
            ref_resolver = jsonschema.validators.RefResolver.from_schema(
                schema)
            return schema, ref_resolver
        except requests.exceptions.RequestException as err:
            status = getattr(err.response, 'status_code', None)
            log.error('%s returned %s', info.schema_url, status, exc_info=True)


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


@grok.subscribe(
    zeit.content.text.interfaces.IJSON,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def validate_after_checkin(context, event):
    schema, ref_resolver = context.get_schema()
    if schema:
        validation = zeit.content.text.interfaces.IValidationSchema(context)
        openapi_schema_validator.validate(
            context.data,
            schema['components']['schemas'][validation.field_name],
            resolver=ref_resolver)
