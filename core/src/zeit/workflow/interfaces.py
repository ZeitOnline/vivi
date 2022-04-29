from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import MAX_PUBLISH_DATE
import zc.form.field
import zeit.cms.syndication.interfaces
import zeit.cms.workflow.interfaces
import zeit.workflow.source
import zope.app.security.vocabulary
import zope.interface
import zope.interface.common.sequence
import zope.schema


# The not necessary singleton of a TriState
NotNecessary = zeit.workflow.source.NotNecessary

WORKFLOW_NS = 'http://namespaces.zeit.de/CMS/workflow'


class ScriptError(Exception):
    """Raised when the publish/retract script fails."""


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


class IPublicationDependencies(zope.interface.Interface):
    """Adapter to find the publication dependencies of an object."""

    def get_dependencies():
        """Return a sequence of all dependent objects.

    The sequence contains all objects which need to be published along with the
    adapted object. Dependent containers will be published recursively.
    """

    retract_dependencies = zope.interface.Attribute("""\
        If True, retract dependent objects along with the adapted object.
        Usually we cannot know whether an object is used by someone else and
        thus can't retract it, but in some cases this decision can be made.""")
