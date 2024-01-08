import logging

import commentjson
import grokcore.component as grok
import jsonschema
import openapi_schema_validator
import requests
import requests_file
import yaml
import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.checkout.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.text.interfaces
import zeit.content.text.text


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


@zope.interface.implementer(zeit.content.text.interfaces.IValidationSchema)
class ValidationSchema(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.content.text.interfaces.IValidationSchema,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('schema_url', 'field_name'),
    )

    def request(self, method, url, **kw):
        session = requests.sessions.Session()
        session.mount('file://', requests_file.FileAdapter())
        response = session.request(method=method, url=url, **kw)
        session.close()
        return response

    def _valid_field_name(self, schema):
        try:
            return schema['components']['schemas'][self.field_name]
        except (AttributeError, KeyError):
            message = 'Field name missing or not provided by schema'
            raise zeit.content.text.interfaces.SchemaValidationError(message)

    def _get(self):
        if not self.schema_url:
            # Send this to "Meldung"
            log.info('No schema url provided', exc_info=True)
            return None
        try:
            response = self.request('GET', self.schema_url)
            schema = yaml.safe_load(response.text)
            ref_resolver = jsonschema.validators.RefResolver.from_schema(schema)
            response.close()
            return schema, ref_resolver
        except requests.exceptions.RequestException as err:
            status = getattr(err.response, 'status_code', None)
            message = f'{self.schema_url} returned {status}'
            log.warning(message, exc_info=True)
            raise zeit.content.text.interfaces.SchemaValidationError(message)

    def validate(self):
        schema, ref_resolver = self._get()
        if not schema:
            return
        if self._valid_field_name(schema):
            try:
                openapi_schema_validator.validate(
                    self.context.data,
                    schema['components']['schemas'][self.field_name],
                    resolver=ref_resolver,
                )
            except jsonschema.exceptions.ValidationError as error:
                raise zeit.content.text.interfaces.SchemaValidationError(str(error))


@grok.subscribe(
    zeit.content.text.interfaces.IJSON, zeit.cms.checkout.interfaces.IBeforeCheckinEvent
)
def validate_after_checkin(context, event):
    validation = zeit.content.text.interfaces.IValidationSchema(context)
    if validation.schema_url and validation.field_name:
        validation.validate()
