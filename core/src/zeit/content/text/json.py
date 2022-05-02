from zeit.cms.i18n import MessageFactory as _

import commentjson
import logging
import openapi_schema_validator
import requests
import yaml

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
            schema = requests.get(info.schema_url)  # yaml schema file expected
            return yaml.safe_load(schema.text)
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

    schema_url = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IValidationSchema['schema_url'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'schema_url')
