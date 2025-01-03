import zope.component
import zope.interface
import zope.schema
import zope.viewlet.interfaces

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.workflow.interfaces


class IWorkflowIndicator(zope.viewlet.interfaces.IViewletManager):
    """Render workflow indicators."""


class ServiceSource(zeit.cms.content.sources.SimpleFixedValueSource):
    """Lists all available third party services of publisher"""

    @property
    def values(self):
        values = {}
        gsm = zope.component.getGlobalSiteManager()
        adapters = gsm.registeredAdapters()
        for adapter in adapters:
            if adapter.provided == zeit.workflow.interfaces.IPublisherData:
                values[adapter.name] = adapter.name
        return values


class IManualMultiPublish(zope.interface.Interface):
    """Manually trigger publish for multiple content objects."""

    force_unpublished = zope.schema.Bool(
        title=_('Publish even if currently unpublished'), default=False
    )
    force_unchanged = zope.schema.Bool(
        title=_('Publish even if with semantic change'), default=False
    )
    skip_deps = zope.schema.Bool(title=_('Ignore publication dependencies'), default=False)
    use_checkin_hooks = zope.schema.Bool(
        title=_('Notify webhooks after checkin, like contenthub'), default=False
    )
    use_publish_hooks = zope.schema.Bool(
        title=_('Notify webhooks after publish, like contenthub'), default=False
    )
    ignore_services = zope.schema.Tuple(
        title=_('Ignore 3rd party services'),
        unique=True,
        value_type=zope.schema.Choice(source=ServiceSource()),
        default=('airship', 'speechbert', 'summy'),
    )
    wait_tms = zope.schema.Bool(
        title=_('Have publisher wait for TMS before fastly purge'), default=False
    )
    skip_tms_enrich = zope.schema.Bool(
        title=_('Skip TMS enrich, e.g. checkin already happened'), default=False
    )
    dlps = zope.schema.Bool(title=_('Update date_last_published_semantic timestamp'), default=False)
    unique_ids = zope.schema.Text(title=_('Unique IDs'))
