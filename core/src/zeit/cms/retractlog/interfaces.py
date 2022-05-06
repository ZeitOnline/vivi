from zeit.cms.i18n import MessageFactory as _
import zope.container.interfaces
import zope.schema
import zeit.cms.content.sources


class IRetractLog(zope.container.interfaces.IReadContainer):
    """Manages templates for a content type."""


class URLText(zope.schema.Text):

    def _validate(self, value):
        if not value:
            raise zope.schema.interfaces.TooShort()
        super()._validate(value)
        url_limit = int(
            RETRACT_LOG_CONFIG.limit)
        if value.count('\n') >= url_limit:
            raise zope.schema.interfaces.TooLong()


class IJob(zope.interface.Interface):
    """A template for xml content types."""

    title = zope.schema.TextLine(title=_("Title"))
    urls_text = URLText(
        title=_('URLs'),
        missing_value='')
    urls = zope.schema.List(value_type=zope.schema.TextLine())
    invalid = zope.schema.List(value_type=zope.schema.TextLine())
    unknown = zope.schema.List(value_type=zope.schema.TextLine())

    def start():
        """Start the retract job."""


class RetractLogConfig(zeit.cms.content.sources.CachedXMLBase):

    product_configuration = 'zeit.cms'
    config_url = 'config-retractlog'
    default_filename = 'retractlog.xml'

    @property
    def limit(self):
        return int(self._get_tree().limit.text)

    @property
    def filter(self):
        return [node.text for node in self._get_tree().findall('filter')]


RETRACT_LOG_CONFIG = RetractLogConfig()
