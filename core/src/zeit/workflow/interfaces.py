from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import MAX_PUBLISH_DATE
import zc.form.field
import zeit.cms.workflow.interfaces
import zeit.workflow.source
import zope.app.security.vocabulary
import zope.interface
import zope.interface.common.sequence
import zope.schema


# The not necessary singleton of a TriState
NotNecessary = zeit.workflow.source.NotNecessary

WORKFLOW_NS = 'http://namespaces.zeit.de/CMS/workflow'


class ITimeBasedPublishing(zeit.cms.workflow.interfaces.IPublishInfo):
    """Time based publishing."""

    release_period = zc.form.field.Combination(
        (zope.schema.Datetime(title=_("From"), required=False,
                              max=MAX_PUBLISH_DATE),
         zope.schema.Datetime(title=_("To"), required=False,
                              max=MAX_PUBLISH_DATE)),
        title=_('Publication period'),
        description=_('workflow-publication-period-description',
                      'Leave empty for no constraint.'),
        required=False)

    released_from = zope.interface.Attribute(
        "Easy access to release_period[0]")
    released_to = zope.interface.Attribute(
        "Easy access to release_period[1]")


class IContentWorkflow(ITimeBasedPublishing):
    """Zeit Workflow interface.

    Currently there is only a *very* simple and static property based workflow
    implemented.

    """

    edited = zope.schema.Choice(
        title=_('status-edited', default='Edited'),
        default=False,
        source=zeit.workflow.source.TriState())

    corrected = zope.schema.Choice(
        title=_('status-corrected', default='Corrected'),
        default=False,
        source=zeit.workflow.source.TriState())

    seo_optimized = zope.schema.Choice(
        title=_('status-seo-optimized', default='SEO optimized'),
        default=False,
        source=zeit.workflow.source.TriState())

    urgent = zope.schema.Bool(
        title=_('Urgent'),
        description=_('Select for newsflashs or on a weekend to publish '
                      'without setting corrected/refined/etc.'),
        default=False)


class IAssetWorkflow(ITimeBasedPublishing):
    """Workflow for assets."""


class IOldCMSStatus(zope.interface.Interface):
    """Support old status flag.

    The old status flag is either "OK" or not presesnt.

    """

    status = zope.schema.TextLine(
        title='Status like old CMS (OK, or not present)',
        required=False)


class IPublisherData(zope.interface.Interface):
    """
    Adapter to return json data for content for specific third party systems
    """

    def json():
        """Return info for content"""
